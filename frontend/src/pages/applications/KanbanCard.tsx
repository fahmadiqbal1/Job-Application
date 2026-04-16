import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { motion } from 'framer-motion'
import { cn, formatScore, scoreBg, daysSince, formatDate } from '@/lib/utils'
import type { ApplicationEntry } from '@/lib/api'

interface KanbanCardProps {
  app: ApplicationEntry
  onClick: () => void
}

export function KanbanCard({ app, onClick }: KanbanCardProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: String(app.num),
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  const scoreNum = app.score !== 'N/A' ? parseFloat(formatScore(app.score)) : null

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className={cn(
        'rounded-xl border bg-navy-800 border-white/8 p-3 cursor-grab active:cursor-grabbing',
        'hover:border-white/15 transition-colors',
        isDragging && 'opacity-50 shadow-2xl scale-105 rotate-1'
      )}
      onClick={onClick}
    >
      <div className="flex items-start gap-2">
        <div className="w-8 h-8 rounded-lg bg-gradient-brand flex items-center justify-center text-white text-xs font-display font-bold shrink-0">
          {app.company[0]?.toUpperCase()}
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-body font-medium text-white truncate">{app.company}</div>
          <div className="text-xs text-white/40 truncate">{app.role}</div>
        </div>
      </div>
      <div className="flex items-center justify-between mt-2.5">
        {scoreNum !== null ? (
          <span className={cn('text-xs px-2 py-0.5 rounded-full border font-body', scoreBg(scoreNum))}>
            {scoreNum.toFixed(1)}
          </span>
        ) : (
          <span />
        )}
        <div className="flex items-center gap-1.5">
          {app.pdf === '✅' && <span className="text-[10px] text-emerald-400">PDF</span>}
          <span className="text-[10px] text-white/25 font-body">{daysSince(app.date)}d</span>
        </div>
      </div>
    </div>
  )
}
