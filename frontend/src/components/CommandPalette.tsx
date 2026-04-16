import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Command } from 'cmdk'
import { useNavigate } from 'react-router-dom'
import { Zap, Search, Plus, LayoutDashboard, Briefcase, FileText, Telescope, BookOpen, Send, BarChart2, Settings } from 'lucide-react'
import { useApplications } from '@/hooks/useTracker'

const QUICK_ACTIONS = [
  { label: 'Evaluate new offer', icon: Zap, path: '/evaluate' },
  { label: 'Run portal scan', icon: Search, path: '/discover' },
  { label: 'Compare top offers', icon: BarChart2, path: '/evaluate/compare' },
  { label: 'Add to applications', icon: Plus, path: '/applications' },
]

const PAGES = [
  { label: 'Command Center', icon: LayoutDashboard, path: '/' },
  { label: 'Evaluate', icon: Zap, path: '/evaluate' },
  { label: 'Applications', icon: Briefcase, path: '/applications' },
  { label: 'CV Studio', icon: FileText, path: '/cv-studio' },
  { label: 'Discover', icon: Telescope, path: '/discover' },
  { label: 'Prepare', icon: BookOpen, path: '/prepare' },
  { label: 'Outreach', icon: Send, path: '/outreach' },
  { label: 'Insights', icon: BarChart2, path: '/insights' },
  { label: 'Settings', icon: Settings, path: '/settings' },
]

interface CommandPaletteProps {
  open: boolean
  onClose: () => void
}

export function CommandPalette({ open, onClose }: CommandPaletteProps) {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const { data: apps = [] } = useApplications()

  const filteredApps = query
    ? apps.filter(a =>
        `${a.company} ${a.role}`.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 5)
    : []

  const runAction = (path: string) => {
    navigate(path)
    onClose()
    setQuery('')
  }

  useEffect(() => {
    if (!open) setQuery('')
  }, [open])

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
            onClick={onClose}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: -8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: -8 }}
            transition={{ duration: 0.15 }}
            className="fixed top-[20vh] left-1/2 -translate-x-1/2 w-full max-w-xl z-50"
          >
            <Command className="rounded-2xl border border-white/15 bg-navy-800 shadow-2xl overflow-hidden font-body">
              <div className="flex items-center border-b border-white/8 px-4">
                <Search className="w-4 h-4 text-white/30 shrink-0" />
                <Command.Input
                  value={query}
                  onValueChange={setQuery}
                  placeholder="Search commands, applications..."
                  className="flex-1 bg-transparent py-4 px-3 text-sm text-white placeholder:text-white/30 focus:outline-none"
                />
              </div>
              <Command.List className="max-h-80 overflow-y-auto p-2">
                <Command.Empty className="py-8 text-center text-sm text-white/30">No results found</Command.Empty>

                <Command.Group heading={<span className="text-[10px] text-white/30 uppercase tracking-widest px-2 py-1">Quick Actions</span>}>
                  {QUICK_ACTIONS.map(a => (
                    <Command.Item
                      key={a.path}
                      onSelect={() => runAction(a.path)}
                      className="flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer text-sm text-white/70 hover:bg-white/8 hover:text-white aria-selected:bg-white/8 aria-selected:text-white transition-colors"
                    >
                      <a.icon className="w-4 h-4 text-brand-cyan-light" />
                      {a.label}
                    </Command.Item>
                  ))}
                </Command.Group>

                {filteredApps.length > 0 && (
                  <Command.Group heading={<span className="text-[10px] text-white/30 uppercase tracking-widest px-2 py-1">Applications</span>}>
                    {filteredApps.map(app => (
                      <Command.Item
                        key={app.num}
                        onSelect={() => runAction('/applications')}
                        className="flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer text-sm text-white/70 hover:bg-white/8 hover:text-white aria-selected:bg-white/8 transition-colors"
                      >
                        <div className="w-5 h-5 rounded bg-gradient-brand flex items-center justify-center text-white text-[10px] font-bold shrink-0">
                          {app.company[0]}
                        </div>
                        <span className="font-medium">{app.company}</span>
                        <span className="text-white/40 truncate">{app.role}</span>
                      </Command.Item>
                    ))}
                  </Command.Group>
                )}

                <Command.Group heading={<span className="text-[10px] text-white/30 uppercase tracking-widest px-2 py-1">Pages</span>}>
                  {PAGES.map(p => (
                    <Command.Item
                      key={p.path}
                      onSelect={() => runAction(p.path)}
                      className="flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer text-sm text-white/70 hover:bg-white/8 hover:text-white aria-selected:bg-white/8 transition-colors"
                    >
                      <p.icon className="w-4 h-4 text-white/40" />
                      {p.label}
                    </Command.Item>
                  ))}
                </Command.Group>
              </Command.List>
            </Command>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
