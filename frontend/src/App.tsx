import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AppProvider } from './context/AppContext'
import { Layout } from './components/Layout'
import SetupPage from './pages/SetupPage'
import CriteriaPage from './pages/CriteriaPage'
import ResultsPage from './pages/ResultsPage'
import SensitivityPage from './pages/SensitivityPage'
import ComparePage from './pages/ComparePage'

function App() {
  return (
    <AppProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/setup" element={<SetupPage />} />
            <Route path="/criteria" element={<CriteriaPage />} />
            <Route path="/results" element={<ResultsPage />} />
            <Route path="/sensitivity" element={<SensitivityPage />} />
            <Route path="/compare" element={<ComparePage />} />
            <Route path="/" element={<Navigate to="/setup" replace />} />
          </Routes>
        </Layout>
      </Router>
    </AppProvider>
  )
}

export default App
