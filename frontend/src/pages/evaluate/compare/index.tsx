import { useState } from 'react'
import { motion } from 'framer-motion'
import { Plus, X, GitCompare } from 'lucide-react'
import { GlassCard } from '@/components/GlassCard'
import { MatrixTable } from './MatrixTable'
import { useCompareOffers } from '@/hooks/useEvaluation'

export default function ComparePage() {
  const [reportIds, setReportIds] = useState<string[]>(['', ''])
  const { mutate: compare, data: matrix, isPending } = useCompareOffers()

  const addSlot = () => setReportIds(ids => [...ids, ''])
  const removeSlot = (i: number) => setReportIds(ids => ids.filter((_, idx) => idx !== i))
  const updateSlot = (i: number, v: string) =>
    setReportIds(ids => ids.map((id, idx) => (idx === i ? v : id)))

  const handleCompare = () => {
    const valid = reportIds.filter(Boolean)
    if (valid.length >= 2) compare(valid)
  }

  return (
    <div className="p-8 space-y-6">
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
        <h1 className="text-2xl font-display font-bold text-white">Compare Offers</h1>
        <p className="text-sm text-white/40 font-body mt-1">10-dimension weighted matrix across multiple offers</p>
      </motion.div>

      <GlassCard className="p-6 max-w-xl">
        <div className="space-y-3">
          {reportIds.map((id, i) => (
            <div key={i} className="flex items-center gap-2">
              <input
                type="text"
                value={id}
                onChange={e => updateSlot(i, e.target.value)}
                placeholder={`Report ID (e.g. 012)`}
                className="flex-1 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder:text-white/25 font-body text-sm focus:outline-none focus:border-brand-cyan/50"
              />
              {reportIds.length > 2 && (
                <button onClick={() => removeSlot(i)} className="text-white/30 hover:text-red-400 transition-colors">
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          ))}
        </div>
        <div className="flex items-center gap-3 mt-4">
          <button
            onClick={addSlot}
            className="flex items-center gap-1.5 text-xs text-white/40 hover:text-white/70 font-body transition-colors"
          >
            <Plus className="w-3 h-3" /> Add offer
          </button>
          <button
            onClick={handleCompare}
            disabled={reportIds.filter(Boolean).length < 2 || isPending}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-brand text-white text-sm font-body font-medium hover:opacity-90 transition-opacity disabled:opacity-40 ml-auto"
          >
            <GitCompare className="w-4 h-4" />
            {isPending ? 'Comparing...' : 'Compare'}
          </button>
        </div>
      </GlassCard>

      {matrix && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
          <MatrixTable matrix={matrix} />
        </motion.div>
      )}
    </div>
  )
}
