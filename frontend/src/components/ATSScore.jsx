import { useState } from 'react'
import { ChevronDown } from 'lucide-react'

export function ATSScore({
  score,
  missingKeywords = [],
  compact = false,
}) {
  const [expanded, setExpanded] = useState(false)

  // Color based on score
  let color = 'text-red-400'
  let bgColor = 'bg-red-900/30'
  if (score >= 90) {
    color = 'text-green-400'
    bgColor = 'bg-green-900/30'
  } else if (score >= 70) {
    color = 'text-yellow-400'
    bgColor = 'bg-yellow-900/30'
  }

  if (compact) {
    return (
      <div className={`px-2 py-1 rounded font-bold text-sm ${color} ${bgColor}`}>
        {score}%
      </div>
    )
  }

  return (
    <div className={`rounded border ${bgColor} border-zinc-700`}>
      {/* Header with score and toggle */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-zinc-800/50 transition"
      >
        <div>
          <div className="text-sm text-zinc-400">ATS Score</div>
          <div className={`text-2xl font-bold ${color}`}>{score}%</div>
        </div>
        <ChevronDown
          size={20}
          className={`text-zinc-400 transition ${expanded ? 'rotate-180' : ''}`}
        />
      </button>

      {/* Expanded: missing keywords list */}
      {expanded && missingKeywords.length > 0 && (
        <div className="border-t border-zinc-700 px-4 py-3 space-y-2">
          <div className="text-sm text-zinc-400">Missing Keywords:</div>
          <div className="flex flex-wrap gap-2">
            {missingKeywords.map((kw, idx) => (
              <span
                key={idx}
                className="text-xs bg-zinc-700 text-zinc-200 px-2 py-1 rounded"
              >
                {kw}
              </span>
            ))}
          </div>
        </div>
      )}

      {expanded && missingKeywords.length === 0 && (
        <div className="border-t border-zinc-700 px-4 py-3 text-sm text-green-400">
          ✓ All required keywords matched
        </div>
      )}
    </div>
  )
}
