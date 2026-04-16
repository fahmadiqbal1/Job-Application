import { useState } from 'react'
import { GlassCard } from '@/components/GlassCard'
import { Plus, Inbox } from 'lucide-react'
import { usePipeline, useAddToPipeline } from '@/hooks/useScanner'

export function URLInbox() {
  const { data: pending = [] } = usePipeline()
  const { mutate: addUrl, isPending } = useAddToPipeline()
  const [url, setUrl] = useState('')
  const [company, setCompany] = useState('')
  const [title, setTitle] = useState('')

  const handleAdd = () => {
    if (!url.trim()) return
    addUrl({ url: url.trim(), company: company.trim() || 'Unknown', title: title.trim() || 'Unknown Role' })
    setUrl(''); setCompany(''); setTitle('')
  }

  return (
    <GlassCard className="p-6">
      <h3 className="text-sm font-display font-semibold text-white/60 uppercase tracking-wider mb-4">
        URL Inbox <span className="ml-1 text-brand-cyan-light font-normal normal-case">{pending.length} pending</span>
      </h3>

      <div className="space-y-2 mb-4">
        <input
          value={url} onChange={e => setUrl(e.target.value)}
          placeholder="https://..."
          className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder:text-white/20 font-body text-sm focus:outline-none focus:border-brand-cyan/50"
        />
        <div className="flex gap-2">
          <input
            value={company} onChange={e => setCompany(e.target.value)}
            placeholder="Company"
            className="flex-1 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder:text-white/20 font-body text-sm focus:outline-none focus:border-brand-cyan/50"
          />
          <input
            value={title} onChange={e => setTitle(e.target.value)}
            placeholder="Role title"
            className="flex-1 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder:text-white/20 font-body text-sm focus:outline-none focus:border-brand-cyan/50"
          />
        </div>
        <button
          onClick={handleAdd}
          disabled={!url.trim() || isPending}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl bg-white/8 border border-white/10 text-white text-sm font-body hover:bg-white/12 transition-colors disabled:opacity-40"
        >
          <Plus className="w-3.5 h-3.5" /> Add to Pipeline
        </button>
      </div>

      {pending.length > 0 ? (
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {pending.map((item, i) => (
            <div key={i} className="flex items-center gap-2 text-xs font-body py-1.5 border-b border-white/5 last:border-0">
              <Inbox className="w-3 h-3 text-white/30 shrink-0" />
              <div className="flex-1 min-w-0">
                <span className="text-white/70 font-medium">{item.company}</span>
                <span className="text-white/30 mx-1">·</span>
                <span className="text-white/40 truncate">{item.role}</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-xs text-white/25 font-body text-center py-4">No pending URLs</p>
      )}
    </GlassCard>
  )
}
