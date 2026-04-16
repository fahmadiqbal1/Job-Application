import { motion, AnimatePresence } from 'framer-motion'
import { CheckCircle, Loader2, Clock } from 'lucide-react'
import { cn } from '@/lib/utils'
import { StreamingText } from '@/components/StreamingText'
import { useState } from 'react'
import type { BlockState } from '@/hooks/useEvaluation'

interface BlockCardProps {
  block: BlockState
}

export function BlockCard({ block }: BlockCardProps) {
  const [expanded, setExpanded] = useState(false)
  const { phase, label, content, status } = block

  const ringClass =
    status === 'done' ? 'border-emerald-400/50 bg-emerald-400/5' :
    status === 'streaming' ? 'border-brand-cyan-light/50 bg-brand-cyan/5 animate-pulse-slow' :
    'border-white/10 bg-white/3'

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: 16 }}
      animate={{ opacity: 1, x: 0 }}
      className={cn('rounded-xl border p-4 transition-colors duration-500', ringClass)}
    >
      <div
        className={cn('flex items-center gap-3', content && 'cursor-pointer')}
        onClick={() => content && setExpanded(e => !e)}
      >
        {/* Phase badge */}
        <div className={cn(
          'w-8 h-8 rounded-lg flex items-center justify-center text-sm font-display font-bold shrink-0',
          status === 'done' ? 'bg-emerald-400/20 text-emerald-300' :
          status === 'streaming' ? 'bg-brand-cyan/20 text-brand-cyan-light' :
          'bg-white/8 text-white/30',
        )}>
          {phase}
        </div>

        <div className="flex-1 min-w-0">
          <div className={cn('text-sm font-body font-medium',
            status === 'pending' ? 'text-white/30' : 'text-white/80'
          )}>
            {label}
          </div>
          {status === 'done' && content && (
            <div className="text-xs text-white/30 font-body mt-0.5 truncate">
              {content.slice(0, 80)}...
            </div>
          )}
        </div>

        {status === 'done' && <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />}
        {status === 'streaming' && <Loader2 className="w-4 h-4 text-brand-cyan-light animate-spin shrink-0" />}
        {status === 'pending' && <Clock className="w-4 h-4 text-white/20 shrink-0" />}
      </div>

      <AnimatePresence>
        {(status === 'streaming' || (status === 'done' && expanded)) && content && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="mt-3 pt-3 border-t border-white/8">
              <StreamingText
                content={content}
                isStreaming={status === 'streaming'}
                className="max-h-64 overflow-y-auto text-xs"
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
