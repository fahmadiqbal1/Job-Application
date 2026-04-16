import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import { GlassCard } from '@/components/GlassCard'
import { useScoreTrends } from '@/hooks/useTracker'

export function ScoreTrend() {
  const { data } = useScoreTrends()
  const trends = (data?.trends ?? []).map((t, i) => ({ ...t, index: i + 1 }))

  return (
    <GlassCard className="p-6">
      <h3 className="text-sm font-display font-semibold text-white/60 uppercase tracking-wider mb-4">Score Over Time</h3>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={trends}>
          <XAxis dataKey="index" tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis domain={[1, 5]} tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 11 }} axisLine={false} tickLine={false} />
          <Tooltip
            contentStyle={{ background: '#141b2d', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, color: 'white' }}
            formatter={(v: number) => [v.toFixed(1), 'score']}
          />
          <ReferenceLine y={3} stroke="rgba(255,255,255,0.15)" strokeDasharray="3 3" />
          <Line
            type="monotone"
            dataKey="score"
            stroke="hsl(187,74%,50%)"
            strokeWidth={2}
            dot={{ fill: 'hsl(187,74%,50%)', r: 3 }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </GlassCard>
  )
}
