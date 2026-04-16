import { GlassCard } from '@/components/GlassCard'
import { Eye } from 'lucide-react'

interface KeywordPanelProps {
  keywords: string[]
  onPreview: () => void
  isPreviewing: boolean
}

export function KeywordPanel({ keywords, onPreview, isPreviewing }: KeywordPanelProps) {
  return (
    <GlassCard className="p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-display font-semibold text-white/50 uppercase tracking-wider">
          Extracted Keywords <span className="ml-1 text-brand-cyan-light">{keywords.length}</span>
        </h3>
        <button
          onClick={onPreview}
          disabled={isPreviewing}
          className="flex items-center gap-1.5 text-xs text-white/50 hover:text-white/80 font-body transition-colors disabled:opacity-40"
        >
          <Eye className="w-3.5 h-3.5" /> {isPreviewing ? 'Building...' : 'Preview CV'}
        </button>
      </div>
      <div className="flex flex-wrap gap-2">
        {keywords.map((kw, i) => (
          <span
            key={i}
            className="px-2.5 py-1 rounded-full bg-brand-cyan/10 border border-brand-cyan/20 text-brand-cyan-light text-xs font-body"
          >
            {kw}
          </span>
        ))}
      </div>
    </GlassCard>
  )
}
