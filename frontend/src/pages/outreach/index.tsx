import { useState } from 'react'
import { useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useMutation } from '@tanstack/react-query'
import { GlassCard } from '@/components/GlassCard'
import { ContactFinder } from './ContactFinder'
import { MessageGenerator } from './MessageGenerator'
import { Users } from 'lucide-react'
import { api } from '@/lib/api'
import type { Contact, OutreachResult } from '@/lib/api'

export default function OutreachPage() {
  const location = useLocation()
  const [company, setCompany] = useState(location.state?.company ?? '')
  const [role, setRole] = useState(location.state?.role ?? '')
  const [selected, setSelected] = useState<Contact | null>(null)

  const { mutate: findContacts, data: contacts = [], isPending: finding } = useMutation({
    mutationFn: (req: { company: string; role: string }) =>
      api.post<Contact[]>('/outreach/find-contacts', req),
  })

  const { mutate: generateMessage, data: msgResult, isPending: generating } = useMutation({
    mutationFn: (req: { contact: Contact; company: string; role: string; report_id?: string }) =>
      api.post<OutreachResult>('/outreach/message', req),
  })

  const handleFind = () => {
    if (company && role) findContacts({ company, role })
  }

  return (
    <div className="p-8 space-y-6">
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
        <h1 className="text-2xl font-display font-bold text-white">Outreach</h1>
        <p className="text-sm text-white/40 font-body mt-1">Find contacts and craft personalised messages</p>
      </motion.div>

      {/* Input row */}
      <GlassCard className="p-5">
        <div className="flex gap-2">
          <input
            value={company} onChange={e => setCompany(e.target.value)}
            placeholder="Company name"
            className="flex-1 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder:text-white/20 font-body text-sm focus:outline-none focus:border-brand-cyan/50"
          />
          <input
            value={role} onChange={e => setRole(e.target.value)}
            placeholder="Role title"
            className="flex-1 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder:text-white/20 font-body text-sm focus:outline-none focus:border-brand-cyan/50"
          />
          <button
            onClick={handleFind}
            disabled={!company || !role || finding}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-brand text-white text-sm font-body font-medium hover:opacity-90 transition-opacity disabled:opacity-40"
          >
            <Users className="w-4 h-4" /> {finding ? 'Finding...' : 'Find Contacts'}
          </button>
        </div>
      </GlassCard>

      <div className="grid grid-cols-2 gap-4">
        <ContactFinder contacts={contacts} isLoading={finding} onSelect={setSelected} selected={selected} />
        <MessageGenerator
          contact={selected}
          result={msgResult}
          isLoading={generating}
          onGenerate={(c) => generateMessage({ contact: c, company, role, report_id: location.state?.report_id })}
        />
      </div>
    </div>
  )
}
