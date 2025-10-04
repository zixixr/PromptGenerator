import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useProjectStore } from '../store/projectStore'
import api, { Project, Iteration } from '../lib/api'
import './ProjectDetailPage.css'

function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const { currentProject, setCurrentProject, updateProject } = useProjectStore()
  const [iterations, setIterations] = useState<Iteration[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (projectId) {
      loadProject(projectId)
    }
  }, [projectId])

  const loadProject = async (id: string) => {
    try {
      const project = await api.getProject(id)
      setCurrentProject(project)
      // In a real implementation, we'd fetch iterations from a dedicated endpoint
    } catch (error) {
      console.error('Failed to load project:', error)
    }
  }

  const handleStartOptimization = async () => {
    if (!projectId) return

    setLoading(true)
    try {
      await api.startOptimization(projectId)
      updateProject(projectId, { status: 'running' })
      // Poll for updates in real implementation
      setTimeout(() => loadProject(projectId), 2000)
    } catch (error) {
      console.error('Failed to start optimization:', error)
      alert('Failed to start optimization')
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async (format: 'json' | 'csv') => {
    if (!projectId) return

    try {
      const data = await api.exportProject(projectId, format)
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: format === 'json' ? 'application/json' : 'text/csv',
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `project-${projectId}.${format}`
      a.click()
    } catch (error) {
      console.error('Failed to export:', error)
    }
  }

  if (!currentProject) {
    return <div>Loading...</div>
  }

  return (
    <div className="project-detail-page">
      <div className="project-header">
        <div>
          <h1>{currentProject.name}</h1>
          <span className={`badge ${currentProject.status}`}>
            {currentProject.status}
          </span>
        </div>
        <div className="header-actions">
          {currentProject.status === 'draft' && (
            <button
              className="primary"
              onClick={handleStartOptimization}
              disabled={loading}
            >
              {loading ? 'Starting...' : 'Start Optimization'}
            </button>
          )}
          <button className="secondary" onClick={() => handleExport('json')}>
            Export JSON
          </button>
          <button className="secondary" onClick={() => handleExport('csv')}>
            Export CSV
          </button>
        </div>
      </div>

      <div className="project-content">
        <div className="info-section card">
          <h2>Configuration</h2>
          <div className="info-grid">
            <div>
              <label>Target Model</label>
              <p>{currentProject.target_model}</p>
            </div>
            <div>
              <label>Max Iterations</label>
              <p>{currentProject.max_iterations}</p>
            </div>
            <div>
              <label>Created</label>
              <p>{new Date(currentProject.created_at).toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="prompt-section card">
          <h2>Initial Prompt</h2>
          <pre className="prompt-content">{currentProject.initial_prompt}</pre>
        </div>

        {iterations.length > 0 && (
          <div className="iterations-section card">
            <h2>Iterations</h2>
            <div className="iterations-list">
              {iterations.map((iteration) => (
                <div key={iteration.id} className="iteration-item">
                  <div className="iteration-header">
                    <span>Iteration {iteration.iteration_number}</span>
                    <span className={`badge ${iteration.status}`}>
                      {iteration.status}
                    </span>
                  </div>
                  <div className="iteration-stats">
                    <span>✓ {iteration.passed_criteria_count} passed</span>
                    <span>✗ {iteration.failed_criteria_count} failed</span>
                    {iteration.duration_seconds && (
                      <span>{iteration.duration_seconds}s</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ProjectDetailPage
