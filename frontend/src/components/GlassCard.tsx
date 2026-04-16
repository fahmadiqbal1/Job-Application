import { cn } from '@/lib/utils'
import type { ReactNode } from 'react'

interface GlassCardProps {
  children: ReactNode
  className?: string
  gradient?: boolean
  onClick?: () => void
  hover?: boolean
}

export function GlassCard({ children, className, gradient, onClick, hover = false }: GlassCardProps) {
  return (
    <div
      onClick={onClick}
      className={cn(
        'relative rounded-2xl border border-white/10 bg-navy-800/60 backdrop-blur-md',
        gradient && 'before:absolute before:inset-0 before:rounded-2xl before:bg-gradient-brand-subtle before:opacity-50 before:-z-10',
        hover && 'cursor-pointer transition-all duration-200 hover:border-white/20 hover:bg-navy-700/60 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-brand-cyan/5',
        className,
      )}
    >
      {children}
    </div>
  )
}
