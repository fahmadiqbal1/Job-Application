import { useState } from 'react'
import { ChevronUp, ChevronDown } from 'lucide-react'
import { GlassCard } from '@/components/GlassCard'
import { StatusBadge } from '@/components/StatusBadge'
import { useApplications } from '@/hooks/useTracker'
import { cn, formatScore, scoreBg, formatDate } from '@/lib/utils'
import type { ApplicationEntry } from '@/lib/api'

type SortKey = 'num' | 'date' | 'company' | 'score' | 'status'
type SortDir = 'asc' | 'desc'

interface TableViewProps {
  onRowClick: (app: ApplicationEntry) => void
}

export function TableView({ onRowClick }: TableViewProps) {
  const { data: apps = [] } = useApplications()
  const [sortKey, setSortKey] = useState<SortKey>('num')
  const [sortDir, setSortDir] = useState<SortDir>('desc')

  const handleSort = (key: SortKey) => {
    if (sortKey === key) setSortDir(d => (d === 'asc' ? 'desc' : 'asc'))
    else { setSortKey(key); setSortDir('asc') }
  }

  const sorted = [...apps].sort((a, b) => {
    let av: string | number = a[sortKey] ?? ''
    let bv: string | number = b[sortKey] ?? ''
    if (sortKey === 'score') {
      av = parseFloat(formatScore(a.score)) || 0
      bv = parseFloat(formatScore(b.score)) || 0
    }
    if (av < bv) return sortDir === 'asc' ? -1 : 1
    if (av > bv) return sortDir === 'asc' ? 1 : -1
    return 0
  })

  const SortIcon = ({ col }: { col: SortKey }) =>
    sortKey === col
      ? (sortDir === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />)
      : <ChevronDown className="w-3 h-3 opacity-20" />

  const th = (label: string, key: SortKey) => (
    <th
      className="text-left text-xs font-display font-semibold text-white/40 uppercase tracking-wide pb-3 pr-4 cursor-pointer hover:text-white/70 transition-colors"
      onClick={() => handleSort(key)}
    >
      <div className="flex items-center gap-1">{label} <SortIcon col={key} /></div>
    </th>
  )

  return (
    <GlassCard className="p-6 overflow-x-auto">
      <table className="w-full text-sm font-body">
        <thead>
          <tr>
            {th('#', 'num')}
            {th('Date', 'date')}
            {th('Company', 'company')}
            <th className="text-left text-xs font-display font-semibold text-white/40 uppercase tracking-wide pb-3 pr-4">Role</th>
            {th('Score', 'score')}
            {th('Status', 'status')}
            <th className="text-left text-xs font-display font-semibold text-white/40 uppercase tracking-wide pb-3">PDF</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
          {sorted.map(app => {
            const scoreNum = app.score !== 'N/A' ? parseFloat(formatScore(app.score)) : null
            return (
              <tr
                key={app.num}
                className="hover:bg-white/4 cursor-pointer transition-colors"
                onClick={() => onRowClick(app)}
              >
                <td className="py-3 pr-4 text-white/30">{String(app.num).padStart(3, '0')}</td>
                <td className="py-3 pr-4 text-white/50">{formatDate(app.date)}</td>
                <td className="py-3 pr-4 text-white font-medium">{app.company}</td>
                <td className="py-3 pr-4 text-white/60 max-w-xs truncate">{app.role}</td>
                <td className="py-3 pr-4">
                  {scoreNum !== null ? (
                    <span className={cn('text-xs px-2 py-0.5 rounded-full border', scoreBg(scoreNum))}>
                      {scoreNum.toFixed(1)}
                    </span>
                  ) : <span className="text-white/20">—</span>}
                </td>
                <td className="py-3 pr-4"><StatusBadge status={app.status} /></td>
                <td className="py-3 text-sm">{app.pdf}</td>
              </tr>
            )
          })}
          {sorted.length === 0 && (
            <tr>
              <td colSpan={7} className="py-12 text-center text-white/30 text-sm">
                No applications yet — evaluate an offer to get started.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </GlassCard>
  )
}
