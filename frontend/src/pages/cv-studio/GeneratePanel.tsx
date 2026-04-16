import { GlassCard } from '@/components/GlassCard'
import { Download, FileText } from 'lucide-react'
import type { CVGenerateResult } from '@/lib/api'

interface GeneratePanelProps {
  onGenerate: (format: 'A4' | 'Letter') => void
  isGenerating: boolean
  result: CVGenerateResult | undefined
}

export function GeneratePanel({ onGenerate, isGenerating, result }: GeneratePanelProps) {
  return (
    <GlassCard className="p-5">
      <h3 className="text-xs font-display font-semibold text-white/50 uppercase tracking-wider mb-3">Generate PDF</h3>
      <div className="flex gap-2">
        <button
          onClick={() => onGenerate('A4')}
          disabled={isGenerating}
          className="flex-1 flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl bg-white/8 border border-white/10 text-white text-sm font-body hover:bg-white/12 transition-colors disabled:opacity-40"
        >
          <FileText className="w-4 h-4" /> A4
        </button>
        <button
          onClick={() => onGenerate('Letter')}
          disabled={isGenerating}
          className="flex-1 flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl bg-white/8 border border-white/10 text-white text-sm font-body hover:bg-white/12 transition-colors disabled:opacity-40"
        >
          <FileText className="w-4 h-4" /> Letter
        </button>
      </div>

      {isGenerating && (
        <p className="text-xs text-white/40 font-body mt-3 text-center">Generating PDF...</p>
      )}

      {result && result.success && (
        <div className="mt-3 p-3 rounded-lg bg-emerald-400/8 border border-emerald-400/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-emerald-300 font-body font-medium">PDF Generated</p>
              <p className="text-[10px] text-white/40 font-body mt-0.5">
                {result.pages}p · {(result.size_bytes / 1024).toFixed(0)}KB
              </p>
            </div>
            <a
              href={`/api/v2/cv/download/${result.cv_id}`}
              download
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-400/15 text-emerald-300 text-xs font-body hover:bg-emerald-400/25 transition-colors"
            >
              <Download className="w-3.5 h-3.5" /> Download
            </a>
          </div>
        </div>
      )}
    </GlassCard>
  )
}
