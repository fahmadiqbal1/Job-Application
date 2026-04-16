import { useEffect, useRef } from 'react'
import { cn } from '@/lib/utils'

interface StreamingTextProps {
  content: string
  isStreaming?: boolean
  className?: string
}

export function StreamingText({ content, isStreaming = false, className }: StreamingTextProps) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isStreaming && ref.current) {
      ref.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [content, isStreaming])

  return (
    <div ref={ref} className={cn('whitespace-pre-wrap font-body text-sm text-white/80 leading-relaxed', className)}>
      {content}
      {isStreaming && (
        <span className="inline-block w-0.5 h-4 ml-0.5 bg-brand-cyan-light animate-pulse align-middle" />
      )}
    </div>
  )
}
