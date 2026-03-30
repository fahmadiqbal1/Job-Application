import React, { createContext, useState, useCallback, useEffect } from 'react'
import { useWebSocket } from '../hooks/useWebSocket'
import { useApi } from '../hooks/useApi'

export const PipelineContext = createContext()

export function PipelineContextProvider({ children }) {
  // State
  const [run, setRun] = useState(null)
  const [jobs, setJobs] = useState([])
  const [pendingConfirmations, setPendingConfirmations] = useState([])
  const [atsScores, setAtsScores] = useState({})
  const [resumeEdits, setResumeEdits] = useState({})
  const [browserFrame, setBrowserFrame] = useState(null)
  const [actionLog, setActionLog] = useState([])
  const [activeTab, setActiveTab] = useState('dashboard')
  const [dailyDigest, setDailyDigest] = useState(null)

  const { get, post } = useApi()

  // Load initial status
  useEffect(() => {
    const loadStatus = async () => {
      const { data } = await get('/api/status')
      if (data) {
        setRun({
          is_active: data.is_active,
          run_id: data.run_id,
          phase: data.phase,
          phase_detail: data.phase_detail,
          started_at: data.started_at,
          stop_event: null,
        })
        if (data.pending_confirmations?.length > 0) {
          setPendingConfirmations(data.pending_confirmations)
        }
      }
    }

    loadStatus()
    const interval = setInterval(loadStatus, 5000) // Poll every 5s
    return () => clearInterval(interval)
  }, [get])

  // WebSocket for pipeline events
  const handlePipelineEvent = useCallback((event) => {
    const { type, data } = event

    switch (type) {
      case 'phase_start':
        setRun((prev) => ({ ...prev, phase: data.phase, phase_detail: data.detail }))
        break

      case 'job_found':
        setJobs((prev) => [...prev, data.job])
        break

      case 'ats_score':
        setAtsScores((prev) => ({
          ...prev,
          [data.job_id]: {
            score: data.score,
            missing_keywords: data.missing_keywords,
          },
        }))
        break

      case 'resume_diff':
        setResumeEdits((prev) => ({
          ...prev,
          [data.job_id]: {
            original: data.original,
            edited: data.edited,
          },
        }))
        break

      case 'confirmation_request':
        setPendingConfirmations((prev) => [
          ...prev,
          data.job_id,
        ])
        // Auto-switch to ApproveQueue tab
        setActiveTab('approve')
        break

      case 'job_applied':
        setJobs((prev) =>
          prev.map((job) =>
            job.job_id === data.job_id ? { ...job, status: 'applied' } : job
          )
        )
        setPendingConfirmations((prev) =>
          prev.filter((id) => id !== data.job_id)
        )
        break

      case 'pipeline_complete':
        setRun((prev) => ({ ...prev, is_active: false }))
        break

      case 'error':
        console.error('Pipeline error:', data.message)
        break

      case 'daily_digest':
        setDailyDigest(data)
        break

      default:
        break
    }
  }, [])

  useWebSocket('/api/ws/status', handlePipelineEvent)

  // WebSocket for browser stream
  const handleBrowserEvent = useCallback((event) => {
    const { type, data } = event

    switch (type) {
      case 'frame':
        setBrowserFrame({
          data: data.data,
          url: data.url,
          action: data.action,
          timestamp: data.timestamp,
        })
        setActionLog((prev) => [
          ...prev.slice(-99),
          { action: data.action, timestamp: data.timestamp },
        ])
        break

      case 'selector_result':
        // Portal health check result — handled by PortalManager component
        break

      default:
        break
    }
  }, [])

  useWebSocket('/api/ws/browser', handleBrowserEvent)

  // API actions
  const startSearch = useCallback(
    async (keywords) => {
      const { data, error } = await post('/api/search', { keywords })
      if (!error && data) {
        setJobs([])
        setAtsScores({})
        setResumeEdits({})
        setPendingConfirmations([])
        setRun({
          is_active: true,
          run_id: data.run_id,
          phase: 'scraping',
          phase_detail: null,
          started_at: new Date().toISOString(),
        })
      }
      return { data, error }
    },
    [post]
  )

  const stopRun = useCallback(async () => {
    const { error } = await post('/api/stop', {})
    if (!error) {
      setRun((prev) => ({ ...prev, is_active: false }))
    }
    return { error }
  }, [post])

  const confirmJob = useCallback(
    async (jobId, action) => {
      const { error } = await post(`/api/confirm/${jobId}`, { action })
      if (!error) {
        setPendingConfirmations((prev) => prev.filter((id) => id !== jobId))
      }
      return { error }
    },
    [post]
  )

  const refreshJobs = useCallback(async () => {
    const { data } = await get('/api/jobs')
    if (data?.jobs) {
      setJobs(data.jobs)
    }
  }, [get])

  const activePendingCount = pendingConfirmations.length

  const value = {
    // State
    run,
    jobs,
    pendingConfirmations,
    atsScores,
    resumeEdits,
    browserFrame,
    actionLog,
    activeTab,
    setActiveTab,
    dailyDigest,
    activePendingCount,

    // Actions
    startSearch,
    stopRun,
    confirmJob,
    refreshJobs,
  }

  return (
    <PipelineContext.Provider value={value}>
      {children}
    </PipelineContext.Provider>
  )
}

export function usePipeline() {
  const context = React.useContext(PipelineContext)
  if (!context) {
    throw new Error('usePipeline must be used within PipelineContextProvider')
  }
  return context
}
