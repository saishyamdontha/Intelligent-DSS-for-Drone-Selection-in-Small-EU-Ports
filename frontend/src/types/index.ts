export type MissionType = 'surveillance' | 'inspection' | 'environmental_monitoring' | 'maritime_safety'
export type EnvironmentType = 'coastal' | 'inland' | 'mixed'

export interface Scenario {
  id: string
  name: string
  budget_min: number
  budget_max: number
  mission_type: MissionType
  environment_type: EnvironmentType
  created_at: string
}

export interface Criterion {
  id: string
  name: string
  category: string
}

export interface DroneSpecs {
  [key: string]: number
}

export interface Drone {
  id: string
  name: string
  specs: DroneSpecs
  topsisScore: number
  rank: number
}

export interface EvaluationResult {
  scenario_id: string
  timestamp: string
  rankings: Drone[]
  top_3_criteria: Array<{ criterion: string; average_score: number }>
}

export interface AppContextType {
  currentScenario: Scenario | null
  setCurrentScenario: (scenario: Scenario | null) => void
  pairwiseMatrix: number[][] | null
  setPairwiseMatrix: (matrix: number[][]) => void
  isDarkMode: boolean
  setIsDarkMode: (dark: boolean) => void
}
