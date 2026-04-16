import { useState } from 'react'
import { Copy, Check } from 'lucide-react'
import { cn } from '@/lib/utils'

interface MessageCardProps {
  variant: number
  text: string
  charLimit?: number
}

export function MessageCard({ variant, text, charLimit = 300 }: MessageCardProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const over = text.length > charLimit

  return (
    <div className="rounded-xl border border-white/10 bg-white/4 p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-display font-semibold text-white/40 uppercase tracking-wide">
          Variant {variant}
        </span>
        <div className="flex items-center gap-2">
          <span className={cn('text-xs font-body', over ? 'text-red-400' : 'text-white/30')}>
            {text.length}/{charLimit}
          </span>
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 text-xs text-white/40 hover:text-white/80 transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>
      <p className="text-sm font-body text-white/70 leading-relaxed">{text}</p>
    </div>
  )
}
