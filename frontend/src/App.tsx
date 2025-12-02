import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Sidebar from './components/layout/Sidebar'
import Header from './components/layout/Header'
import UploadPage from './pages/UploadPage'
import AnalysisDetailPage from './pages/AnalysisDetailPage'
import ComparisonPage from './pages/ComparisonPage'
import DashboardPage from './pages/DashboardPage'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <Sidebar />
        <div className="app-content">
          <Header />
          <main className="app-main">
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/analyses" element={<DashboardPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/analysis/:analysisId" element={<AnalysisDetailPage />} />
              <Route path="/comparison/:analysisId/:transformationId?" element={<ComparisonPage />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  )
}

export default App
