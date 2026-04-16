import { useState } from 'react'
import { useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useMutation } from '@tanstack/react-query'
import { GlassCard } from '@/components/GlassCard'
import { InterviewPrepCard } from './InterviewPrepCard'
import { StoryBank } from './StoryBank'
import { CompanyResearch } from './CompanyResearch'
import { BookOpen, Building2 } from 'lucide-react'
import { api } from '@/lib/api'

export default function PreparePage() {
  const location = useLocation()
  const [company, setCompany] = useState(location.state?.company ?? '')
  const [role, setRole] = useState(location.state?.role ?? '')

  const { mutate: prepInterview, data: prepResult, isPending: prepping } = useMutation({
    mutationFn: (req: { company: string; role: string; report_id?: string }) =>
      api.post<{ content: string }>('/prepare/interview', req),
  })

  const { mutate: researchCompany, data: researchResult, isPending: researching } = useMutation({
    mutationFn: (req: { company: string; role: string }) =>
      api.post<{ content: string }>('/prepare/company', req),
  })

  return (
    <div className="p-8 space-y-6">
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
        <h1 className="text-2xl font-display font-bold text-white">Prepare</h1>
        <p className="text-sm text-white/40 font-body mt-1">Interview prep, company research, and story bank</p>
      </motion.div>

      <GlassCard className="p-5">
        <div className="flex gap-2">
          <input value={company} onChange={e => setCompany(e.target.value)} placeholder="Company"
            className="flex-1 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder:text-white/20 font-body text-sm focus:outline-none focus:border-brand-cyan/50" />
          <input value={role} onChange={e => setRole(e.target.value)} placeholder="Role"
            className="flex-1 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder:text-white/20 font-body text-sm focus:outline-none focus:border-brand-cyan/50" />
          <button
            onClick={() => prepInterview({ company, role, report_id: location.state?.report_id })}
            disabled={!company || !role || prepping}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-brand text-white text-sm font-body font-medium hover:opacity-90 transition-opacity disabled:opacity-40"
          >
            <BookOpen className="w-4 h-4" /> {prepping ? 'Preparing...' : 'Prepare'}
          </button>
          <button
            onClick={() => researchCompany({ company, role })}
            disabled={!company || researching}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/8 border border-white/10 text-white text-sm font-body hover:bg-white/12 transition-colors disabled:opacity-40"
          >
            <Building2 className="w-4 h-4" /> {researching ? 'Researching...' : 'Research Co.'}
          </button>
        </div>
      </GlassCard>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-4">
          <InterviewPrepCard content={prepResult?.content ?? null} isLoading={prepping} />
          <StoryBank />
        </div>
        <CompanyResearch content={researchResult?.content ?? null} isLoading={researching} />
      </div>
    </div>
  )
}
