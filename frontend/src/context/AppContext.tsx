import { createContext, useContext, useState, ReactNode, useEffect } from 'react'
import { AppContextType, Scenario } from '../types'

const AppContext = createContext<AppContextType | undefined>(undefined)

export function AppProvider({ children }: { children: ReactNode }) {
  const [currentScenario, setCurrentScenario] = useState<Scenario | null>(null)
  const [pairwiseMatrix, setPairwiseMatrix] = useState<number[][] | null>(null)
  const [isDarkMode, setIsDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('theme') === 'dark' ||
        (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)
    }
    return false
  })

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }, [isDarkMode])

  const value: AppContextType = {
    currentScenario,
    setCurrentScenario,
    pairwiseMatrix,
    setPairwiseMatrix,
    isDarkMode,
    setIsDarkMode,
  }

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

export function useAppContext() {
  const context = useContext(AppContext)
  if (context === undefined) {
    throw new Error('useAppContext must be used within AppProvider')
  }
  return context
}
