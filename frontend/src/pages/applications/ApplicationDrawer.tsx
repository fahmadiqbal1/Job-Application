import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, FileText, Send, BookOpen, ExternalLink, Edit3, Check } from 'lucide-react'
import { StatusBadge } from '@/components/StatusBadge'
import { ScoreMeter } from '@/components/ScoreMeter'
import { useUpdateNotes, useUpdateStatus } from '@/hooks/useTracker'
import { formatScore, formatDate } from '@/lib/utils'
import { useNavigate } from 'react-router-dom'
import type { ApplicationEntry } from '@/lib/api'

const STATUSES = ['Evaluated', 'Applied', 'Responded', 'Interview', 'Offer', 'Rejected', 'Discarded', 'SKIP']

interface ApplicationDrawerProps {
  app: ApplicationEntry | null
  onClose: () => void
}

export function ApplicationDrawer({ app, onClose }: ApplicationDrawerProps) {
  const navigate = useNavigate()
  const [editingNotes, setEditingNotes] = useState(false)
  const [notesVal, setNotesVal] = useState('')
  const { mutate: updateNotes } = useUpdateNotes()
  const { mutate: updateStatus } = useUpdateStatus()

  const scoreNum = app?.score !== 'N/A' ? parseFloat(formatScore(app?.score ?? '')) : null

  const saveNotes = () => {
    if (!app) return
    updateNotes({ num: app.num, notes: notesVal })
    setEditingNotes(false)
  }

  return (
    <AnimatePresence>
      {app && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/40 z-40"
            onClick={onClose}
          />
          {/* Drawer */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 28, stiffness: 280 }}
            className="fixed right-0 top-0 h-full w-96 bg-navy-800 border-l border-white/10 z-50 flex flex-col"
          >
            {/* Header */}
            <div className="flex items-start justify-between p-6 border-b border-white/8">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-brand flex items-center justify-center text-white font-display font-bold">
                  {app.company[0]?.toUpperCase()}
                </div>
                <div>
                  <h3 className="font-display font-bold text-white">{app.company}</h3>
                  <p className="text-xs text-white/50 font-body">{app.role}</p>
                </div>
              </div>
              <button onClick={onClose} className="text-white/30 hover:text-white/70 transition-colors mt-1">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Score */}
              {scoreNum !== null && (
                <div className="flex justify-center">
                  <ScoreMeter score={scoreNum} size="sm" />
                </div>
              )}

              {/* Meta */}
              <div className="space-y-2 text-sm font-body">
                <div className="flex justify-between">
                  <span className="text-white/40">Date</span>
                  <span className="text-white/70">{formatDate(app.date)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-white/40">Status</span>
                  <StatusBadge status={app.status} />
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">PDF</span>
                  <span>{app.pdf}</span>
                </div>
                {app.report && (
                  <div className="flex justify-between">
                    <span className="text-white/40">Report</span>
                    <span className="text-white/70 text-xs">{app.report}</span>
                  </div>
                )}
              </div>

              {/* Status quick-change */}
              <div>
                <p className="text-xs font-display font-semibold text-white/40 uppercase tracking-wide mb-2">Change Status</p>
                <div className="flex flex-wrap gap-1.5">
                  {STATUSES.map(s => (
                    <button
                      key={s}
                      onClick={() => updateStatus({ num: app.num, status: s })}
                      className={`text-xs px-2.5 py-1 rounded-lg border font-body transition-colors ${
                        app.status === s
                          ? 'bg-brand-cyan/20 border-brand-cyan/40 text-brand-cyan-light'
                          : 'bg-white/5 border-white/10 text-white/50 hover:text-white/80'
                      }`}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>

              {/* Notes */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs font-display font-semibold text-white/40 uppercase tracking-wide">Notes</p>
                  {!editingNotes ? (
                    <button
                      onClick={() => { setNotesVal(app.notes ?? ''); setEditingNotes(true) }}
                      className="text-white/30 hover:text-white/70 transition-colors"
                    >
                      <Edit3 className="w-3.5 h-3.5" />
                    </button>
                  ) : (
                    <button onClick={saveNotes} className="text-emerald-400 hover:text-emerald-300 transition-colors">
                      <Check className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
                {editingNotes ? (
                  <textarea
                    value={notesVal}
                    onChange={e => setNotesVal(e.target.value)}
                    rows={4}
                    className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white/80 font-body text-xs focus:outline-none focus:border-brand-cyan/50 resize-none"
                  />
                ) : (
                  <p className="text-xs text-white/50 font-body">
                    {app.notes || <span className="italic text-white/25">No notes</span>}
                  </p>
                )}
              </div>
            </div>

            {/* Action buttons */}
            <div className="p-6 border-t border-white/8 space-y-2">
              <button
                onClick={() => navigate('/cv-studio', { state: { report_id: app.report } })}
                className="w-full flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-brand text-white text-sm font-body font-medium hover:opacity-90 transition-opacity"
              >
                <FileText className="w-4 h-4" /> Generate CV
              </button>
              <div className="flex gap-2">
                <button
                  onClick={() => navigate('/outreach', { state: { company: app.company, role: app.role } })}
                  className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-xl bg-white/8 border border-white/10 text-white text-sm font-body hover:bg-white/12 transition-colors"
                >
                  <Send className="w-3.5 h-3.5" /> Outreach
                </button>
                <button
                  onClick={() => navigate('/prepare', { state: { company: app.company, role: app.role } })}
                  className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-xl bg-white/8 border border-white/10 text-white text-sm font-body hover:bg-white/12 transition-colors"
                >
                  <BookOpen className="w-3.5 h-3.5" /> Prepare
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
