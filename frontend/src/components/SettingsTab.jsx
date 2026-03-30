import { useState, useEffect } from 'react'
import { useApi } from '../hooks/useApi'
import { Eye, EyeOff } from 'lucide-react'

export function SettingsTab() {
  const { get } = useApi()
  const [settings, setSettings] = useState(null)
  const [models, setModels] = useState(null)
  const [showSecrets, setShowSecrets] = useState(false)

  useEffect(() => {
    const loadSettings = async () => {
      const [settingsRes, modelsRes] = await Promise.all([
        get('/api/settings'),
        get('/api/models'),
      ])
      if (settingsRes.data) setSettings(settingsRes.data)
      if (modelsRes.data) setModels(modelsRes.data)
    }

    loadSettings()
  }, [get])

  if (!settings || !models) {
    return <div className="text-zinc-400">Loading...</div>
  }

  return (
    <div className="space-y-6 max-w-2xl">
      {/* API Keys */}
      <div className="bg-zinc-800 border border-zinc-700 rounded-lg p-6 space-y-4">
        <h2 className="text-lg font-bold text-white">API Keys</h2>
        <div className="space-y-3">
          <div>
            <label className="block text-sm text-zinc-400 mb-1">OpenAI API Key</label>
            <div className="flex items-center gap-2">
              <input
                type={showSecrets ? 'text' : 'password'}
                value={settings.openai_api_key}
                disabled
                className="flex-1 bg-zinc-700 border border-zinc-600 rounded px-3 py-2 text-white disabled:opacity-50 font-mono text-sm"
              />
              <button
                onClick={() => setShowSecrets(!showSecrets)}
                className="text-zinc-400 hover:text-zinc-200"
              >
                {showSecrets ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Model Selection */}
      <div className="bg-zinc-800 border border-zinc-700 rounded-lg p-6 space-y-4">
        <h2 className="text-lg font-bold text-white">Model Selection</h2>
        <div className="space-y-3">
          {models.agents.map((agent) => (
            <div key={agent}>
              <label className="block text-sm text-zinc-400 mb-1 capitalize">
                {agent.replace('_', ' ')} Agent
              </label>
              <select className="w-full bg-zinc-700 border border-zinc-600 rounded px-3 py-2 text-white">
                {models.models.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </div>
          ))}
        </div>
      </div>

      {/* Other Settings */}
      <div className="bg-zinc-800 border border-zinc-700 rounded-lg p-6 space-y-4">
        <h2 className="text-lg font-bold text-white">Settings</h2>
        <div className="space-y-3 text-sm text-zinc-400">
          <div>
            <span className="text-zinc-500">Resume Path:</span> {settings.resume_path}
          </div>
          <div>
            <span className="text-zinc-500">ATS Threshold:</span> {settings.target_ats_score}%
          </div>
          <div>
            <span className="text-zinc-500">Confirmation Timeout:</span> {settings.confirmation_timeout_secs}s
          </div>
        </div>
      </div>
    </div>
  )
}
