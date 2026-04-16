import { useState } from 'react'
import {
  DndContext,
  DragOverlay,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent,
} from '@dnd-kit/core'
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { motion } from 'framer-motion'
import { KanbanCard } from './KanbanCard'
import { useApplications, useUpdateStatus } from '@/hooks/useTracker'
import type { ApplicationEntry } from '@/lib/api'

const COLUMNS = [
  { id: 'Evaluated', label: 'Evaluated', color: 'border-sky-400/30 bg-sky-400/5' },
  { id: 'Applied', label: 'Applied', color: 'border-indigo-400/30 bg-indigo-400/5' },
  { id: 'Responded', label: 'Responded', color: 'border-purple-400/30 bg-purple-400/5' },
  { id: 'Interview', label: 'Interview', color: 'border-amber-400/30 bg-amber-400/5' },
  { id: 'Offer', label: 'Offer', color: 'border-emerald-400/30 bg-emerald-400/5' },
  { id: 'Rejected', label: 'Rejected', color: 'border-red-400/30 bg-red-400/5' },
  { id: 'Discarded', label: 'Discarded', color: 'border-white/10 bg-white/3' },
]

interface KanbanBoardProps {
  onCardClick: (app: ApplicationEntry) => void
}

export function KanbanBoard({ onCardClick }: KanbanBoardProps) {
  const { data: apps = [] } = useApplications()
  const { mutate: updateStatus } = useUpdateStatus()
  const [activeId, setActiveId] = useState<string | null>(null)

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  )

  const getColumnApps = (status: string) =>
    apps.filter(a => a.status === status)

  const activeApp = activeId ? apps.find(a => String(a.num) === activeId) : null

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(String(event.active.id))
  }

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    setActiveId(null)
    if (!over) return
    const overId = String(over.id)
    const colId = COLUMNS.find(c => c.id === overId)?.id
    if (colId) {
      const app = apps.find(a => String(a.num) === String(active.id))
      if (app && app.status !== colId) {
        updateStatus({ num: app.num, status: colId })
      }
    }
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="flex gap-3 overflow-x-auto pb-4">
        {COLUMNS.map((col, idx) => {
          const colApps = getColumnApps(col.id)
          return (
            <motion.div
              key={col.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              className={`flex-none w-56 rounded-xl border p-3 ${col.color}`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-display font-semibold text-white/60 uppercase tracking-wide">
                  {col.label}
                </span>
                <span className="text-xs text-white/30 font-body">{colApps.length}</span>
              </div>
              <SortableContext
                items={colApps.map(a => String(a.num))}
                strategy={verticalListSortingStrategy}
              >
                <div className="space-y-2 min-h-12">
                  {colApps.map(app => (
                    <KanbanCard key={app.num} app={app} onClick={() => onCardClick(app)} />
                  ))}
                </div>
              </SortableContext>
            </motion.div>
          )
        })}
      </div>

      <DragOverlay>
        {activeApp && (
          <div className="opacity-90 rotate-2 scale-105">
            <KanbanCard app={activeApp} onClick={() => {}} />
          </div>
        )}
      </DragOverlay>
    </DndContext>
  )
}
