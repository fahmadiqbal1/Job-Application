/** Shared utility functions */

export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ')
}

export function formatScore(score: string | number): string {
  if (typeof score === 'string') {
    const m = score.match(/([\d.]+)\/5/)
    if (m) return m[1]
    return score
  }
  return score.toFixed(1)
}

export function scoreColor(score: number): string {
  if (score >= 4.5) return 'text-emerald-400'
  if (score >= 3.5) return 'text-amber-400'
  if (score >= 2.5) return 'text-orange-400'
  return 'text-red-400'
}

export function scoreBg(score: number): string {
  if (score >= 4.5) return 'bg-emerald-400/20 text-emerald-300 border-emerald-400/30'
  if (score >= 3.5) return 'bg-amber-400/20 text-amber-300 border-amber-400/30'
  if (score >= 2.5) return 'bg-orange-400/20 text-orange-300 border-orange-400/30'
  return 'bg-red-400/20 text-red-300 border-red-400/30'
}

export function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  try {
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  } catch {
    return dateStr
  }
}

export function daysSince(dateStr: string): number {
  if (!dateStr) return 0
  const diff = Date.now() - new Date(dateStr).getTime()
  return Math.floor(diff / (1000 * 60 * 60 * 24))
}

export function slugify(text: string): string {
  return text.toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-').slice(0, 30)
}
