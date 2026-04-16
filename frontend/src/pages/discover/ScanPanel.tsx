import { useState } from 'react'
import { motion } from 'framer-motion'
import { GlassCard } from '@/components/GlassCard'
import { Search, Loader2, CheckCircle } from 'lucide-react'
import { useStartScan, useScanStatus } from '@/hooks/useScanner'

interface ScanPanelProps {
  onJobStarted: (jobId: string) => void
  activeJobId: string | null
}

export function ScanPanel({ onJobStarted, activeJobId }: ScanPanelProps) {
  const { mutate: startScan, isPending } = useStartScan()
  const { data: status } = useScanStatus(activeJobId)

  const handleScan = () => {
    startScan(undefined, { onSuccess: (res) => onJobStarted(res.job_id) })
  }

  return (
    <GlassCard className="p-6">
      <h3 className="text-sm font-display font-semibold text-white/60 uppercase tracking-wider mb-4">Portal Scanner</h3>

      {status?.status === 'running' ? (
        <motion.div className="space-y-3" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <div className="flex items-center gap-2 text-sm text-white/70 font-body">
            <Loader2 className="w-4 h-4 animate-spin text-brand-cyan-light" />
            Scanning portals…
          </div>
          <div className="w-full bg-white/5 rounded-full h-1.5 overflow-hidden">
            <motion.div
              className="h-full bg-gradient-brand rounded-full"
              initial={{ width: '0%' }}
              animate={{ width: `${((status.found ?? 0) / Math.max(status.total_companies ?? 1, 1)) * 100}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
          <p className="text-xs text-white/40 font-body">
            {status.found ?? 0} jobs found · {status.companies_scanned ?? 0} portals scanned
          </p>
        </motion.div>
      ) : status?.status === 'done' ? (
        <div className="flex items-center gap-2 text-sm text-emerald-300 font-body">
          <CheckCircle className="w-4 h-4" />
          Scan complete — {status.found} new jobs found
        </div>
      ) : (
        <div className="space-y-3">
          <p className="text-sm text-white/50 font-body">
            Scan 45+ configured company portals for matching roles.
          </p>
          <button
            onClick={handleScan}
            disabled={isPending}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-brand text-white text-sm font-body font-medium hover:opacity-90 transition-opacity disabled:opacity-40"
          >
            <Search className="w-4 h-4" />
            {isPending ? 'Starting...' : 'Start Scan'}
          </button>
        </div>
      )}
    </GlassCard>
  )
}
