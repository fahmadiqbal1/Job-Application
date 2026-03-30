import {
  Search,
  CheckSquare,
  Briefcase,
  Monitor,
  Settings,
} from 'lucide-react'
import { usePipeline } from '../context/PipelineContext'

export function TabBar({ activeTab, setActiveTab }) {
  const { activePendingCount } = usePipeline()

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: Search },
    { id: 'approve', label: 'Approve Queue', icon: CheckSquare, badge: activePendingCount },
    { id: 'jobs', label: 'Jobs', icon: Briefcase },
    { id: 'activity', label: 'Activity', icon: Monitor },
    { id: 'settings', label: 'Settings', icon: Settings },
  ]

  return (
    <div className="border-b border-zinc-700 bg-zinc-900 px-6">
      <div className="flex gap-1">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = activeTab === tab.id

          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition
                ${
                  isActive
                    ? 'border-b-2 border-blue-500 text-blue-400'
                    : 'border-b-2 border-transparent text-zinc-400 hover:text-zinc-200'
                }
              `}
            >
              <Icon size={18} />
              {tab.label}
              {tab.badge > 0 && (
                <span className="ml-1 bg-orange-600 text-white text-xs font-bold px-2 py-0.5 rounded-full">
                  {tab.badge}
                </span>
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}
