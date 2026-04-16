import { useEffect, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { GlassCard } from '@/components/GlassCard'
import { Save } from 'lucide-react'
import { api } from '@/lib/api'

export function PortalsEditor() {
  const qc = useQueryClient()
  const { data } = useQuery({
    queryKey: ['portals-raw'],
    queryFn: () => api.get<{ content: string }>('/settings/portals'),
  })
  const { mutate: save, isPending } = useMutation({
    mutationFn: (content: string) => api.put('/settings/portals', { content }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['portals-raw'] }),
  })

  const [content, setContent] = useState('')
  useEffect(() => { if (data?.content) setContent(data.content) }, [data])

  return (
    <GlassCard className="p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-display font-semibold text-white/50 uppercase tracking-wider">Portals Config (YAML)</h3>
        <button
          onClick={() => save(content)}
          disabled={isPending}
          className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-gradient-brand text-white font-body disabled:opacity-40"
        >
          <Save className="w-3 h-3" /> {isPending ? 'Saving...' : 'Save'}
        </button>
      </div>
      <textarea
        value={content}
        onChange={e => setContent(e.target.value)}
        rows={24}
        className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white/80 font-mono text-xs focus:outline-none focus:border-brand-cyan/50 resize-none"
      />
    </GlassCard>
  )
}
