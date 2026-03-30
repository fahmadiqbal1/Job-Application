import { useState } from 'react'
import { ChevronRight } from 'lucide-react'
import { StatusBadge } from './StatusBadge'
import { ATSScore } from './ATSScore'

export function JobCard({ job, onSelect, atsScore }) {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <button
      onClick={() => onSelect?.(job)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`
        w-full bg-zinc-800 border border-zinc-700 rounded-lg p-4 text-left
        transition hover:border-blue-500 hover:bg-zinc-700/50
        ${isHovered ? 'shadow-lg shadow-blue-500/10' : ''}
      `}
    >
      {/* Header: Title + Status Badge */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex-1 min-w-0">
          <h3 className="font-bold text-white truncate">{job.title}</h3>
          <p className="text-sm text-zinc-400 truncate">{job.company}</p>
        </div>
        <StatusBadge status={job.status || 'pending'} />
      </div>

      {/* Portal badge */}
      <div className="text-xs bg-zinc-700 text-zinc-300 px-2 py-1 rounded inline-block mb-3">
        {job.portal}
      </div>

      {/* ATS Score (compact) */}
      {atsScore && (
        <div className="mb-3">
          <ATSScore
            score={atsScore.score}
            missingKeywords={atsScore.missing_keywords || []}
            compact={true}
          />
        </div>
      )}

      {/* Expand indicator */}
      {isHovered && (
        <div className="flex items-center justify-end text-zinc-500 mt-2 text-sm">
          View details
          <ChevronRight size={16} />
        </div>
      )}
    </button>
  )
}
