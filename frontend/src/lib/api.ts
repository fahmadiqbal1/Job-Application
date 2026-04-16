/** Typed API client for Career Platform v2 endpoints */

const BASE = '/api/v2'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.text()
    throw new Error(err || `HTTP ${res.status}`)
  }
  return res.json()
}

// ── Tracker ────────────────────────────────────────────────────────────────

export const getApplications = (params?: { status?: string; min_score?: number; limit?: number }) =>
  request<ApplicationEntry[]>(`/tracker?${new URLSearchParams(params as Record<string, string> ?? {})}`)

export const getTrackerStats = () => request<TrackerStats>('/tracker/stats')
export const getTrackerFunnel = () => request<FunnelData>('/tracker/funnel')
export const getScoreTrends = () => request<{ trends: ScoreTrendPoint[] }>('/tracker/score-trends')

export const updateStatus = (num: number, status: string) =>
  request(`/tracker/${num}/status`, { method: 'POST', body: JSON.stringify({ status }) })

export const updateNotes = (num: number, notes: string) =>
  request(`/tracker/${num}/notes`, { method: 'POST', body: JSON.stringify({ notes }) })

export const triggerMerge = () => request('/tracker/merge', { method: 'POST' })

// ── Evaluation ────────────────────────────────────────────────────────────

export const startEvaluation = (input: string, options?: { generate_pdf?: boolean; draft_answers?: boolean }) =>
  request<EvaluationResult>('/evaluate', {
    method: 'POST',
    body: JSON.stringify({ input, input_type: 'auto', ...options }),
  })

export const getEvaluation = (reportId: string) =>
  request<{ report_id: string; content: string; path: string }>(`/evaluate/${reportId}`)

export const compareOffers = (reportIds: string[]) =>
  request<ComparisonMatrix>('/evaluate/compare', { method: 'POST', body: JSON.stringify({ report_ids: reportIds }) })

// ── CV Studio ──────────────────────────────────────────────────────────────

export const generateCV = (body: { jd_text?: string; report_id?: string; format?: string }) =>
  request<CVGenerateResult>('/cv/generate', { method: 'POST', body: JSON.stringify(body) })

export const previewCV = (body: { jd_text?: string; report_id?: string; keywords?: string[] }) =>
  fetch(`${BASE}/cv/preview`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
    .then(r => r.text())

// ── Scanner ────────────────────────────────────────────────────────────────

export const startScan = (levels?: string[]) =>
  request<{ job_id: string }>('/scan/start', { method: 'POST', body: JSON.stringify({ levels: levels ?? ['direct', 'greenhouse', 'search'] }) })

export const getScanStatus = (jobId: string) => request<ScanJobStatus>(`/scan/status/${jobId}`)
export const getScanResults = (jobId?: string) => request<{ results: ScanResult[]; job_id: string | null }>(`/scan/results${jobId ? `?job_id=${jobId}` : ''}`)
export const addToPipeline = (url: string, company?: string, title?: string) =>
  request('/scan/pipeline/add', { method: 'POST', body: JSON.stringify({ url, company, title }) })
export const getPipeline = () => request<{ pending: Array<{ url: string; company: string; role: string }>; count: number }>('/scan/pipeline')

// ── Outreach ───────────────────────────────────────────────────────────────

export const findContacts = (company: string, role: string) =>
  request<{ contacts: Contact[] }>('/outreach/find-contacts', { method: 'POST', body: JSON.stringify({ company, role }) })

export const generateMessage = (contact: Contact, report_id?: string, language?: string) =>
  request<OutreachResult>('/outreach/message', { method: 'POST', body: JSON.stringify({ contact, report_id, language }) })

// ── Prepare ────────────────────────────────────────────────────────────────

export const prepareInterview = (company: string, role: string, report_id?: string) =>
  request<InterviewPrepResult>('/prepare/interview', { method: 'POST', body: JSON.stringify({ company, role, report_id }) })

export const researchCompany = (company: string, role: string) =>
  request<{ content: string }>('/prepare/company', { method: 'POST', body: JSON.stringify({ company, role }) })

export const getStories = () => request<{ stories: StoryEntry[] }>('/prepare/story-bank')
export const addStory = (story: StoryEntry) =>
  request('/prepare/story-bank', { method: 'POST', body: JSON.stringify(story) })

// ── Insights ───────────────────────────────────────────────────────────────

export const evaluateProject = (body: ProjectEvalRequest) =>
  request<ProjectEvalResult>('/insights/project', { method: 'POST', body: JSON.stringify(body) })

export const evaluateTraining = (body: TrainingEvalRequest) =>
  request<TrainingEvalResult>('/insights/training', { method: 'POST', body: JSON.stringify(body) })

export const getAnalytics = () => request<AnalyticsData>('/insights/analytics')

// ── Settings ───────────────────────────────────────────────────────────────

export const getProfile = () => request<Record<string, unknown>>('/settings/profile')
export const updateProfile = (profile: Record<string, unknown>) =>
  request('/settings/profile', { method: 'PUT', body: JSON.stringify(profile) })

export const getCVContent = () => request<{ content: string }>('/settings/cv')
export const updateCVContent = (content: string) =>
  request('/settings/cv', { method: 'PUT', body: JSON.stringify({ content }) })

export const getPortalsConfig = () => request<{ raw_yaml: string }>('/settings/portals')
export const updatePortalsConfig = (raw_yaml: string) =>
  request('/settings/portals', { method: 'PUT', body: JSON.stringify({ raw_yaml }) })

// ── Generic api helper used by inline useMutation calls ───────────────────

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'POST', body: body ? JSON.stringify(body) : undefined }),
  put: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'PUT', body: body ? JSON.stringify(body) : undefined }),
}

