import { motion } from 'framer-motion'
import { ScoreTrend } from './ScoreTrend'
import { PortalPerformance } from './PortalPerformance'
import { ProjectEval } from './ProjectEval'
import { TrainingEval } from './TrainingEval'

export default function InsightsPage() {
  return (
    <div className="p-8 space-y-6">
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
        <h1 className="text-2xl font-display font-bold text-white">Insights</h1>
        <p className="text-sm text-white/40 font-body mt-1">Analytics, trends, and ROI evaluations</p>
      </motion.div>

      <div className="grid grid-cols-2 gap-4">
        <ScoreTrend />
        <PortalPerformance />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <ProjectEval />
        <TrainingEval />
      </div>
    </div>
  )
}
