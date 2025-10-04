import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useProjectStore } from '../store/projectStore'
import api, { ProjectCreate } from '../lib/api'
import './CreateProjectPage.css'

function CreateProjectPage() {
  const navigate = useNavigate()
  const { addProject } = useProjectStore()

  const [formData, setFormData] = useState<Partial<ProjectCreate>>({
    name: '',
    target_model: 'gpt-4',
    initial_prompt: '',
    max_iterations: 20,
    test_scenarios: [],
    evaluation_criteria: [],
    model_configuration: {
      provider: 'openai',
      model_name: 'gpt-4',
      temperature: 0.7,
      max_tokens: 2000,
    },
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const project = await api.createProject(formData as ProjectCreate)
      addProject(project)
      navigate(`/projects/${project.id}`)
    } catch (error) {
      console.error('Failed to create project:', error)
      alert('Failed to create project. Please check all fields.')
    }
  }

  const addTestScenario = () => {
    setFormData({
      ...formData,
      test_scenarios: [
        ...(formData.test_scenarios || []),
        { name: '', description: '', turn_limit: 5, priority: 5 },
      ],
    })
  }

  const addCriterion = () => {
    setFormData({
      ...formData,
      evaluation_criteria: [
        ...(formData.evaluation_criteria || []),
        {
          name: '',
          description: '',
          threshold: 70,
          is_predefined: false,
        },
      ],
    })
  }

  return (
    <div className="create-project-page">
      <h1>Create New Project</h1>

      <form onSubmit={handleSubmit} className="project-form">
        <div className="form-section card">
          <h2>Basic Information</h2>

          <div className="form-group">
            <label>Project Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label>Target Model</label>
            <select
              value={formData.target_model}
              onChange={(e) =>
                setFormData({ ...formData, target_model: e.target.value })
              }
            >
              <option value="gpt-4">GPT-4</option>
              <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
              <option value="claude-3-opus">Claude 3 Opus</option>
              <option value="claude-3-sonnet">Claude 3 Sonnet</option>
              <option value="gemini-pro">Gemini Pro</option>
            </select>
          </div>

          <div className="form-group">
            <label>Initial System Prompt</label>
            <textarea
              rows={6}
              value={formData.initial_prompt}
              onChange={(e) =>
                setFormData({ ...formData, initial_prompt: e.target.value })
              }
              required
            />
          </div>

          <div className="form-group">
            <label>Max Iterations</label>
            <input
              type="number"
              min="1"
              max="100"
              value={formData.max_iterations}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  max_iterations: parseInt(e.target.value),
                })
              }
            />
          </div>
        </div>

        <div className="form-section card">
          <div className="section-header">
            <h2>Test Scenarios</h2>
            <button type="button" onClick={addTestScenario} className="secondary">
              Add Scenario
            </button>
          </div>

          {formData.test_scenarios?.map((scenario, index) => (
            <div key={index} className="scenario-item">
              <input
                placeholder="Scenario Name"
                value={scenario.name}
                onChange={(e) => {
                  const updated = [...(formData.test_scenarios || [])]
                  updated[index].name = e.target.value
                  setFormData({ ...formData, test_scenarios: updated })
                }}
              />
              <textarea
                placeholder="Description"
                value={scenario.description}
                onChange={(e) => {
                  const updated = [...(formData.test_scenarios || [])]
                  updated[index].description = e.target.value
                  setFormData({ ...formData, test_scenarios: updated })
                }}
              />
            </div>
          ))}
        </div>

        <div className="form-section card">
          <div className="section-header">
            <h2>Evaluation Criteria</h2>
            <button type="button" onClick={addCriterion} className="secondary">
              Add Criterion
            </button>
          </div>

          {formData.evaluation_criteria?.map((criterion, index) => (
            <div key={index} className="criterion-item">
              <input
                placeholder="Criterion Name"
                value={criterion.name}
                onChange={(e) => {
                  const updated = [...(formData.evaluation_criteria || [])]
                  updated[index].name = e.target.value
                  setFormData({ ...formData, evaluation_criteria: updated })
                }}
              />
              <input
                type="number"
                placeholder="Threshold (0-100)"
                value={criterion.threshold}
                onChange={(e) => {
                  const updated = [...(formData.evaluation_criteria || [])]
                  updated[index].threshold = parseInt(e.target.value)
                  setFormData({ ...formData, evaluation_criteria: updated })
                }}
              />
            </div>
          ))}
        </div>

        <div className="form-actions">
          <button type="submit" className="primary">
            Create Project
          </button>
          <button
            type="button"
            onClick={() => navigate('/')}
            className="secondary"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}

export default CreateProjectPage
