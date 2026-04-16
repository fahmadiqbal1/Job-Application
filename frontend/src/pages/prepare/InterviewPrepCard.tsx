import { GlassCard } from '@/components/GlassCard'
import { StreamingText } from '@/components/StreamingText'
import { Skeleton } from '@/components/Skeleton'

interface InterviewPrepCardProps {
  content: string | null
  isLoading: boolean
}

export function InterviewPrepCard({ content, isLoading }: InterviewPrepCardProps) {
  return (
    <GlassCard className="p-5">
      <h3 className="text-xs font-display font-semibold text-white/50 uppercase tracking-wider mb-3">
        Interview Prep Pack
      </h3>
      {isLoading ? (
        <div className="space-y-2">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-4 rounded" />)}
        </div>
      ) : content ? (
        <StreamingText content={content} isStreaming={false} className="max-h-96 overflow-y-auto text-sm" />
      ) : (
        <p className="text-xs text-white/25 font-body text-center py-6">
          Enter company and role, then click Prepare
        </p>
      )}
    </GlassCard>
  )
}
