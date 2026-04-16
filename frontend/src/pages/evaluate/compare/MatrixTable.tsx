import { GlassCard } from '@/components/GlassCard'
import { cn } from '@/lib/utils'
import type { ComparisonMatrix } from '@/lib/api'

interface MatrixTableProps {
  matrix: ComparisonMatrix
}

function cellColor(value: number, weight: number): string {
  const weighted = value * weight
  if (weighted >= 3.5) return 'text-emerald-300 bg-emerald-400/8'
  if (weighted >= 2.5) return 'text-amber-300 bg-amber-400/8'
  if (weighted >= 1.5) return 'text-orange-300 bg-orange-400/8'
  return 'text-red-300 bg-red-400/8'
}

export function MatrixTable({ matrix }: MatrixTableProps) {
  const { dimensions, offers, totals } = matrix

  return (
    <GlassCard className="p-6 overflow-x-auto">
      <h3 className="text-sm font-display font-semibold text-white/60 uppercase tracking-wider mb-4">
        Comparison Matrix
      </h3>
      <table className="w-full text-xs font-body">
        <thead>
          <tr>
            <th className="text-left text-white/40 pb-3 pr-4 font-medium min-w-40">Dimension</th>
            <th className="text-center text-white/40 pb-3 pr-4 font-medium">Weight</th>
            {offers.map(o => (
              <th key={o.report_id} className="text-center text-white/80 pb-3 pr-4 font-medium min-w-28">
                <div>{o.company}</div>
                <div className="text-white/40 font-normal truncate max-w-28">{o.role}</div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
          {dimensions.map(dim => (
            <tr key={dim.key}>
              <td className="py-2.5 pr-4 text-white/70">{dim.label}</td>
              <td className="py-2.5 pr-4 text-center text-white/40">{(dim.weight * 100).toFixed(0)}%</td>
              {offers.map(o => {
                const val = o.scores[dim.key] ?? 0
                return (
                  <td key={o.report_id} className="py-2.5 pr-4 text-center">
                    <span className={cn('px-2 py-0.5 rounded-md', cellColor(val, dim.weight))}>
                      {val.toFixed(1)}
                    </span>
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
        <tfoot className="border-t border-white/15">
          <tr>
            <td colSpan={2} className="pt-3 text-white/60 font-medium">Weighted Total</td>
            {totals.map(t => (
              <td key={t.report_id} className="pt-3 text-center">
                <span className={cn(
                  'text-base font-display font-bold',
                  t.total >= 4 ? 'text-emerald-300' :
                  t.total >= 3 ? 'text-amber-300' : 'text-red-300'
                )}>
                  {t.total.toFixed(2)}
                </span>
              </td>
            ))}
          </tr>
        </tfoot>
      </table>
    </GlassCard>
  )
}
