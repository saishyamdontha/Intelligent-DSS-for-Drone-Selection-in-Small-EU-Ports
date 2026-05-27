import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Button } from '../components/FormComponents'
import api from '../services/api'
// mockData not needed — using real backend
import { Download, Plus, X } from 'lucide-react'

export default function ComparePage() {
  const navigate = useNavigate()
  const [drones, setDrones] = useState<any[]>([])
  const [selectedDrones, setSelectedDrones] = useState<any[]>([])
  const [sortBy, setSortBy] = useState<string>('flight_time')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const fetchDrones = async () => {
      try {
        const data = await api.getDrones()
        setDrones(data)
        if (data.length >= 2) {
          setSelectedDrones([data[0], data[1]])
        }
      } catch (error) {
        console.error('Failed to fetch drones:', error)
      }
    }
    fetchDrones()
  }, [])

  const handleAddDrone = (drone: typeof mockDrones[0]) => {
    if (!selectedDrones.find((d) => d.id === drone.id)) {
      setSelectedDrones([...selectedDrones, drone])
    }
  }

  const handleRemoveDrone = (droneId: string) => {
    setSelectedDrones(selectedDrones.filter((d) => d.id !== droneId))
  }

  const handleExportPDF = () => {
    alert('PDF export would be implemented here. In production, use a library like jsPDF or html2pdf.')
  }

  const criteria = [
    'flight_time',
    'flight_range',
    'night_vision',
    'payload_capacity',
    'camera_quality',
    'autonomy_level',
    'weather_resistance',
    'realtime_transmission',
    'obstacle_avoidance',
    'gps_accuracy',
    'battery_swappable',
    'maintenance_req',
    'initial_cost',
    'operational_cost',
    'regulatory_compliance',
    'integration_capability',
    'sensor_compatibility',
    'data_storage',
  ]

  const getCriterionLabel = (key: string) => {
    const labels: Record<string, string> = {
      flight_time: 'Flight Time (min)',
      flight_range: 'Flight Range (km)',
      night_vision: 'Night Vision (0-10)',
      payload_capacity: 'Payload Capacity (kg)',
      camera_quality: 'Camera Quality (MP)',
      autonomy_level: 'Autonomy Level (0-10)',
      weather_resistance: 'Weather Resistance (Beaufort)',
      realtime_transmission: 'Real-time Transmission (0-10)',
      obstacle_avoidance: 'Obstacle Avoidance (0-10)',
      gps_accuracy: 'GPS Accuracy (cm)',
      battery_swappable: 'Battery Swappable (0-10)',
      maintenance_req: 'Maintenance Required (hours/year)',
      initial_cost: 'Initial Cost ($)',
      operational_cost: 'Operational Cost ($/hour)',
      regulatory_compliance: 'Regulatory Compliance (%)',
      integration_capability: 'Integration Capability (0-10)',
      sensor_compatibility: 'Sensor Compatibility (0-10)',
      data_storage: 'Data Storage (GB)',
    }
    return labels[key] || key
  }

  const getColorClass = (value: number, criterion: string, max: number) => {
    const percentage = value / max
    // Higher is better for most criteria
    const betterIfHigher = ![
      'maintenance_req',
      'initial_cost',
      'operational_cost',
      'gps_accuracy',
    ].includes(criterion)

    if (betterIfHigher) {
      if (percentage >= 0.8) return 'bg-green-100 dark:bg-green-900'
      if (percentage >= 0.6) return 'bg-yellow-100 dark:bg-yellow-900'
      return 'bg-red-100 dark:bg-red-900'
    } else {
      if (percentage <= 0.2) return 'bg-green-100 dark:bg-green-900'
      if (percentage <= 0.4) return 'bg-yellow-100 dark:bg-yellow-900'
      return 'bg-red-100 dark:bg-red-900'
    }
  }

  const getMaxValue = (criterion: string) => {
    const values = selectedDrones.map((d) => (d.specs[criterion] as number) || 0)
    return Math.max(...values, 1)
  }

  if (loading) {
    return <div className="p-8 text-center">Loading drones...</div>
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
        Drone Comparison
      </h1>
      <p className="text-gray-600 dark:text-gray-400 mb-8">
        Compare specs side-by-side with color-coded performance indicators
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
        {/* Drone Selection Panel */}
        <Card className="lg:col-span-1 h-fit">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Available Drones</h3>
          <div className="space-y-2 mb-6 max-h-96 overflow-y-auto">
            {drones.map((drone) => {
              const isSelected = selectedDrones.find((d) => d.id === drone.id)
              return (
                <button
                  key={drone.id}
                  onClick={() => handleAddDrone(drone)}
                  className={`w-full text-left px-3 py-2 rounded transition-colors ${
                    isSelected
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  <p className="font-medium text-sm">{drone.name}</p>
                  <p className="text-xs text-opacity-80">Score: {drone.topsisScore.toFixed(3)}</p>
                </button>
              )
            })}
          </div>

          <Button
            onClick={handleExportPDF}
            variant="success"
            size="sm"
            className="w-full flex items-center justify-center gap-2"
          >
            <Download size={16} />
            Export PDF
          </Button>
        </Card>

        {/* Comparison Table */}
        <div className="lg:col-span-3">
          <Card>
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-semibold text-gray-900 dark:text-white">
                Selected Drones ({selectedDrones.length})
              </h3>
              {selectedDrones.length < drones.length && (
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  <Plus size={14} className="inline mr-1" />
                  Click drones on the left to add
                </p>
              )}
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700">
                    <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300 font-semibold">
                      Spec
                    </th>
                    {selectedDrones.map((drone) => (
                      <th key={drone.id} className="px-4 py-3 text-center text-gray-700 dark:text-gray-300 font-semibold">
                        <div className="flex items-center justify-between">
                          <span>{drone.name.split(' ')[0]}</span>
                          <button
                            onClick={() => handleRemoveDrone(drone.id)}
                            className="text-red-600 hover:text-red-800 ml-2"
                          >
                            <X size={16} />
                          </button>
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400 font-normal">
                          {drone.topsisScore.toFixed(3)}
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {criteria.map((criterion) => {
                    const maxValue = getMaxValue(criterion)
                    return (
                      <tr
                        key={criterion}
                        className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700"
                      >
                        <td className="px-4 py-3 text-gray-900 dark:text-white font-medium">
                          {getCriterionLabel(criterion)}
                        </td>
                        {selectedDrones.map((drone) => {
                          const value = drone.specs[criterion] as number || 0
                          const color = getColorClass(value, criterion, maxValue)
                          return (
                            <td
                              key={`${drone.id}-${criterion}`}
                              className={`px-4 py-3 text-center font-semibold rounded ${color}`}
                            >
                              {typeof value === 'number' && value % 1 !== 0
                                ? value.toFixed(2)
                                : value}
                            </td>
                          )
                        })}
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="lg:col-span-2 p-3 bg-green-50 dark:bg-green-900/20">
          <p className="text-sm text-green-800 dark:text-green-300">
            <span className="inline-block w-3 h-3 bg-green-100 dark:bg-green-900 rounded mr-2"></span>
            <strong>Green:</strong> Best value for the criterion
          </p>
        </Card>
        <Card className="p-3 bg-red-50 dark:bg-red-900/20">
          <p className="text-sm text-red-800 dark:text-red-300">
            <span className="inline-block w-3 h-3 bg-red-100 dark:bg-red-900 rounded mr-2"></span>
            <strong>Red:</strong> Worst value for the criterion
          </p>
        </Card>
      </div>

      <div className="flex gap-4 mt-8">
        <Button variant="secondary" onClick={() => navigate('/sensitivity')}>
          Back to Sensitivity
        </Button>
        <Button onClick={() => navigate('/results')} variant="secondary">
          Back to Results
        </Button>
      </div>
    </div>
  )
}
