import { useState } from 'react'
import { usePipeline } from '../context/PipelineContext'
import { JobCard } from './JobCard'

export function JobsTab() {
  const { jobs, atsScores, resumeEdits } = usePipeline()
  const [filter, setFilter] = useState('all')
  const [selectedJob, setSelectedJob] = useState(null)

  const filters = [
    { id: 'all', label: 'All', count: jobs.length },
    { id: 'applied', label: 'Applied', count: jobs.filter((j) => j.status === 'applied').length },
    { id: 'pending', label: 'Pending', count: jobs.filter((j) => j.status === 'pending' || !j.status).length },
    { id: 'skipped', label: 'Skipped', count: jobs.filter((j) => j.status === 'skipped').length },
    { id: 'failed', label: 'Failed', count: jobs.filter((j) => j.status === 'failed').length },
  ]

  const filteredJobs = jobs.filter((job) => {
    if (filter === 'all') return true
    return job.status === filter || (filter === 'pending' && !job.status)
  })

  if (jobs.length === 0) {
    return (
      <div className="bg-zinc-800 rounded-lg border border-zinc-700 p-12 text-center text-zinc-400">
        <p className="mb-2">No jobs found</p>
        <p className="text-sm">Start a search from the Dashboard tab to see results</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
      {/* Left: Job list with filters */}
      <div className="lg:col-span-2 space-y-4">
        {/* Filter tabs */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          {filters.map((f) => (
            <button
              key={f.id}
              onClick={() => setFilter(f.id)}
              className={`
                px-4 py-2 rounded font-medium text-sm whitespace-nowrap transition
                ${
                  filter === f.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-zinc-700 text-zinc-300 hover:bg-zinc-600'
                }
              `}
            >
              {f.label} ({f.count})
            </button>
          ))}
        </div>

        {/* Job grid */}
        {filteredJobs.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 auto-rows-max">
            {filteredJobs.map((job) => (
              <JobCard
                key={job.job_id}
                job={job}
                atsScore={atsScores[job.job_id]}
                onSelect={() => setSelectedJob(job)}
              />
            ))}
          </div>
        ) : (
          <div className="bg-zinc-800 rounded-lg p-6 text-center text-zinc-400">
            No jobs with status "{filter}"
          </div>
        )}
      </div>

      {/* Right: Job detail panel */}
      {selectedJob && (
        <div className="bg-zinc-800 border border-zinc-700 rounded-lg p-4 space-y-4 overflow-y-auto max-h-96">
          <div>
            <h2 className="text-lg font-bold text-white">{selectedJob.title}</h2>
            <p className="text-zinc-400">{selectedJob.company}</p>
          </div>

          {/* Cover Letter */}
          {selectedJob.cover_letter && (
            <div className="space-y-2">
              <h3 className="text-sm font-bold text-zinc-300">Cover Letter</h3>
              <div className="bg-zinc-900 rounded p-3 text-sm text-zinc-300 max-h-32 overflow-y-auto">
                {selectedJob.cover_letter}
              </div>
            </div>
          )}

          {/* Tailored Resume (if available) */}
          {selectedJob.tailored_resume && (
            <div className="space-y-2">
              <h3 className="text-sm font-bold text-zinc-300">Tailored Resume</h3>
              <div className="bg-zinc-900 rounded p-3 text-xs text-zinc-400 max-h-40 overflow-y-auto font-mono">
                {selectedJob.tailored_resume}
              </div>
              <button className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm py-1 rounded transition">
                Copy Resume
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
