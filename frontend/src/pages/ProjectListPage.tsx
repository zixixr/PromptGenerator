import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useProjectStore } from '../store/projectStore'
import api from '../lib/api'
import './ProjectListPage.css'

function ProjectListPage() {
  const { projects, setProjects, removeProject } = useProjectStore()

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      const data = await api.listProjects()
      setProjects(data)
    } catch (error) {
      console.error('Failed to load projects:', error)
    }
  }

  const handleDelete = async (projectId: string) => {
    if (!confirm('Are you sure you want to delete this project?')) return

    try {
      await api.deleteProject(projectId)
      removeProject(projectId)
    } catch (error) {
      console.error('Failed to delete project:', error)
    }
  }

  return (
    <div className="project-list-page">
      <div className="page-header">
        <h1>Projects</h1>
        <Link to="/projects/new">
          <button className="primary">Create Project</button>
        </Link>
      </div>

      {projects.length === 0 ? (
        <div className="empty-state card">
          <p>No projects yet. Create your first optimization project!</p>
        </div>
      ) : (
        <div className="projects-grid">
          {projects.map((project) => (
            <div key={project.id} className="project-card card">
              <div className="project-header">
                <h3>{project.name}</h3>
                <span className={`badge ${project.status}`}>
                  {project.status}
                </span>
              </div>
              <div className="project-info">
                <p className="project-model">Model: {project.target_model}</p>
                <p className="project-iterations">
                  Max Iterations: {project.max_iterations}
                </p>
                <p className="project-date">
                  Created: {new Date(project.created_at).toLocaleDateString()}
                </p>
              </div>
              <div className="project-actions">
                <Link to={`/projects/${project.id}`}>
                  <button className="primary">View Details</button>
                </Link>
                <button
                  className="danger"
                  onClick={() => handleDelete(project.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ProjectListPage
