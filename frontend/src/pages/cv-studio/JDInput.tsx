import { useState } from 'react'
import { GlassCard } from '@/components/GlassCard'
import { Sparkles } from 'lucide-react'

interface JDInputProps {
  onExtract: (text: string) => void
  isLoading: boolean
}

export function JDInput({ onExtract, isLoading }: JDInputProps) {
  const [value, setValue] = useState('')

  return (
    <GlassCard className="p-5">
      <h3 className="text-xs font-display font-semibold text-white/50 uppercase tracking-wider mb-3">Job Description</h3>
      <textarea
        value={value}
        onChange={e => setValue(e.target.value)}
        rows={8}
        placeholder="Paste the job description to extract keywords and tailor your CV..."
        className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white/80 placeholder:text-white/20 font-body text-sm focus:outline-none focus:border-brand-cyan/50 resize-none"
      />
      <button
        onClick={() => onExtract(value)}
        disabled={!value.trim() || isLoading}
        className="mt-3 w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-brand text-white text-sm font-body font-medium hover:opacity-90 transition-opacity disabled:opacity-40"
      >
        <Sparkles className="w-4 h-4" />
        {isLoading ? 'Extracting keywords...' : 'Extract Keywords'}
      </button>
    </GlassCard>
  )
}
