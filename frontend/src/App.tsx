import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import UploadPage from './pages/UploadPage'
import AnalysisDetailPage from './pages/AnalysisDetailPage'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <header className="app-header">
          <h1>Motor de Traducción Espacial (MTE)</h1>
          <p>Sistema de análisis y diagnóstico de datos espaciales</p>
        </header>
        <main className="app-main">
          <Routes>
            <Route path="/" element={<UploadPage />} />
            <Route path="/analysis/:analysisId" element={<AnalysisDetailPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
