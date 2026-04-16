import { motion } from 'framer-motion'
import { TrendingUp, CheckCircle, Star, Activity } from 'lucide-react'
import { GlassCard } from '@/components/GlassCard'
import { useTrackerStats } from '@/hooks/useTracker'
import { CardSkeleton } from '@/components/Skeleton'

function KPICard({ label, value, sub, icon: Icon, color }: {
  label: string; value: string | number; sub?: string; icon: typeof TrendingUp; color: string
}) {
  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <GlassCard className="p-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs text-white/40 font-body uppercase tracking-wider mb-2">{label}</p>
            <p className="text-3xl font-display font-bold text-white">{value}</p>
            {sub && <p className="text-xs text-white/40 font-body mt-1">{sub}</p>}
          </div>
          <div className={`p-2.5 rounded-xl ${color}`}>
            <Icon className="w-5 h-5" />
          </div>
        </div>
      </GlassCard>
    </motion.div>
  )
}

export function KPICards() {
  const { data: stats, isLoading } = useTrackerStats()

  if (isLoading) return (
    <div className="grid grid-cols-4 gap-4">
      {[...Array(4)].map((_, i) => <CardSkeleton key={i} />)}
    </div>
  )

  const applied = (stats?.by_status?.Applied ?? 0) + (stats?.by_status?.Responded ?? 0) +
    (stats?.by_status?.Interview ?? 0) + (stats?.by_status?.Offer ?? 0)
  const applyRate = stats?.total ? Math.round((applied / stats.total) * 100) : 0

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <KPICard label="Total Evaluated" value={stats?.total ?? 0} icon={Activity}
        color="bg-sky-400/15 text-sky-400" />
      <KPICard label="Applied" value={applied} sub={`${applyRate}% of evaluated`} icon={CheckCircle}
        color="bg-emerald-400/15 text-emerald-400" />
      <KPICard label="Avg Score" value={stats?.avg_score ? `${stats.avg_score}/5` : '—'} icon={Star}
        color="bg-amber-400/15 text-amber-400" />
      <KPICard label="With PDF" value={stats?.pdf_coverage_pct ? `${stats.pdf_coverage_pct}%` : '0%'}
        sub="CV coverage" icon={TrendingUp} color="bg-purple-400/15 text-purple-400" />
    </div>
  )
}
