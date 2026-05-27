import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Button, FormField, Slider } from '../components/FormComponents'
import { useAppContext } from '../context/AppContext'
import { MissionType, EnvironmentType, Scenario } from '../types'
import api from '../services/api'

export default function SetupPage() {
  const navigate = useNavigate()
  const { setCurrentScenario } = useAppContext()
  const [loading, setLoading] = useState(false)
  
  const [countryCode, setCountryCode] = useState('SE')
  const [formData, setFormData] = useState({
    name: '',
    budget_min: 10000,
    budget_max: 50000,
    mission_type: 'surveillance' as MissionType,
    environment_type: 'coastal' as EnvironmentType,
  })

  const missionTypes: { value: MissionType; label: string }[] = [
    { value: 'surveillance', label: 'Surveillance' },
    { value: 'inspection', label: 'Inspection' },
    { value: 'environmental_monitoring', label: 'Environmental Monitoring' },
    { value: 'maritime_safety', label: 'Maritime Safety' },
  ]

  const environmentTypes: { value: EnvironmentType; label: string }[] = [
    { value: 'coastal', label: 'Coastal' },
    { value: 'inland', label: 'Inland' },
    { value: 'mixed', label: 'Mixed' },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const scenario: Scenario = {
        id: `scenario-${Date.now()}`,
        ...formData,
        country_code: countryCode,
        created_at: new Date().toISOString(),
      }

      // Try to create via API, fallback to mock
      sessionStorage.setItem(`scenario_${scenario.id}`, JSON.stringify(scenario))

      setCurrentScenario(scenario)
      navigate('/criteria')
    } catch (error) {
      console.error('Error creating scenario:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Port Scenario Setup</h1>
      <p className="text-gray-600 dark:text-gray-400 mb-8">
        Configure your drone selection parameters
      </p>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-6">
          <FormField label="Scenario Name" required>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., Port A Surveillance Mission"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              required
            />
          </FormField>

          <FormField label="Budget Range">
            <div className="space-y-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <Slider
                label="Minimum Budget ($)"
                value={formData.budget_min}
                onChange={(value) => setFormData({ ...formData, budget_min: value })}
                min={1000}
                max={formData.budget_max - 1000}
                step={1000}
              />
              <Slider
                label="Maximum Budget ($)"
                value={formData.budget_max}
                onChange={(value) => setFormData({ ...formData, budget_max: value })}
                min={formData.budget_min + 1000}
                max={500000}
                step={1000}
              />
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Selected Range: ${formData.budget_min.toLocaleString()} - ${formData.budget_max.toLocaleString()}
              </p>
            </div>
          </FormField>

          <FormField label="Mission Type" required>
            <select
              value={formData.mission_type}
              onChange={(e) => setFormData({ ...formData, mission_type: e.target.value as MissionType })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              {missionTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </FormField>

          <FormField label="Environment Type" required>
            <select
              value={formData.environment_type}
              onChange={(e) => setFormData({ ...formData, environment_type: e.target.value as EnvironmentType })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              {environmentTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </FormField>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Country (EU Regulations)</label>
            <select
              value={countryCode}
              onChange={(e) => setCountryCode(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="SE">🇸🇪 Sweden</option>
              <option value="DE">🇩🇪 Germany</option>
              <option value="FR">🇫🇷 France</option>
              <option value="NL">🇳🇱 Netherlands</option>
              <option value="ES">🇪🇸 Spain</option>
              <option value="IT">🇮🇹 Italy</option>
              <option value="PL">🇵🇱 Poland</option>
              <option value="DK">🇩🇰 Denmark</option>
              <option value="FI">🇫🇮 Finland</option>
              <option value="NO">🇳🇴 Norway</option>
              <option value="BE">🇧🇪 Belgium</option>
              <option value="PT">🇵🇹 Portugal</option>
              <option value="GR">🇬🇷 Greece</option>
              <option value="HR">🇭🇷 Croatia</option>
            </select>
          </div>

          <div className="flex gap-4 pt-6">
            <Button type="submit" loading={loading} size="lg">
              Continue to Criteria Weighting
            </Button>
          </div>
        </form>
      </Card>

      <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/30 rounded-lg border border-blue-200 dark:border-blue-700">
        <p className="text-sm text-blue-800 dark:text-blue-200">
          💡 <strong>Tip:</strong> The scenario parameters define the context for drone evaluation. Adjust the budget range and mission type to match your specific requirements.
        </p>
      </div>
    </div>
  )
}
