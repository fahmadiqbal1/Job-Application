import { useEffect, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { GlassCard } from '@/components/GlassCard'
import { Save } from 'lucide-react'
import { api } from '@/lib/api'
import type { ProfileConfig } from '@/lib/api'

export function ProfileEditor() {
  const qc = useQueryClient()
  const { data: profile } = useQuery({
    queryKey: ['profile'],
    queryFn: () => api.get<ProfileConfig>('/settings/profile'),
  })
  const { mutate: save, isPending } = useMutation({
    mutationFn: (p: ProfileConfig) => api.put('/settings/profile', p),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['profile'] }),
  })

  const [form, setForm] = useState<ProfileConfig>({
    name: '', email: '', location: '', timezone: '',
    target_roles: [], salary_min: 0, salary_max: 0, currency: 'USD',
  })

  useEffect(() => { if (profile) setForm(profile) }, [profile])

  const field = (label: string, key: keyof ProfileConfig, type = 'text') => (
    <div>
      <label className="block text-xs text-white/40 font-body mb-1">{label}</label>
      <input
        type={type}
        value={String(form[key] ?? '')}
        onChange={e => setForm(f => ({ ...f, [key]: type === 'number' ? Number(e.target.value) : e.target.value }))}
        className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white font-body text-sm focus:outline-none focus:border-brand-cyan/50"
      />
    </div>
  )

  return (
    <GlassCard className="p-5">
      <h3 className="text-xs font-display font-semibold text-white/50 uppercase tracking-wider mb-4">Profile</h3>
      <div className="grid grid-cols-2 gap-3">
        {field('Full Name', 'name')}
        {field('Email', 'email', 'email')}
        {field('Location', 'location')}
        {field('Timezone', 'timezone')}
        {field('Salary Min', 'salary_min', 'number')}
        {field('Salary Max', 'salary_max', 'number')}
      </div>
      <div className="mt-3">
        <label className="block text-xs text-white/40 font-body mb-1">Target Roles (comma-separated)</label>
        <input
          value={form.target_roles?.join(', ') ?? ''}
          onChange={e => setForm(f => ({ ...f, target_roles: e.target.value.split(',').map(r => r.trim()) }))}
          className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white font-body text-sm focus:outline-none focus:border-brand-cyan/50"
        />
      </div>
      <button
        onClick={() => save(form)}
        disabled={isPending}
        className="mt-4 flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-brand text-white text-sm font-body font-medium disabled:opacity-40"
      >
        <Save className="w-4 h-4" /> {isPending ? 'Saving...' : 'Save Profile'}
      </button>
    </GlassCard>
  )
}
