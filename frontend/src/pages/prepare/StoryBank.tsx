import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { GlassCard } from '@/components/GlassCard'
import { Plus, ChevronDown, ChevronUp } from 'lucide-react'
import { api } from '@/lib/api'
import type { StoryEntry } from '@/lib/api'

function StoryRow({ story }: { story: StoryEntry }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="border border-white/8 rounded-xl overflow-hidden">
      <button
        className="w-full flex items-center justify-between p-4 hover:bg-white/4 transition-colors"
        onClick={() => setOpen(o => !o)}
      >
        <div className="text-left">
          <div className="text-sm font-body font-medium text-white">{story.situation}</div>
          <div className="text-xs text-white/40 mt-0.5">{story.tags?.join(', ')}</div>
        </div>
        {open ? <ChevronUp className="w-4 h-4 text-white/30" /> : <ChevronDown className="w-4 h-4 text-white/30" />}
      </button>
      {open && (
        <div className="px-4 pb-4 space-y-3 text-sm font-body border-t border-white/8 pt-4">
          <div><span className="text-white/40 text-xs uppercase tracking-wide">Task</span><p className="text-white/70 mt-1">{story.task}</p></div>
          <div><span className="text-white/40 text-xs uppercase tracking-wide">Action</span><p className="text-white/70 mt-1">{story.action}</p></div>
          <div><span className="text-white/40 text-xs uppercase tracking-wide">Result</span><p className="text-white/70 mt-1">{story.result}</p></div>
          {story.reflection && <div><span className="text-white/40 text-xs uppercase tracking-wide">Reflection</span><p className="text-white/70 mt-1">{story.reflection}</p></div>}
        </div>
      )}
    </div>
  )
}

export function StoryBank() {
  const qc = useQueryClient()
  const [adding, setAdding] = useState(false)
  const [form, setForm] = useState({ situation: '', task: '', action: '', result: '', reflection: '' })
  const { data: stories = [] } = useQuery({
    queryKey: ['stories'],
    queryFn: () => api.get<StoryEntry[]>('/prepare/story-bank'),
  })
  const { mutate: addStory } = useMutation({
    mutationFn: (s: Partial<StoryEntry>) => api.post('/prepare/story-bank', s),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['stories'] }); setAdding(false) },
  })

  return (
    <GlassCard className="p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xs font-display font-semibold text-white/50 uppercase tracking-wider">
          Story Bank <span className="ml-1 text-brand-cyan-light">{stories.length}</span>
        </h3>
        <button onClick={() => setAdding(a => !a)} className="text-white/30 hover:text-white/70 transition-colors">
          <Plus className="w-4 h-4" />
        </button>
      </div>

      {adding && (
        <div className="mb-4 space-y-2 p-4 rounded-xl bg-white/4 border border-white/8">
          {(['situation', 'task', 'action', 'result', 'reflection'] as const).map(f => (
            <textarea
              key={f}
              value={form[f]}
              onChange={e => setForm(v => ({ ...v, [f]: e.target.value }))}
              placeholder={f.charAt(0).toUpperCase() + f.slice(1)}
              rows={2}
              className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white/80 placeholder:text-white/20 font-body text-xs focus:outline-none resize-none"
            />
          ))}
          <button
            onClick={() => addStory(form)}
            className="px-3 py-1.5 rounded-lg bg-gradient-brand text-white text-xs font-body"
          >
            Save Story
          </button>
        </div>
      )}

      <div className="space-y-2 max-h-80 overflow-y-auto">
        {stories.length === 0
          ? <p className="text-xs text-white/25 font-body text-center py-4">No stories yet — run interview prep to auto-generate them</p>
          : stories.map((s, i) => <StoryRow key={i} story={s} />)
        }
      </div>
    </GlassCard>
  )
}
