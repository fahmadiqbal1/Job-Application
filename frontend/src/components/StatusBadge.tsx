import { cn } from '@/lib/utils'

const STATUS_STYLES: Record<string, string> = {
  Evaluated: 'bg-sky-400/15 text-sky-300 border-sky-400/30',
  Applied: 'bg-blue-400/15 text-blue-300 border-blue-400/30',
  Responded: 'bg-violet-400/15 text-violet-300 border-violet-400/30',
  Interview: 'bg-amber-400/15 text-amber-300 border-amber-400/30',
  Offer: 'bg-emerald-400/15 text-emerald-300 border-emerald-400/30',
  Rejected: 'bg-red-400/15 text-red-300 border-red-400/30',
  Discarded: 'bg-zinc-400/15 text-zinc-400 border-zinc-400/30',
  SKIP: 'bg-zinc-600/15 text-zinc-500 border-zinc-600/30',
}

export function StatusBadge({ status, className }: { status: string; className?: string }) {
  const style = STATUS_STYLES[status] ?? 'bg-zinc-400/15 text-zinc-400 border-zinc-400/30'
  return (
    <span className={cn('inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium font-body', style, className)}>
      {status}
    </span>
  )
}
