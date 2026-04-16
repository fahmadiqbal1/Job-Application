import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { Plus, Search, Zap } from 'lucide-react'
import { KPICards } from './KPICards'
import { FunnelChartCard } from './FunnelChart'
import { ScoreHistogram } from './ScoreHistogram'
import { GlassCard } from '@/components/GlassCard'
import { useApplications } from '@/hooks/useTracker'
import { StatusBadge } from '@/components/StatusBadge'
import { formatDate, formatScore, scoreBg } from '@/lib/utils'

function RecentApplications() {
  const { data: apps } = useApplications({ limit: 6 } as { limit: number })
  const recent = (apps ?? []).slice(0, 6)

  return (
    <GlassCard className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-display font-semibold text-white/60 uppercase tracking-wider">Recent</h3>
      </div>
      <div className="space-y-2">
        {recent.length === 0 && (
          <p className="text-sm text-white/30 font-body text-center py-6">No evaluations yet — paste a job URL to start.</p>
        )}
        {recent.map(app => (
          <div key={app.num} className="flex items-center gap-3 py-2 border-b border-white/5 last:border-0">
            <div className="w-8 h-8 rounded-lg bg-gradient-brand flex items-center justify-center text-white text-xs font-display font-bold shrink-0">
              {app.company[0]?.toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-body font-medium text-white truncate">{app.company}</div>
              <div className="text-xs text-white/40 truncate">{app.role}</div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              {app.score !== 'N/A' && (
                <span className={`text-xs px-2 py-0.5 rounded-full border font-body ${scoreBg(parseFloat(formatScore(app.score)))}`}>
                  {formatScore(app.score)}
                </span>
              )}
              <StatusBadge status={app.status} />
            </div>
          </div>
        ))}
      </div>
    </GlassCard>
  )
}

export default function CommandCenterPage() {
  const navigate = useNavigate()

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
        <h1 className="text-2xl font-display font-bold text-white">Command Center</h1>
        <p className="text-sm text-white/40 font-body mt-1">Your job search at a glance</p>
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}
        className="flex gap-3"
      >
        <button
          onClick={() => navigate('/evaluate')}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-brand text-white text-sm font-body font-medium hover:opacity-90 transition-opacity"
        >
          <Zap className="w-4 h-4" /> Evaluate Offer
        </button>
        <button
          onClick={() => navigate('/discover')}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/8 border border-white/10 text-white text-sm font-body font-medium hover:bg-white/12 transition-colors"
        >
          <Search className="w-4 h-4" /> Scan Portals
        </button>
        <button
          onClick={() => navigate('/applications')}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/8 border border-white/10 text-white text-sm font-body font-medium hover:bg-white/12 transition-colors"
        >
          <Plus className="w-4 h-4" /> Applications
        </button>
      </motion.div>

      {/* KPIs */}
      <KPICards />

      {/* Charts + Recent */}
      <div className="grid grid-cols-3 gap-4">
        <FunnelChartCard />
        <ScoreHistogram />
        <RecentApplications />
      </div>
    </div>
  )
}
