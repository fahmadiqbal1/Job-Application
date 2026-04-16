import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { GlassCard } from '@/components/GlassCard'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer } from 'recharts'
import { api } from '@/lib/api'
import type { ProjectEvalResult } from '@/lib/api'

export function ProjectEval() {
  const [name, setName] = useState('')
  const [desc, setDesc] = useState('')
  const { mutate, data, isPending } = useMutation({
    mutationFn: (req: { name: string; description: string }) =>
      api.post<ProjectEvalResult>('/insights/project', req),
  })

  const chartData = data ? Object.entries(data.scores).map(([k, v]) => ({ dimension: k, value: v })) : []

  return (
    <GlassCard className="p-5">
      <h3 className="text-xs font-display font-semibold text-white/50 uppercase tracking-wider mb-3">Project Evaluation</h3>
      <div className="space-y-2 mb-3">
        <input value={name} onChange={e => setName(e.target.value)} placeholder="Project name"
          className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder:text-white/20 font-body text-sm focus:outline-none" />
        <textarea value={desc} onChange={e => setDesc(e.target.value)} placeholder="Describe the project..." rows={4}
          className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder:text-white/20 font-body text-sm focus:outline-none resize-none" />
        <button onClick={() => mutate({ name, description: desc })} disabled={!name || !desc || isPending}
          className="w-full py-2 rounded-xl bg-gradient-brand text-white text-sm font-body disabled:opacity-40">
          {isPending ? 'Evaluating...' : 'Evaluate Project'}
        </button>
      </div>
      {data && (
        <>
          <div className="text-center mb-2">
            <span className="text-2xl font-display font-bold text-white">{data.overall.toFixed(1)}</span>
            <span className="text-white/40 text-sm font-body">/5</span>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <RadarChart data={chartData}>
              <PolarGrid stroke="rgba(255,255,255,0.1)" />
              <PolarAngleAxis dataKey="dimension" tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 10 }} />
              <Radar dataKey="value" stroke="hsl(187,74%,50%)" fill="hsl(187,74%,50%)" fillOpacity={0.2} />
            </RadarChart>
          </ResponsiveContainer>
        </>
      )}
    </GlassCard>
  )
}
