import { usePipeline } from '../context/PipelineContext'
import { ATSScore } from './ATSScore'
import { Check, X } from 'lucide-react'

export function ApproveQueue() {
  const { pendingConfirmations, jobs, atsScores, confirmJob } = usePipeline()

  const pendingJobs = jobs.filter((j) => pendingConfirmations.includes(j.job_id))

  if (pendingJobs.length === 0) {
    return (
      <div className="bg-zinc-800 rounded-lg border border-zinc-700 p-12 text-center text-zinc-400">
        <p className="mb-2">No pending approvals</p>
        <p className="text-sm">Jobs will appear here when they need your approval</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {pendingJobs.map((job) => {
        const atsData = atsScores[job.job_id]
        return (
          <div
            key={job.job_id}
            className="bg-zinc-800 border border-orange-600/30 rounded-lg p-4 space-y-3"
          >
            {/* Header: Title, Company, Portal */}
            <div className="space-y-1">
              <h3 className="font-bold text-white">{job.title}</h3>
              <div className="flex items-center justify-between text-sm text-zinc-400">
                <span>{job.company}</span>
                <span className="bg-zinc-700 px-2 py-1 rounded text-xs">
                  {job.portal}
                </span>
              </div>
            </div>

            {/* ATS Score Badge */}
            {atsData && (
              <div className="w-full">
                <ATSScore
                  score={atsData.score}
                  missingKeywords={atsData.missing_keywords || []}
                  compact={false}
                />
              </div>
            )}

            {/* Cover Letter Preview */}
            {job.cover_letter_preview && (
              <div className="bg-zinc-900 rounded px-3 py-2 text-sm text-zinc-300 border border-zinc-700 max-h-24 overflow-y-auto">
                <span className="text-xs text-zinc-500">Cover Letter:</span>
                <p className="mt-1">{job.cover_letter_preview}</p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-2">
              <button
                onClick={() => confirmJob(job.job_id, 'YES')}
                className="flex items-center gap-2 flex-1 bg-green-600 hover:bg-green-700 text-white font-medium py-2 rounded transition"
              >
                <Check size={16} />
                Approve & Apply
              </button>
              <button
                onClick={() => confirmJob(job.job_id, 'SKIP')}
                className="flex items-center gap-2 flex-1 bg-zinc-700 hover:bg-zinc-600 text-white font-medium py-2 rounded transition"
              >
                <X size={16} />
                Skip
              </button>
            </div>
          </div>
        )
      })}
    </div>
  )
}
