import { ReactNode } from 'react'
import { useLocation, Link } from 'react-router-dom'
import { Zap, Settings, BarChart3, Activity, TrendingUp, Moon, Sun } from 'lucide-react'
import { useAppContext } from '../context/AppContext'

const navItems = [
  { path: '/setup', icon: Settings, label: 'Setup', step: 1 },
  { path: '/criteria', icon: Activity, label: 'Criteria', step: 2 },
  { path: '/results', icon: BarChart3, label: 'Results', step: 3 },
  { path: '/sensitivity', icon: TrendingUp, label: 'Sensitivity', step: 4 },
  { path: '/compare', icon: Zap, label: 'Compare', step: 5 },
]

export function Sidebar() {
  const location = useLocation()
  const { isDarkMode, setIsDarkMode } = useAppContext()

  return (
    <aside className="w-64 bg-gray-900 text-white min-h-screen flex flex-col shadow-lg">
      <div className="p-6 border-b border-gray-700">
        <div className="flex items-center gap-2 mb-2">
          <Zap size={32} className="text-blue-400" />
          <div>
            <h1 className="text-xl font-bold">Drone DSS</h1>
            <p className="text-xs text-gray-400">Selection System</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-4 py-6 space-y-2">
        {navItems.map(({ path, icon: Icon, label }) => (
          <Link
            key={path}
            to={path}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
              location.pathname === path
                ? 'bg-blue-600 text-white'
                : 'text-gray-300 hover:bg-gray-800'
            }`}
          >
            <Icon size={20} />
            <span className="font-medium">{label}</span>
          </Link>
        ))}
      </nav>

      <div className="p-4 border-t border-gray-700">
        <button
          onClick={() => setIsDarkMode(!isDarkMode)}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-gray-800 hover:bg-gray-700"
        >
          {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
          <span className="text-sm">{isDarkMode ? 'Light' : 'Dark'}</span>
        </button>
      </div>
    </aside>
  )
}

export function ProgressStepper() {
  const location = useLocation()
  const steps = [
    { label: 'Setup', path: '/setup' },
    { label: 'Criteria', path: '/criteria' },
    { label: 'Results', path: '/results' },
    { label: 'Sensitivity', path: '/sensitivity' },
    { label: 'Compare', path: '/compare' },
  ]

  const currentStep = steps.findIndex(s => s.path === location.pathname)

  return (
    <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between max-w-4xl">
        {steps.map((step, index) => (
          <div key={step.path} className="flex items-center flex-1">
            <Link
              to={step.path}
              className={`flex items-center justify-center w-10 h-10 rounded-full font-bold transition-all ${
                index <= currentStep
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
              }`}
            >
              {index + 1}
            </Link>
            <span className={`ml-2 text-sm font-medium ${
              index <= currentStep
                ? 'text-blue-600 dark:text-blue-400'
                : 'text-gray-500 dark:text-gray-400'
            }`}>
              {step.label}
            </span>
            {index < steps.length - 1 && (
              <div className={`flex-1 h-1 mx-4 rounded ${
                index < currentStep
                  ? 'bg-blue-600'
                  : 'bg-gray-200 dark:bg-gray-700'
              }`} />
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <ProgressStepper />
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
