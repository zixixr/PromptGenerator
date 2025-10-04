import { BrowserRouter, Route, Routes } from 'react-router-dom'
import ProjectListPage from './pages/ProjectListPage'
import ProjectDetailPage from './pages/ProjectDetailPage'
import CreateProjectPage from './pages/CreateProjectPage'
import SettingsPage from './pages/SettingsPage'
import Navigation from './components/Navigation'

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<ProjectListPage />} />
            <Route path="/projects/new" element={<CreateProjectPage />} />
            <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
