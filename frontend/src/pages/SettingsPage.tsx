import { useState } from 'react'
import api from '../lib/api'
import './SettingsPage.css'

function SettingsPage() {
  const [provider, setProvider] = useState<string>('openai')
  const [apiKey, setApiKey] = useState<string>('')
  const [message, setMessage] = useState<string>('')

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      await api.storeCredential(provider, apiKey)
      setMessage('Credential saved successfully!')
      setApiKey('')
      setTimeout(() => setMessage(''), 3000)
    } catch (error) {
      setMessage('Failed to save credential')
      console.error('Failed to save credential:', error)
    }
  }

  return (
    <div className="settings-page">
      <h1>Settings</h1>

      <div className="settings-content">
        <div className="settings-section card">
          <h2>API Credentials</h2>
          <p className="section-description">
            Configure API keys for LLM providers. Keys are encrypted and stored
            locally.
          </p>

          <form onSubmit={handleSave} className="credentials-form">
            <div className="form-group">
              <label>Provider</label>
              <select
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
              >
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="google">Google</option>
                <option value="custom">Custom Endpoint</option>
              </select>
            </div>

            <div className="form-group">
              <label>API Key</label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Enter your API key"
                required
              />
            </div>

            <button type="submit" className="primary">
              Save Credential
            </button>

            {message && <div className="message">{message}</div>}
          </form>
        </div>

        <div className="settings-section card">
          <h2>About</h2>
          <p>Prompt Optimizer v0.1.0</p>
          <p className="about-text">
            Automated prompt iteration system for optimizing LLM prompts against
            custom evaluation criteria.
          </p>
        </div>
      </div>
    </div>
  )
}

export default SettingsPage
