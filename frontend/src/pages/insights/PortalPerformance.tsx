import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { GlassCard } from '@/components/GlassCard'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'

interface PortalStat { source: string; found: number; avg_score: number }

export function PortalPerformance() {
  const { data } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => api.get<{ portals: PortalStat[] }>('/insights/analytics'),
  })

  const portals = data?.portals ?? []

  return (
    <GlassCard className="p-6">
      <h3 className="text-sm font-display font-semibold text-white/60 uppercase tracking-wider mb-4">Portal Performance</h3>
      {portals.length === 0 ? (
        <p className="text-sm text-white/25 font-body text-center py-12">Run a scan to see portal performance</p>
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={portals} barSize={28}>
            <XAxis dataKey="source" tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis hide />
            <Tooltip
              contentStyle={{ background: '#141b2d', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, color: 'white' }}
              formatter={(v: number, name: string) => [name === 'found' ? `${v} jobs` : v.toFixed(1), name]}
            />
            <Bar dataKey="found" radius={[4, 4, 0, 0]}>
              {portals.map((_, i) => <Cell key={i} fill={`hsl(${187 + i * 30}, 60%, 50%)`} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </GlassCard>
  )
}
