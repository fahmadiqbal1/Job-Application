import { GlassCard } from '@/components/GlassCard'
import { MessageCard } from './MessageCard'
import { Skeleton } from '@/components/Skeleton'
import { Send } from 'lucide-react'
import type { Contact, OutreachResult } from '@/lib/api'

interface MessageGeneratorProps {
  contact: Contact | null
  result: OutreachResult | undefined
  isLoading: boolean
  onGenerate: (contact: Contact) => void
}

export function MessageGenerator({ contact, result, isLoading, onGenerate }: MessageGeneratorProps) {
  return (
    <GlassCard className="p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-display font-semibold text-white/50 uppercase tracking-wider">Messages</h3>
        {contact && (
          <button
            onClick={() => onGenerate(contact)}
            disabled={isLoading}
            className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-gradient-brand text-white font-body hover:opacity-90 transition-opacity disabled:opacity-40"
          >
            <Send className="w-3 h-3" /> Generate
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map(i => <Skeleton key={i} className="h-24 rounded-xl" />)}
        </div>
      ) : result ? (
        <div className="space-y-3">
          {result.variants.map((text, i) => (
            <MessageCard key={i} variant={i + 1} text={text} />
          ))}
        </div>
      ) : (
        <p className="text-xs text-white/25 font-body text-center py-6">
          {contact ? 'Click Generate to create message variants' : 'Select a contact first'}
        </p>
      )}
    </GlassCard>
  )
}
