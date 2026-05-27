import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Button } from '../components/FormComponents'
import { useAppContext } from '../context/AppContext'
import api from '../services/api'
import AIExplanation from '../components/AIExplanation'
import { mockResults, mockDrones } from '../services/mockData'
import { Drone, ChevronDown, ChevronUp } from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
} from 'recharts'

export default function ResultsPage() {
  const navigate = useNavigate()
  const { currentScenario } = useAppContext()
  const [results, setResults] = useState<any>({ rankings: [], top_3_criteria: [] })
  const [expandedDrone, setExpandedDrone] = useState<string | null>(null)
  const [sortKey, setSortKey] = useState<'rank' | 'score' | 'name'>('rank')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchResults = async () => {
      if (!currentScenario) {
        setLoading(false)
        return
      }

      try {
        const data = await api.getResults(currentScenario.id)
        setResults(data)
      } catch (error) {
        console.error('Failed to fetch results:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchResults()
  }, [currentScenario])

  const sortedRankings = [...results.rankings].sort((a, b) => {
    switch (sortKey) {
      case 'score':
        return b.topsisScore - a.topsisScore
      case 'name':
        return a.name.localeCompare(b.name)
      case 'rank':
      default:
        return a.rank - b.rank
    }
  })

  const top5Data = sortedRankings.slice(0, 5).map((drone) => ({
    name: drone.name.replace(' ', '\n'),
    score: parseFloat(drone.topsisScore.toFixed(2)),
  }))

  const top3Drones = sortedRankings.slice(0, 3)
  const criteriaForRadar = [
    { key: 'flight_time', label: 'Flight Time' },
    { key: 'payload_capacity', label: 'Payload' },
    { key: 'autonomy_level', label: 'Autonomy' },
    { key: 'weather_resistance', label: 'Weather' },
    { key: 'gps_accuracy', label: 'GPS', scale: 10 },
  ]

  const radarData = criteriaForRadar.map((criterion) => ({
    criterion: criterion.label,
    ...Object.fromEntries(
      top3Drones.map((drone) => [
        drone.name.split(' ')[0],
        (drone.specs[criterion.key] as number) / (criterion.scale || 1) * 10,
      ])
    ),
  }))

  if (loading) {
    return <div className="p-8 text-center">Loading results...</div>
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
        Drone Rankings & Analysis
      </h1>
      <p className="text-gray-600 dark:text-gray-400 mb-8">
        TOPSIS-based evaluation results for your scenario
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Top 5 Bar Chart */}
        <Card>
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Top 5 Drones by Score</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={top5Data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 1]} />
              <Tooltip />
              <Bar dataKey="score" fill="#0066cc" />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        {/* Top 3 Radar Chart */}
        <Card>
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Top 3 Drones Radar</h3>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="criterion" />
              <PolarRadiusAxis />
              {top3Drones.map((drone, index) => (
                <Radar
                  key={drone.id}
                  name={drone.name.split(' ')[0]}
                  dataKey={drone.name.split(' ')[0]}
                  stroke={['#0066cc', '#00cc99', '#ff6b6b'][index]}
                  fill={['#0066cc', '#00cc99', '#ff6b6b'][index]}
                  fillOpacity={0.25}
                />
              ))}
              <Legend />
            </RadarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Rankings Table */}
      <Card className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold text-gray-900 dark:text-white">Rankings</h3>
          <select
            value={sortKey}
            onChange={(e) => setSortKey(e.target.value as any)}
            className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
          >
            <option value="rank">Sort by Rank</option>
            <option value="score">Sort by Score</option>
            <option value="name">Sort by Name</option>
          </select>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700">
                <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300 font-semibold">Rank</th>
                <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300 font-semibold">Drone Name</th>
                <th className="px-4 py-3 text-right text-gray-700 dark:text-gray-300 font-semibold">TOPSIS Score</th>
                <th className="px-4 py-3 text-right text-gray-700 dark:text-gray-300 font-semibold">Flight Time</th>
                <th className="px-4 py-3 text-right text-gray-700 dark:text-gray-300 font-semibold">Payload</th>
                <th className="px-4 py-3 text-center text-gray-700 dark:text-gray-300 font-semibold">Action</th>
              </tr>
            </thead>
            <tbody>
              {sortedRankings.map((drone, index) => (
                <tbody key={drone.id}>
                  <tr className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-4 py-3 text-gray-900 dark:text-white font-semibold">{index + 1}</td>
                    <td className="px-4 py-3 text-gray-900 dark:text-white">{drone.name}</td>
                    <td className="px-4 py-3 text-right">
                      <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded font-semibold">
                        {drone.topsisScore.toFixed(3)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right text-gray-600 dark:text-gray-400">
                      {drone.specs.flight_time} min
                    </td>
                    <td className="px-4 py-3 text-right text-gray-600 dark:text-gray-400">
                      {drone.specs.payload_capacity} kg
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => setExpandedDrone(expandedDrone === drone.id ? null : drone.id)}
                        className="text-blue-600 dark:text-blue-400 hover:text-blue-800"
                      >
                        {expandedDrone === drone.id ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                      </button>
                    </td>
                  </tr>
                  {expandedDrone === drone.id && (
                    <tr className="bg-gray-50 dark:bg-gray-700">
                      <td colSpan={6} className="px-4 py-4">
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                          {Object.entries(drone.specs).map(([key, value]) => (
                            <div key={key} className="p-2 bg-white dark:bg-gray-600 rounded">
                              <p className="text-xs text-gray-600 dark:text-gray-400 uppercase">{key.replace(/_/g, ' ')}</p>
                              <p className="font-semibold text-gray-900 dark:text-white">{value}</p>
                            </div>
                          ))}
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <AIExplanation currentScenario={currentScenario} evaluationResult={results} />

      <div className="flex gap-4">
        <Button variant="secondary" onClick={() => navigate('/criteria')}>
          Back to Criteria
        </Button>
        <Button onClick={() => navigate('/sensitivity')}>
          Sensitivity Analysis
        </Button>
        <Button onClick={() => navigate('/compare')} variant="success">
          Compare Drones
        </Button>
      </div>
    </div>
  )
}
