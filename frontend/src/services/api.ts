import axios, { AxiosInstance } from 'axios'
import { mockCriteria } from './mockData'

const API_BASE_URL = 'http://localhost:8001'

class APIService {
  private client: AxiosInstance
  constructor() {
    this.client = axios.create({ baseURL: API_BASE_URL, timeout: 30000 })
  }

  async getScenarios() { return [] }

  async createScenario(scenario: any) {
    sessionStorage.setItem(`scenario_${scenario.id}`, JSON.stringify(scenario))
    return scenario
  }

  async getDrones() {
    try {
      const r = await this.client.get('/drones')
      return r.data.drones.map((d: any) => ({
        id: d.id, name: d.name, manufacturer: d.manufacturer,
        specs: {
          flight_time:            d.flight_time_min,
          flight_range:           d.flight_range_km,
          night_vision:           d.night_vision === "advanced" ? 2 : d.night_vision === "basic" ? 1 : 0,
          payload_capacity:       d.payload_capacity_kg,
          camera_quality:         d.camera_quality_mp,
          autonomy_level:         d.autonomy_level === "fully-autonomous" ? 3 : d.autonomy_level === "semi-autonomous" ? 2 : 1,
          weather_resistance:     d.weather_resistance_ip === "IP55" ? 3 : d.weather_resistance_ip === "IP53" ? 2 : 1,
          realtime_transmission:  d.real_time_transmission ? 1 : 0,
          obstacle_avoidance:     d.obstacle_avoidance === "omnidirectional" ? 2 : d.obstacle_avoidance === "basic" ? 1 : 0,
          gps_accuracy:           d.gps_accuracy_m,
          battery_swappable:      d.battery_swappable ? 1 : 0,
          maintenance_req:        d.maintenance_score,
          initial_cost:           d.initial_cost_eur,
          operational_cost:       d.operational_cost_eur_hr,
          regulatory_compliance:  d.regulatory_compliance === "Certified" ? 4 : d.regulatory_compliance === "Specific" ? 3 : 2,
          integration_capability: d.integration_capability === "high" ? 3 : d.integration_capability === "medium" ? 2 : 1,
          sensor_compatibility:   d.sensor_compatibility,
          data_storage:           d.data_storage_gb,
          launch_recovery_method: d.launch_recovery_method === "automated-pad" ? 3 : d.launch_recovery_method === "VTOL" ? 2 : 1,
          redundancy_failsafe:    d.redundancy_failsafe === "full-redundancy" ? 3 : d.redundancy_failsafe === "advanced" ? 2 : d.redundancy_failsafe === "basic" ? 1 : 0,
        },
        topsisScore: 0, rank: 0,
      }))
    } catch { return [] }
  }

  async getCriteria() { return mockCriteria }

  async submitPairwiseComparison(scenarioId: string, matrix: number[][]) {
    sessionStorage.setItem('ahp_matrix', JSON.stringify(matrix))
    return { status: 'ok' }
  }

  async evaluate(scenarioId: string, params: any) {
    const mission = (params.mission_type || '').toLowerCase()
    const budget  = params.budget_max || 999999

    let sid = 'S01'
    if (mission.includes('environmental'))                                   sid = 'S04'
    else if (mission.includes('emergency') || mission.includes('maritime')) sid = 'S05'
    else if (mission.includes('inspection'))                                sid = 'S03'
    else if (budget > 20000)                                                sid = 'S02'
    else                                                                    sid = 'S01'

    console.log('>>> Calling backend scenario:', sid, 'budget:', budget, 'mission:', mission)

    const countryCode = params.country_code || 'SE'
    const response = await this.client.post(
      `/evaluate/country?scenario_id=${sid}&country_code=${countryCode}&n_sensitivity_simulations=100`
    )
    const data = response.data
    const drones = await this.getDrones()

    const rankings = data.ranking.map((r: any) => {
      const drone = drones.find((d: any) => d.id === r.id)
      return {
        id: r.id, name: r.name, manufacturer: r.manufacturer,
        topsisScore: r.closeness_coefficient, rank: r.rank,
        specs: drone ? drone.specs : {},
      }
    })

    return {
      scenario_id: scenarioId,
      timestamp: new Date().toISOString(),
      rankings,
      sensitivity: data.sensitivity,
      recommendation: data.recommendation,
      top_3_criteria: (data.ahp?.top5_criteria_by_weight || [])
        .slice(0, 3)
        .map(([criterion, weight]: [string, number]) => ({ criterion, average_score: weight * 10 })),
    }
  }

  async getResults(scenarioId: string) {
    const stored = sessionStorage.getItem(`scenario_${scenarioId}`)
    const scenario = stored ? JSON.parse(stored) : {}
    return this.evaluate(scenarioId, scenario)
  }

  async sensitivityAnalysis(scenarioId: string, weights: Record<string, number>) {
    return this.getResults(scenarioId)
  }

  async getSessions() { return [] }

  async explainResults(scenarioId: string, params: any) {
    try {
      const mission = (params.mission_type || '').toLowerCase()
      const budget  = params.budget_max || 999999
      let sid = 'S01'
      if (mission.includes('environmental'))                                   sid = 'S04'
      else if (mission.includes('emergency') || mission.includes('maritime')) sid = 'S05'
      else if (mission.includes('inspection'))                                 sid = 'S03'
      else if (budget > 20000)                                                 sid = 'S02'
      else                                                                     sid = 'S01'
      const response = await this.client.post('/explain', {
        scenario_id: sid,
        n_sensitivity_simulations: 50,
      })
      return response.data.ai_explanation
    } catch (error: any) {
      console.error('Explain error:', error?.response?.data || error.message)
      return null
    }
  }

  async chat(question: string, evaluationResult: any, chatHistory: any[]) {
    try {
      const response = await this.client.post('/chat', {
        question,
        evaluation_result: evaluationResult,
        chat_history: chatHistory,
      })
      return response.data.answer
    } catch (error: any) {
      return 'Sorry, I could not answer that question.'
    }
  }
}

export default new APIService()
