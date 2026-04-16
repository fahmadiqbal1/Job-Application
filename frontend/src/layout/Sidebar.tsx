import { NavLink, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  LayoutDashboard, Search, BarChart2, Columns, FileText,
  BookOpen, Send, TrendingUp, Settings, Zap,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const NAV = [
  { to: '/', icon: LayoutDashboard, label: 'Command Center' },
  { to: '/discover', icon: Search, label: 'Discover' },
  { to: '/evaluate', icon: BarChart2, label: 'Evaluate' },
  { to: '/applications', icon: Columns, label: 'Applications' },
  { to: '/cv-studio', icon: FileText, label: 'CV Studio' },
  { to: '/prepare', icon: BookOpen, label: 'Prepare' },
  { to: '/outreach', icon: Send, label: 'Outreach' },
  { to: '/insights', icon: TrendingUp, label: 'Insights' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

interface SidebarProps {
  onCommandPalette: () => void
}

export function Sidebar({ onCommandPalette }: SidebarProps) {
  const location = useLocation()

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-navy-900/80 backdrop-blur-xl border-r border-white/8 flex flex-col z-30">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-white/8">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-brand flex items-center justify-center">
            <Zap className="w-4 h-4 text-white" />
          </div>
          <div>
            <div className="text-sm font-display font-bold text-white">Career Platform</div>
            <div className="text-xs text-white/40 font-body">AI Job Search</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {NAV.map(({ to, icon: Icon, label }) => {
          const active = to === '/' ? location.pathname === '/' : location.pathname.startsWith(to)
          return (
            <NavLink
              key={to}
              to={to}
              className={cn(
                'relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-body font-medium transition-all duration-150',
                active
                  ? 'text-white'
                  : 'text-white/50 hover:text-white/80 hover:bg-white/5',
              )}
            >
              {active && (
                <motion.div
                  layoutId="sidebar-active"
                  className="absolute inset-0 rounded-xl bg-white/10"
                  transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                />
              )}
              <Icon className={cn('relative z-10 w-4 h-4 shrink-0', active ? 'text-brand-cyan-light' : '')} />
              <span className="relative z-10">{label}</span>
            </NavLink>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-white/8">
        <button
          onClick={onCommandPalette}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg bg-white/4 border border-white/8 text-xs text-white/30 font-body hover:bg-white/8 hover:text-white/50 transition-colors"
        >
          <Search className="w-3 h-3" />
          <span className="flex-1 text-left">Quick actions</span>
          <kbd className="text-[10px] bg-white/8 px-1.5 py-0.5 rounded border border-white/10">⌘K</kbd>
        </button>
      </div>
    </aside>
  )
}
