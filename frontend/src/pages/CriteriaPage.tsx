import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Button } from '../components/FormComponents'
import { useAppContext } from '../context/AppContext'
import api from '../services/api'
import { mockCriteria } from '../services/mockData'
import { ChevronDown, ChevronUp } from 'lucide-react'

const SAATY_SCALE = [
  { value: 1, label: 'Equal' },
  { value: 2, label: 'Slightly More' },
  { value: 3, label: 'Moderately More' },
  { value: 4, label: 'Noticeably More' },
  { value: 5, label: 'Strongly More' },
  { value: 6, label: 'More Strong' },
  { value: 7, label: 'Very Strongly More' },
  { value: 8, label: 'Extremely More' },
  { value: 9, label: 'Absolutely More' },
]

export default function CriteriaPage() {
  const navigate = useNavigate()
  const { currentScenario, setPairwiseMatrix } = useAppContext()
  const [criteria, setCriteria] = useState(mockCriteria)
  const [matrix, setMatrix] = useState<number[][]>([])
  const [loading, setLoading] = useState(false)
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set())

  useEffect(() => {
    const fetchCriteria = async () => {
      try {
        const data = await api.getCriteria()
        setCriteria(data)
      } catch (error) {
        console.error('Failed to fetch criteria:', error)
      }
    }
    fetchCriteria()

    // Initialize matrix with 1s (equal comparison)
    const initialMatrix = Array(mockCriteria.length)
      .fill(null)
      .map(() => Array(mockCriteria.length).fill(1))
    setMatrix(initialMatrix)
  }, [])

  const handleMatrixChange = (i: number, j: number, value: number) => {
    const newMatrix = matrix.map(row => [...row])
    newMatrix[i][j] = value
    // Mirror the value reciprocally
    newMatrix[j][i] = 1 / value
    setMatrix(newMatrix)
  }

  const toggleRow = (index: number) => {
    const newExpanded = new Set(expandedRows)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedRows(newExpanded)
  }

  const handleSubmit = async () => {
    if (!currentScenario) {
      alert('Please setup a scenario first')
      navigate('/setup')
      return
    }

    setLoading(true)
    try {
      await api.submitPairwiseComparison(currentScenario.id, matrix)
      setPairwiseMatrix(matrix)
      navigate('/results')
    } catch (error) {
      console.error('Error submitting pairwise comparison:', error)
      alert('Failed to submit criteria weights')
    } finally {
      setLoading(false)
    }
  }

  if (matrix.length === 0) {
    return <div className="p-8">Loading criteria...</div>
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
        Criteria Weighting (AHP Method)
      </h1>
      <p className="text-gray-600 dark:text-gray-400 mb-8">
        Rate each pair of criteria using the Saaty scale (1-9). The matrix is automatically reciprocal.
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <Card>
          <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Saaty Scale</h3>
          <div className="space-y-2 text-sm">
            {SAATY_SCALE.map((item) => (
              <div key={item.value} className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">{item.label}</span>
                <span className="font-semibold text-blue-600">{item.value}</span>
              </div>
            ))}
          </div>
        </Card>

        <Card className="lg:col-span-2">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Criteria Categories</h3>
          <div className="space-y-2 text-sm">
            {Array.from(new Set(criteria.map(c => c.category))).map((category) => (
              <div key={category} className="flex items-center">
                <span className="inline-block w-3 h-3 rounded-full bg-blue-600 mr-2"></span>
                <span className="text-gray-700 dark:text-gray-300">
                  {category} ({criteria.filter(c => c.category === category).length})
                </span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card className="overflow-x-auto mb-8">
        <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Pairwise Comparison Matrix</h3>
        <div className="space-y-3">
          {criteria.map((criterion, i) => (
            <div key={i}>
              <button
                onClick={() => toggleRow(i)}
                className="w-full flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600"
              >
                <span className="font-medium text-gray-900 dark:text-white">
                  {i + 1}. {criterion.name}
                </span>
                {expandedRows.has(i) ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
              </button>

              {expandedRows.has(i) && (
                <div className="mt-2 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                    {criteria.map((other, j) => {
                      if (i >= j) return null
                      return (
                        <div key={`${i}-${j}`}>
                          <label className="text-xs text-gray-600 dark:text-gray-400 block mb-1">
                            {other.name}
                          </label>
                          <select
                            value={matrix[i][j]}
                            onChange={(e) => handleMatrixChange(i, j, Number(e.target.value))}
                            className="w-full px-2 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-600 text-gray-900 dark:text-white"
                          >
                            {SAATY_SCALE.map((s) => (
                              <option key={s.value} value={s.value}>
                                {s.value}
                              </option>
                            ))}
                          </select>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>

      <div className="flex gap-4">
        <Button
          variant="secondary"
          onClick={() => navigate('/setup')}
        >
          Back to Setup
        </Button>
        <Button
          onClick={handleSubmit}
          loading={loading}
          size="lg"
        >
          Calculate Weights & Continue
        </Button>
      </div>

      <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/30 rounded-lg border border-blue-200 dark:border-blue-700">
        <p className="text-sm text-blue-800 dark:text-blue-200">
          💡 <strong>How to use:</strong> For each criterion pair, indicate which is more important and by how much. Use scale 1-9 where higher values mean the first criterion is much more important. The matrix automatically calculates reciprocal values.
        </p>
      </div>
    </div>
  )
}
