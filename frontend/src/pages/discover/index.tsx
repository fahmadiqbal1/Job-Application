import { useState } from 'react'
import { motion } from 'framer-motion'
import { ScanPanel } from './ScanPanel'
import { URLInbox } from './URLInbox'
import { ResultsGrid } from './ResultsGrid'

export default function DiscoverPage() {
  const [activeJobId, setActiveJobId] = useState<string | null>(null)

  return (
    <div className="p-8 space-y-6">
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
        <h1 className="text-2xl font-display font-bold text-white">Discover</h1>
        <p className="text-sm text-white/40 font-body mt-1">Scan portals for new opportunities</p>
      </motion.div>

      <div className="grid grid-cols-2 gap-4">
        <ScanPanel onJobStarted={setActiveJobId} activeJobId={activeJobId} />
        <URLInbox />
      </div>

      <div>
        <h2 className="text-xs font-display font-semibold text-white/40 uppercase tracking-wider mb-3">Scan Results</h2>
        <ResultsGrid />
      </div>
    </div>
  )
}
