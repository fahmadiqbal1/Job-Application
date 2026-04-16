import { useState } from 'react'
import { motion } from 'framer-motion'
import { LayoutGrid, List } from 'lucide-react'
import { KanbanBoard } from './KanbanBoard'
import { TableView } from './TableView'
import { ApplicationDrawer } from './ApplicationDrawer'
import { cn } from '@/lib/utils'
import type { ApplicationEntry } from '@/lib/api'

type View = 'kanban' | 'table'

export default function ApplicationsPage() {
  const [view, setView] = useState<View>('kanban')
  const [selected, setSelected] = useState<ApplicationEntry | null>(null)

  return (
    <div className="p-8">
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="flex items-center justify-between mb-6"
      >
        <div>
          <h1 className="text-2xl font-display font-bold text-white">Applications</h1>
          <p className="text-sm text-white/40 font-body mt-1">Track your pipeline</p>
        </div>
        <div className="flex gap-1 p-1 rounded-xl bg-white/5">
          <button
            onClick={() => setView('kanban')}
            className={cn(
              'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-body transition-all',
              view === 'kanban' ? 'bg-white/12 text-white' : 'text-white/40 hover:text-white/70'
            )}
          >
            <LayoutGrid className="w-3.5 h-3.5" /> Kanban
          </button>
          <button
            onClick={() => setView('table')}
            className={cn(
              'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-body transition-all',
              view === 'table' ? 'bg-white/12 text-white' : 'text-white/40 hover:text-white/70'
            )}
          >
            <List className="w-3.5 h-3.5" /> Table
          </button>
        </div>
      </motion.div>

      {view === 'kanban'
        ? <KanbanBoard onCardClick={setSelected} />
        : <TableView onRowClick={setSelected} />
      }

      <ApplicationDrawer app={selected} onClose={() => setSelected(null)} />
    </div>
  )
}
