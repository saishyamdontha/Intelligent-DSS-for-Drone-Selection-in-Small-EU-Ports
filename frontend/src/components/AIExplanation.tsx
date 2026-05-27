import { useState, useEffect } from 'react'
import api from '../services/api'

interface Props {
  currentScenario: any
  evaluationResult: any
}

export default function AIExplanation({ currentScenario, evaluationResult }: Props) {
  const [explanation, setExplanation] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [chatOpen, setChatOpen] = useState(false)
  const [question, setQuestion] = useState('')
  const [chatHistory, setChatHistory] = useState<any[]>([])
  const [chatLoading, setChatLoading] = useState(false)

  useEffect(() => {
    if (currentScenario && evaluationResult?.rankings?.length > 0) {
      fetchExplanation()
    }
  }, [currentScenario])

  const fetchExplanation = async () => {
    setLoading(true)
    try {
      const result = await api.explainResults(
        currentScenario?.id || 'scenario',
        currentScenario || {}
      )
      setExplanation(result)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleChat = async () => {
    if (!question.trim()) return
    setChatLoading(true)
    const userMsg = { role: 'user', content: question }
    setChatHistory(prev => [...prev, userMsg])
    setQuestion('')
    try {
      const answer = await api.chat(question, evaluationResult, chatHistory)
      setChatHistory(prev => [...prev, { role: 'assistant', content: answer }])
    } catch (err) {
      console.error(err)
    } finally {
      setChatLoading(false)
    }
  }

  return (
    <div className="mt-6">
      <div className="p-6 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-700">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-2xl">🤖</span>
          <h3 className="font-bold text-lg text-blue-900 dark:text-blue-100">AI Decision Explanation</h3>
          <span className="text-xs px-2 py-1 bg-blue-600 text-white rounded">Powered by Groq</span>
        </div>
        {loading ? (
          <div className="text-blue-700 dark:text-blue-300 animate-pulse">Generating AI explanation...</div>
        ) : explanation ? (
          <div className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap leading-relaxed">{explanation}</div>
        ) : (
          <button onClick={fetchExplanation} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            Generate AI Explanation
          </button>
        )}
      </div>

      <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <button onClick={() => setChatOpen(!chatOpen)} className="flex items-center gap-2 font-semibold text-gray-900 dark:text-white">
          <span>💬</span> Ask a follow-up question
          <span className="text-xs text-gray-500">{chatOpen ? '▲' : '▼'}</span>
        </button>

        {chatOpen && (
          <div className="mt-4">
            <div className="space-y-3 mb-4 max-h-60 overflow-y-auto">
              {chatHistory.map((msg, i) => (
                <div key={i} className={`p-3 rounded-lg text-sm ${msg.role === 'user' ? 'bg-blue-100 dark:bg-blue-900 ml-8' : 'bg-white dark:bg-gray-700 mr-8'}`}>
                  <span className="font-bold">{msg.role === 'user' ? '👤 You' : '🤖 AI'}:</span>{' '}{msg.content}
                </div>
              ))}
              {chatLoading && (
                <div className="p-3 bg-white dark:bg-gray-700 rounded-lg text-sm text-gray-500 animate-pulse mr-8">🤖 Thinking...</div>
              )}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleChat()}
                placeholder="e.g. Why was DJI Matrice eliminated?"
                className="flex-1 px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
              <button onClick={handleChat} disabled={chatLoading || !question.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 text-sm">
                Ask
              </button>
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {['Why was the top drone selected?', 'Which drones were eliminated and why?', 'Is this recommendation stable?', 'What are the regulatory requirements?'].map((q) => (
                <button key={q} onClick={() => setQuestion(q)}
                  className="text-xs px-2 py-1 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300">
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
