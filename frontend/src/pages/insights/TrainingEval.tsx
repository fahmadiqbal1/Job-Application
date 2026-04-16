import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { GlassCard } from '@/components/GlassCard'
import { api } from '@/lib/api'
import { cn } from '@/lib/utils'
import type { TrainingEvalResult } from '@/lib/api'

export function TrainingEval() {
  const [name, setName] = useState('')
  const [desc, setDesc] = useState('')
  const [cost, setCost] = useState('')
  const [hours, setHours] = useState('')
  const { mutate, data, isPending } = useMutation({
    mutationFn: (req: { name: string; description: string; cost_usd?: number; hours?: number }) =>
      api.post<TrainingEvalResult>('/insights/training', req),
  })

  const verdictColor = data?.verdict === 'High ROI' ? 'text-emerald-300' :
    data?.verdict === 'Medium ROI' ? 'text-amber-300' : 'text-red-300'

  return (
    <GlassCard className="p-5">
      <h3 className="text-xs font-display font-semibold text-white/50 uppercase tracking-wider mb-3">Training ROI</h3>
      <div className="space-y-2 mb-3">
        <input value={name} onChange={e => setName(e.target.value)} placeholder="Course / certification name"
          className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder:text-white/20 font-body text-sm focus:outline-none" />
        <textarea value={desc} onChange={e => setDesc(e.target.value)} placeholder="What will you learn?" rows={3}
          className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder:text-white/20 font-body text-sm focus:outline-none resize-none" />
        <div className="flex gap-2">
          <input value={cost} onChange={e => setCost(e.target.value)} placeholder="Cost ($)" type="number"
            className="flex-1 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder:text-white/20 font-body text-sm focus:outline-none" />
          <input value={hours} onChange={e => setHours(e.target.value)} placeholder="Hours" type="number"
            className="flex-1 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder:text-white/20 font-body text-sm focus:outline-none" />
        </div>
        <button
          onClick={() => mutate({ name, description: desc, cost_usd: cost ? parseFloat(cost) : undefined, hours: hours ? parseInt(hours) : undefined })}
          disabled={!name || !desc || isPending}
          className="w-full py-2 rounded-xl bg-gradient-brand text-white text-sm font-body disabled:opacity-40"
        >
          {isPending ? 'Evaluating...' : 'Evaluate Training'}
        </button>
      </div>
      {data && (
        <div className="space-y-2 pt-3 border-t border-white/8">
          <div className="flex justify-between text-sm font-body">
            <span className="text-white/50">Score</span>
            <span className="text-white font-medium">{data.score.toFixed(1)}/5</span>
          </div>
          <div className="flex justify-between text-sm font-body">
            <span className="text-white/50">Verdict</span>
            <span className={cn('font-medium', verdictColor)}>{data.verdict}</span>
          </div>
          {data.recommendation && (
            <p className="text-xs text-white/50 font-body mt-2 leading-relaxed">{data.recommendation}</p>
          )}
        </div>
      )}
    </GlassCard>
  )
}
