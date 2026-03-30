import { useState } from 'react'
import { Play, Square } from 'lucide-react'
import { usePipeline } from '../context/PipelineContext'
import { PhaseProgress } from './PhaseProgress'

export function Dashboard() {
  const { run, startSearch, stopRun, dailyDigest } = usePipeline()
  const [keywords, setKeywords] = useState('')
  const [loading, setLoading] = useState(false)

  const handleStart = async () => {
    if (!keywords.trim() || keywords.trim().length < 3) {
      alert('Keywords must be at least 3 characters')
      return
    }

    setLoading(true)
    await startSearch(keywords)
    setLoading(false)
  }

  const handleStop = async () => {
    if (confirm('Stop the current run?')) {
      await stopRun()
    }
  }

  return (
    <div className="space-y-6">
      {/* Daily Digest Card */}
      {dailyDigest && (
        <div className="bg-zinc-800 border border-purple-700 rounded-lg p-4 space-y-2">
          <h3 className="text-purple-400 font-bold">✨ Daily Run Summary</h3>
          <div className="grid grid-cols-2 gap-2 text-sm text-zinc-300">
            <div>
              <span className="text-zinc-500">Keywords:</span> {dailyDigest.keywords}
            </div>
            <div>
              <span className="text-zinc-500">Jobs Found:</span> {dailyDigest.jobs_found || 0}
            </div>
            <div>
              <span className="text-zinc-500">Analyzed:</span> {dailyDigest.ats_analyzed || 0}
            </div>
            <div>
              <span className="text-zinc-500">Avg ATS:</span> {dailyDigest.avg_ats_score || 0}%
            </div>
          </div>
        </div>
      )}

      {/* Input Section */}
      <div className="bg-zinc-800 rounded-lg border border-zinc-700 p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">
            Job Search Keywords
          </label>
          <input
            type="text"
            placeholder="e.g., Product Manager, AI Engineer, SaaS"
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            disabled={run?.is_active}
            className="w-full bg-zinc-700 border border-zinc-600 rounded px-4 py-2 text-white placeholder-zinc-500 focus:border-blue-500 focus:outline-none disabled:opacity-50"
          />
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleStart}
            disabled={run?.is_active || loading}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-zinc-600 text-white font-medium px-6 py-2 rounded transition"
          >
            <Play size={18} />
            {loading ? 'Starting...' : 'Start Search'}
          </button>

          {run?.is_active && (
            <button
              onClick={handleStop}
              className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white font-medium px-6 py-2 rounded transition"
            >
              <Square size={18} />
              Stop
            </button>
          )}
        </div>
      </div>

      {/* Progress Section */}
      {run?.is_active && (
        <div className="bg-zinc-800 rounded-lg border border-zinc-700 p-6">
          <h2 className="text-lg font-bold text-zinc-100 mb-4">Pipeline Progress</h2>
          <PhaseProgress
            phase={run.phase}
            phaseDetail={run.phase_detail}
          />
        </div>
      )}

      {/* Idle State */}
      {!run?.is_active && (
        <div className="bg-zinc-800 rounded-lg border border-zinc-700 p-12 text-center text-zinc-400">
          <p className="mb-2">No active run</p>
          <p className="text-sm">Type keywords above and click Start to begin</p>
        </div>
      )}
    </div>
  )
}
