import { motion } from 'framer-motion'
import { GlassCard } from '@/components/GlassCard'
import { BlockCard } from './BlockCard'
import { ScoreReveal } from './ScoreReveal'
import type { BlockState, EvalFinalState } from '@/hooks/useEvaluation'

interface SplitViewProps {
  jdText: string
  blocks: BlockState[]
  finalResult: EvalFinalState | null
  onReset: () => void
}

export function SplitView({ jdText, blocks, finalResult, onReset }: SplitViewProps) {
  return (
    <div className="grid grid-cols-5 gap-4 mt-4">
      {/* Left: JD — 2/5 width */}
      <motion.div
        initial={{ opacity: 0, x: -16 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4 }}
        className="col-span-2"
      >
        <GlassCard className="p-5 h-full max-h-[70vh] overflow-y-auto">
          <h3 className="text-xs font-display font-semibold text-white/40 uppercase tracking-wider mb-3">
            Job Description
          </h3>
          <div className="text-sm font-body text-white/70 whitespace-pre-wrap leading-relaxed">
            {jdText || <span className="text-white/20 italic">Extracting job description...</span>}
          </div>
        </GlassCard>
      </motion.div>

      {/* Right: Evaluation blocks — 3/5 width */}
      <motion.div
        initial={{ opacity: 0, x: 16 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
        className="col-span-3 space-y-3"
      >
        {finalResult ? (
          <GlassCard className="p-6">
            <ScoreReveal result={finalResult} onReset={onReset} />
          </GlassCard>
        ) : (
          <>
            {blocks.map(block => (
              <BlockCard key={block.phase} block={block} />
            ))}
          </>
        )}
      </motion.div>
    </div>
  )
}
