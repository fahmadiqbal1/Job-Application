import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { FileText, Send, BookOpen, PlusCircle } from 'lucide-react'
import { ScoreMeter } from '@/components/ScoreMeter'
import { scoreColor } from '@/lib/utils'
import type { EvalFinalState } from '@/hooks/useEvaluation'

interface ScoreRevealProps {
  result: EvalFinalState
  onReset: () => void
}

export function ScoreReveal({ result, onReset }: ScoreRevealProps) {
  const navigate = useNavigate()
  const { score, archetype, company, role, report_id } = result

  const verdict =
    score >= 4.5 ? { label: 'Excellent Match', color: 'text-emerald-300', bg: 'bg-emerald-400/10 border-emerald-400/30' } :
    score >= 3.5 ? { label: 'Good Match', color: 'text-amber-300', bg: 'bg-amber-400/10 border-amber-400/30' } :
    score >= 2.5 ? { label: 'Partial Match', color: 'text-orange-300', bg: 'bg-orange-400/10 border-orange-400/30' } :
    { label: 'Weak Match', color: 'text-red-300', bg: 'bg-red-400/10 border-red-400/30' }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="flex flex-col items-center gap-6 py-8"
    >
      {/* Score meter */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
        <ScoreMeter score={score} size="lg" animate />
      </motion.div>

      {/* Company + role */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="text-center"
      >
        <h3 className="text-xl font-display font-bold text-white">{company}</h3>
        <p className="text-sm text-white/50 font-body mt-1">{role}</p>
      </motion.div>

      {/* Archetype + verdict */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="flex gap-3"
      >
        <span className="px-3 py-1.5 rounded-full bg-white/8 border border-white/15 text-xs font-body text-white/70">
          {archetype}
        </span>
        <span className={`px-3 py-1.5 rounded-full border text-xs font-body font-medium ${verdict.bg} ${verdict.color}`}>
          {verdict.label}
        </span>
      </motion.div>

      {/* Action bar */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="flex flex-wrap gap-3 justify-center"
      >
        <button
          onClick={() => navigate('/cv-studio', { state: { report_id } })}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-brand text-white text-sm font-body font-medium hover:opacity-90 transition-opacity"
        >
          <FileText className="w-4 h-4" /> Generate CV
        </button>
        <button
          onClick={() => navigate('/outreach', { state: { company, role, report_id } })}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/8 border border-white/10 text-white text-sm font-body font-medium hover:bg-white/12 transition-colors"
        >
          <Send className="w-4 h-4" /> Outreach
        </button>
        <button
          onClick={() => navigate('/prepare', { state: { company, role, report_id } })}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/8 border border-white/10 text-white text-sm font-body font-medium hover:bg-white/12 transition-colors"
        >
          <BookOpen className="w-4 h-4" /> Prepare
        </button>
        <button
          onClick={onReset}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/8 border border-white/10 text-white/60 text-sm font-body font-medium hover:bg-white/12 transition-colors"
        >
          <PlusCircle className="w-4 h-4" /> New Evaluation
        </button>
      </motion.div>

      {score < 3.0 && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="text-xs text-orange-300/70 font-body text-center max-w-sm"
        >
          Score below 3.0 — this is a weak match. Consider skipping unless you have a specific reason to apply.
        </motion.p>
      )}
    </motion.div>
  )
}
