import { FunnelChart as RFunnelChart, Funnel, LabelList, Tooltip, ResponsiveContainer } from 'recharts'
import { GlassCard } from '@/components/GlassCard'
import { useTrackerFunnel } from '@/hooks/useTracker'

const COLORS = ['#38bdf8', '#818cf8', '#fb923c', '#fbbf24', '#34d399']

export function FunnelChartCard() {
  const { data: funnel } = useTrackerFunnel()

  const chartData = (funnel?.stages ?? []).map((s, i) => ({
    name: s.name,
    value: s.count,
    fill: COLORS[i % COLORS.length],
  }))

  if (!chartData.length) return null

  return (
    <GlassCard className="p-6">
      <h3 className="text-sm font-display font-semibold text-white/60 uppercase tracking-wider mb-4">
        Application Funnel
      </h3>
      <ResponsiveContainer width="100%" height={220}>
        <RFunnelChart>
          <Tooltip
            contentStyle={{ background: '#141b2d', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, color: 'white' }}
            formatter={(v: number) => [v, 'Applications']}
          />
          <Funnel dataKey="value" data={chartData} isAnimationActive>
            <LabelList dataKey="name" position="center" fill="white" fontSize={11} />
          </Funnel>
        </RFunnelChart>
      </ResponsiveContainer>
    </GlassCard>
  )
}
