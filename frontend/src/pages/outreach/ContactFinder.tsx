import { GlassCard } from '@/components/GlassCard'
import { Skeleton } from '@/components/Skeleton'
import { ExternalLink, User } from 'lucide-react'
import type { Contact } from '@/lib/api'

interface ContactFinderProps {
  contacts: Contact[]
  isLoading: boolean
  onSelect: (contact: Contact) => void
  selected: Contact | null
}

export function ContactFinder({ contacts, isLoading, onSelect, selected }: ContactFinderProps) {
  return (
    <GlassCard className="p-5">
      <h3 className="text-xs font-display font-semibold text-white/50 uppercase tracking-wider mb-3">Contacts</h3>
      {isLoading ? (
        <div className="space-y-2">
          {[1, 2, 3].map(i => <Skeleton key={i} className="h-14 rounded-lg" />)}
        </div>
      ) : contacts.length === 0 ? (
        <p className="text-xs text-white/25 font-body text-center py-6">
          Enter company and role, then click Find Contacts
        </p>
      ) : (
        <div className="space-y-2">
          {contacts.map((c, i) => (
            <button
              key={i}
              onClick={() => onSelect(c)}
              className={`w-full text-left rounded-lg border p-3 transition-all ${
                selected?.name === c.name
                  ? 'border-brand-cyan/40 bg-brand-cyan/8'
                  : 'border-white/8 bg-white/3 hover:border-white/15'
              }`}
            >
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-full bg-gradient-brand flex items-center justify-center shrink-0">
                  <User className="w-3.5 h-3.5 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-body font-medium text-white">{c.name}</div>
                  <div className="text-xs text-white/40">{c.title}</div>
                </div>
                {c.linkedin_url && (
                  <a
                    href={c.linkedin_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={e => e.stopPropagation()}
                    className="text-white/30 hover:text-blue-400 transition-colors"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>
            </button>
          ))}
        </div>
      )}
    </GlassCard>
  )
}
