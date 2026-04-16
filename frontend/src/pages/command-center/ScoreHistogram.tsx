import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { GlassCard } from '@/components/GlassCard'
import { useScoreTrends } from '@/hooks/useTracker'

export function ScoreHistogram() {
  const { data } = useScoreTrends()
  const trends = data?.trends ?? []

  // Build histogram buckets: 1-2, 2-3, 3-4, 4-5
  const buckets = [
    { label: '1–2', range: [1, 2], count: 0, color: '#f87171' },
    { label: '2–3', range: [2, 3], count: 0, color: '#fb923c' },
    { label: '3–4', range: [3, 4], count: 0, color: '#fbbf24' },
    { label: '4–5', range: [4, 5.1], count: 0, color: '#34d399' },
  ]

  trends.forEach(t => {
    const bucket = buckets.find(b => t.score >= b.range[0] && t.score < b.range[1])
    if (bucket) bucket.count++
  })

  return (
    <GlassCard className="p-6">
      <h3 className="text-sm font-display font-semibold text-white/60 uppercase tracking-wider mb-4">
        Score Distribution
      </h3>
      <ResponsiveContainer width="100%" height={160}>
        <BarChart data={buckets} barSize={48}>
          <XAxis dataKey="label" tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 12 }} axisLine={false} tickLine={false} />
          <YAxis hide />
          <Tooltip
            contentStyle={{ background: '#141b2d', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, color: 'white' }}
            formatter={(v: number) => [v, 'offers']}
          />
          <Bar dataKey="count" radius={[6, 6, 0, 0]}>
            {buckets.map((b, i) => <Cell key={i} fill={b.color} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </GlassCard>
  )
}
