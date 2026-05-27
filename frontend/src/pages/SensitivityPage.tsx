import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Button } from '../components/FormComponents'
import { useAppContext } from '../context/AppContext'
import api from '../services/api'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer, Cell
} from 'recharts'

const STABILITY_COLORS: Record<string, string> = {
  HIGH:   '#00cc99',
  MEDIUM: '#f59e0b',
  LOW:    '#ff6b6b',
}

const STABILITY_ICONS: Record<string, string> = {
  HIGH:   '✓✓',
  MEDIUM: '~',
  LOW:    '✗',
}

export default function SensitivityPage() {
  const navigate = useNavigate()
  const { currentScenario } = useAppContext()
  const [sensitivityResults, setSensitivityResults] = useState<any>(null)
  const [rankings, setRankings] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const scenarioId = currentScenario?.id || `scenario-${Date.now()}`
        const params = currentScenario || {
          mission_type: 'surveillance',
          budget_max: 15000,
          environment_type: 'coastal'
        }
        const data = await api.evaluate(scenarioId, params)

        console.log('Full data:', JSON.stringify(data, null, 2))
        // Try multiple possible keys
        const sens = data?.sensitivity || data?.sensitivityResults || null
        console.log('All data keys:', Object.keys(data || {}))
        console.log('Sensitivity found:', sens)
        if (sens && sens.results && sens.results.length > 0) {
          setSensitivityResults(sens)
        } else {
          console.log('Sensitivity empty or missing results array')
          console.log('Raw sensitivity:', JSON.stringify(sens))
        }
        if (data?.rankings) {
          setRankings(data.rankings)
        }
      } catch (err: any) {
        setError('Failed to load sensitivity analysis. Make sure backend is running.')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [currentScenario])

  if (loading) {
    return (
      <div className="p-8 text-center">
        <div className="text-gray-600 dark:text-gray-400">
          Running Monte Carlo Sensitivity Analysis...
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="p-4 bg-red-50 dark:bg-red-900/30 rounded border border-red-200 text-red-700 dark:text-red-300">
          {error}
        </div>
        <Button className="mt-4" variant="secondary" onClick={() => navigate('/results')}>
          Back to Results
        </Button>
      </div>
    )
  }

  const results = sensitivityResults?.results || []
  const settings = sensitivityResults?.settings || {}

  // Chart data — top 3 frequency
  const top3ChartData = results.slice(0, 8).map((r: any) => ({
    name: r.name.split(' ').slice(0, 2).join(' '),
    top3_pct:    r.top3_frequency_pct,
    rank1_pct:   r.rank_1_frequency_pct,
    cc_mean:     parseFloat((r.cc_mean * 100).toFixed(1)),
    stability:   r.stability,
  }))

  // CC distribution chart
  const ccChartData = results.slice(0, 6).map((r: any) => ({
    name:    r.name.split(' ').slice(0, 2).join(' '),
    cc_mean: parseFloat(r.cc_mean.toFixed(4)),
    cc_min:  parseFloat(r.cc_min.toFixed(4)),
    cc_max:  parseFloat(r.cc_max.toFixed(4)),
    cc_std:  parseFloat(r.cc_std.toFixed(4)),
  }))

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
        Sensitivity Analysis
      </h1>
      <p className="text-gray-600 dark:text-gray-400 mb-2">
        Monte Carlo simulation — how stable are the TOPSIS rankings?
      </p>

      {/* Settings Summary */}
      {settings.n_simulations && (
        <div className="mb-8 p-4 bg-blue-50 dark:bg-blue-900/30 rounded border border-blue-200 dark:border-blue-700">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-blue-700 dark:text-blue-300">
                {settings.n_simulations}
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400">Simulations Run</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-blue-700 dark:text-blue-300">
                ±{(settings.perturbation_pct * 100).toFixed(0)}%
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400">Weight Perturbation</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-blue-700 dark:text-blue-300">
                {settings.n_criteria}
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400">Criteria</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-blue-700 dark:text-blue-300">
                {settings.n_drones}
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400">Eligible Drones</p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">

        {/* Top 3 Frequency Chart */}
        <Card>
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
            Top-3 Frequency (% of simulations)
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={top3ChartData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 100]} unit="%" />
              <YAxis type="category" dataKey="name" width={100} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(value) => `${value}%`} />
              <Legend />
              <Bar dataKey="rank1_pct" name="Rank #1 %" fill="#0066cc" />
              <Bar dataKey="top3_pct"  name="Top 3 %" fill="#00cc99" />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        {/* CC Mean Chart */}
        <Card>
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
            Closeness Coefficient — Mean across simulations
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={ccChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <YAxis domain={[0, 1]} />
              <Tooltip />
              <Bar dataKey="cc_mean" name="Mean CC" radius={[4, 4, 0, 0]}>
                {ccChartData.map((_: any, index: number) => (
                  <Cell
                    key={index}
                    fill={['#0066cc','#00cc99','#f59e0b','#ff6b6b','#8b5cf6','#ec4899'][index % 6]}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Stability Table */}
      <Card className="mb-8">
        <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
          Ranking Stability Report
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700">
                <th className="px-4 py-3 text-left">Rank</th>
                <th className="px-4 py-3 text-left">Drone</th>
                <th className="px-4 py-3 text-right">Base CC</th>
                <th className="px-4 py-3 text-right">Mean CC</th>
                <th className="px-4 py-3 text-right">Std Dev</th>
                <th className="px-4 py-3 text-right">Rank #1 %</th>
                <th className="px-4 py-3 text-right">Top 3 %</th>
                <th className="px-4 py-3 text-center">Stability</th>
              </tr>
            </thead>
            <tbody>
              {results.map((r: any) => (
                <tr key={r.id} className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-4 py-3 font-bold text-gray-900 dark:text-white">
                    #{r.base_rank}
                  </td>
                  <td className="px-4 py-3 text-gray-900 dark:text-white">{r.name}</td>
                  <td className="px-4 py-3 text-right text-gray-600 dark:text-gray-400">
                    {r.base_cc.toFixed(4)}
                  </td>
                  <td className="px-4 py-3 text-right text-gray-600 dark:text-gray-400">
                    {r.cc_mean.toFixed(4)}
                  </td>
                  <td className="px-4 py-3 text-right text-gray-600 dark:text-gray-400">
                    ±{r.cc_std.toFixed(4)}
                  </td>
                  <td className="px-4 py-3 text-right text-gray-600 dark:text-gray-400">
                    {r.rank_1_frequency_pct}%
                  </td>
                  <td className="px-4 py-3 text-right text-gray-600 dark:text-gray-400">
                    {r.top3_frequency_pct}%
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span
                      className="px-2 py-1 rounded text-xs font-bold text-white"
                      style={{ backgroundColor: STABILITY_COLORS[r.stability] || '#gray' }}
                    >
                      {STABILITY_ICONS[r.stability]} {r.stability}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-4 grid grid-cols-3 gap-4 text-center text-sm">
          <div className="p-2 rounded" style={{ backgroundColor: '#00cc9920' }}>
            <span className="font-bold text-green-700">HIGH</span>
            <p className="text-xs text-gray-600">Top-3 ≥ 70% of simulations</p>
          </div>
          <div className="p-2 rounded" style={{ backgroundColor: '#f59e0b20' }}>
            <span className="font-bold text-yellow-700">MEDIUM</span>
            <p className="text-xs text-gray-600">Top-3 40–70% of simulations</p>
          </div>
          <div className="p-2 rounded" style={{ backgroundColor: '#ff6b6b20' }}>
            <span className="font-bold text-red-700">LOW</span>
            <p className="text-xs text-gray-600">Top-3 &lt; 40% of simulations</p>
          </div>
        </div>
      </Card>

      <div className="flex gap-4">
        <Button variant="secondary" onClick={() => navigate('/results')}>
          Back to Results
        </Button>
        <Button onClick={() => navigate('/compare')} variant="success">
          Compare Drones
        </Button>
      </div>
    </div>
  )
}
