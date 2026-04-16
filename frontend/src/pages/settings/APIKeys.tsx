import { GlassCard } from '@/components/GlassCard'
import { CheckCircle, XCircle } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'

interface ProviderStatus { provider: string; configured: boolean }

export function APIKeys() {
  const { data: statuses = [] } = useQuery({
    queryKey: ['api-key-status'],
    queryFn: () => api.get<ProviderStatus[]>('/settings/api-keys'),
    retry: false,
  })

  return (
    <GlassCard className="p-5">
      <h3 className="text-xs font-display font-semibold text-white/50 uppercase tracking-wider mb-4">API Keys</h3>
      <div className="space-y-3">
        {statuses.map(s => (
          <div key={s.provider} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
            <span className="text-sm font-body text-white/70">{s.provider}</span>
            {s.configured
              ? <span className="flex items-center gap-1.5 text-xs text-emerald-300 font-body"><CheckCircle className="w-3.5 h-3.5" /> Configured</span>
              : <span className="flex items-center gap-1.5 text-xs text-red-400 font-body"><XCircle className="w-3.5 h-3.5" /> Not set</span>
            }
          </div>
        ))}
      </div>
      <p className="text-xs text-white/30 font-body mt-4">
        API keys are configured via <code className="text-white/50">.env</code> file on the server. Restart required after changes.
      </p>
    </GlassCard>
  )
}
