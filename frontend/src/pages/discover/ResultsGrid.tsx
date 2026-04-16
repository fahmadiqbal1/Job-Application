import { motion } from 'framer-motion'
import { ExternalLink, Plus, Zap } from 'lucide-react'
import { GlassCard } from '@/components/GlassCard'
import { useScanResults, useAddToPipeline } from '@/hooks/useScanner'
import { useNavigate } from 'react-router-dom'
import type { ScanResult } from '@/lib/api'

export function ResultsGrid() {
  const { data: results = [] } = useScanResults()
  const { mutate: addToPipeline } = useAddToPipeline()
  const navigate = useNavigate()

  if (results.length === 0) {
    return (
      <GlassCard className="p-8 text-center col-span-3">
        <p className="text-sm text-white/30 font-body">No scan results yet — run a portal scan to discover new offers.</p>
      </GlassCard>
    )
  }

  return (
    <div className="grid grid-cols-3 gap-3">
      {results.map((result, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.03 }}
        >
          <GlassCard className="p-4 h-full flex flex-col">
            <div className="flex items-start gap-2 flex-1">
              <div className="w-8 h-8 rounded-lg bg-gradient-brand flex items-center justify-center text-white text-xs font-display font-bold shrink-0">
                {result.company[0]?.toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-body font-medium text-white truncate">{result.company}</div>
                <div className="text-xs text-white/50 truncate mt-0.5">{result.title}</div>
                {result.location && (
                  <div className="text-xs text-white/30 mt-0.5">{result.location}</div>
                )}
              </div>
            </div>
            <div className="flex items-center gap-1.5 mt-3 pt-3 border-t border-white/5">
              <button
                onClick={() => navigate('/evaluate', { state: { url: result.url } })}
                className="flex-1 flex items-center justify-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-gradient-brand text-white text-xs font-body hover:opacity-90 transition-opacity"
              >
                <Zap className="w-3 h-3" /> Evaluate
              </button>
              <button
                onClick={() => addToPipeline({ url: result.url, company: result.company, title: result.title })}
                className="flex items-center justify-center px-2.5 py-1.5 rounded-lg bg-white/8 border border-white/10 text-white/60 text-xs font-body hover:bg-white/12 transition-colors"
              >
                <Plus className="w-3 h-3" />
              </button>
              <a
                href={result.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center px-2.5 py-1.5 rounded-lg bg-white/8 border border-white/10 text-white/60 text-xs font-body hover:bg-white/12 transition-colors"
              >
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </GlassCard>
        </motion.div>
      ))}
    </div>
  )
}
