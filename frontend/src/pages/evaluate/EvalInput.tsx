import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Link2, FileText, Zap, X, CheckCircle } from 'lucide-react'
import { GlassCard } from '@/components/GlassCard'
import { cn } from '@/lib/utils'

const JOB_BOARD_PATTERNS = [
  /greenhouse\.io\/[^/]+\/jobs/,
  /lever\.co\/[^/]+\/postings/,
  /linkedin\.com\/jobs/,
  /workday\.com/,
  /jobs\.ashby\.io/,
  /boards\.greenhouse\.io/,
  /apply\.workable\.com/,
  /jobs\.lever\.co/,
  /careers\./,
  /\/jobs\//,
  /\/careers\//,
]

function isJobUrl(text: string): boolean {
  try {
    new URL(text.trim())
    return JOB_BOARD_PATTERNS.some(p => p.test(text))
  } catch {
    return false
  }
}

interface EvalInputProps {
  onSubmit: (input: string, isUrl: boolean) => void
  isLoading: boolean
}

export function EvalInput({ onSubmit, isLoading }: EvalInputProps) {
  const [value, setValue] = useState('')
  const [detectedUrl, setDetectedUrl] = useState(false)
  const [mode, setMode] = useState<'url' | 'jd'>('url')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (mode === 'url') {
      setDetectedUrl(isJobUrl(value))
    }
  }, [value, mode])

  const handlePaste = (e: React.ClipboardEvent) => {
    const text = e.clipboardData.getData('text')
    if (isJobUrl(text)) {
      e.preventDefault()
      setValue(text.trim())
      setDetectedUrl(true)
      setMode('url')
    }
  }

  const handleSubmit = () => {
    if (!value.trim() || isLoading) return
    onSubmit(value.trim(), mode === 'url' || detectedUrl)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleSubmit()
  }

  return (
    <GlassCard className="p-6">
      <h2 className="text-lg font-display font-bold text-white mb-4">Evaluate an Offer</h2>

      {/* Mode toggle */}
      <div className="flex gap-1 p-1 rounded-xl bg-white/5 mb-4 w-fit">
        <button
          onClick={() => setMode('url')}
          className={cn(
            'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-body font-medium transition-all',
            mode === 'url' ? 'bg-white/12 text-white' : 'text-white/40 hover:text-white/70'
          )}
        >
          <Link2 className="w-3 h-3" /> URL
        </button>
        <button
          onClick={() => setMode('jd')}
          className={cn(
            'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-body font-medium transition-all',
            mode === 'jd' ? 'bg-white/12 text-white' : 'text-white/40 hover:text-white/70'
          )}
        >
          <FileText className="w-3 h-3" /> Paste JD
        </button>
      </div>

      <div className="relative">
        {mode === 'url' ? (
          <input
            type="url"
            value={value}
            onChange={e => setValue(e.target.value)}
            onPaste={handlePaste}
            onKeyDown={handleKeyDown}
            placeholder="https://jobs.greenhouse.io/company/12345"
            className="w-full px-4 py-3 pr-10 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/25 font-body text-sm focus:outline-none focus:border-brand-cyan/50 transition-colors"
          />
        ) : (
          <textarea
            ref={textareaRef}
            value={value}
            onChange={e => setValue(e.target.value)}
            onPaste={handlePaste}
            onKeyDown={handleKeyDown}
            rows={8}
            placeholder="Paste the full job description here..."
            className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/25 font-body text-sm focus:outline-none focus:border-brand-cyan/50 transition-colors resize-none"
          />
        )}
        {value && (
          <button
            onClick={() => { setValue(''); setDetectedUrl(false) }}
            className="absolute right-3 top-3 text-white/30 hover:text-white/60"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      <AnimatePresence>
        {detectedUrl && mode === 'url' && (
          <motion.div
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="flex items-center gap-2 mt-2 text-xs text-emerald-300 font-body"
          >
            <CheckCircle className="w-3 h-3" /> Job URL detected — ready to evaluate
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex items-center justify-between mt-4">
        <p className="text-xs text-white/30 font-body">⌘ + Enter to submit</p>
        <button
          onClick={handleSubmit}
          disabled={!value.trim() || isLoading}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-brand text-white text-sm font-body font-medium hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <Zap className="w-4 h-4" />
          {isLoading ? 'Evaluating...' : 'Evaluate'}
        </button>
      </div>
    </GlassCard>
  )
}