// ── Types ──────────────────────────────────────────────────────────────────

export interface ApplicationEntry {
  num: number
  date: string
  company: string
  role: string
  score: string
  status: string
  pdf: string
  report: string | null
  report_path: string | null
  notes: string
}

export interface TrackerStats {
  total: number
  by_status: Record<string, number>
  avg_score: number | null
  pdf_coverage_pct: number
  report_coverage_pct: number
}

export interface FunnelData {
  stages: Array<{ name: string; count: number; stage_count: number; pct: number }>
}

export interface ScoreTrendPoint {
  date: string
  score: number
  company: string
  role: string
  archetype: string
}

export interface EvaluationBlock {
  phase: string
  label: string
  content: string
  done: boolean
}

export interface EvaluationResult {
  report_id: string
  company: string
  role: string
  archetype: string
  score: number
  blocks: EvaluationBlock[]
  keywords: string[]
  pdf_path: string | null
  report_path: string
  date: string
  url: string | null
}

export interface ComparisonMatrix {
  offers: Array<{ report_id: string; company: string; role: string; scores: Record<string, number> }>
  dimensions: Array<{ key: string; label: string; weight: number }>
  totals: Array<{ report_id: string; total: number }>
  recommendation: string
}

export interface CVGenerateResult {
  success: boolean
  cv_id: string
  pdf_path: string
  html_path: string
  keywords_injected: string[]
  keyword_coverage_pct: number
  pages: number
  size_bytes: number
  error?: string
}

export interface ScanResult {
  url: string
  title: string
  company: string
  location?: string
  source: string
  priority: boolean
  date_found: string
  status: string
}

export interface ScanJobStatus {
  job_id: string
  status: string
  companies_scanned: number
  total_companies: number
  scanned: number
  total: number
  found: number
  filtered: number
  new: number
  results: ScanResult[]
  error: string | null
}

export interface Contact {
  name: string
  title: string
  linkedin_url: string | null
  company: string
}

export interface OutreachResult {
  contact: Contact
  variants: string[]
  messages: string[]
  char_counts: number[]
}

export interface StoryEntry {
  title?: string
  situation: string
  task: string
  action: string
  result: string
  reflection?: string
  archetypes?: string[]
  tags?: string[]
}

export interface InterviewPrepResult {
  company: string
  role: string
  questions: Array<{ question: string; answer_guidance: string }>
  stories: StoryEntry[]
  red_flags: Array<{ question: string; how_to_handle: string }>
  day_of_tips: string[]
  output_path: string | null
}

export interface ProjectEvalRequest {
  name: string
  description: string
  tech_stack?: string[]
  status?: string
}

export interface ProjectEvalResult {
  name: string
  scores: Record<string, number>
  total: number
  overall: number
  verdict: string
  reasoning: string
  action_plan: string | null
}

export interface TrainingEvalRequest {
  name: string
  provider: string
  weeks: number
  hours_per_week: number
  description?: string
}

export interface TrainingEvalResult {
  name: string
  scores: Record<string, number>
  score: number
  total: number
  verdict: string
  timebox_weeks: number | null
  reasoning: string
  recommendation?: string
}

export interface AnalyticsData {
  stats: TrackerStats
  funnel: FunnelData
  score_trends: ScoreTrendPoint[]
}

export interface ProfileConfig {
  name: string
  email: string
  location: string
  timezone: string
  target_roles: string[]
  salary_min: number
  salary_max: number
  currency: string
}
