import { GlassCard } from '@/components/GlassCard'
import { Skeleton } from '@/components/Skeleton'

interface CVPreviewProps {
  html: string | null
  isLoading: boolean
}

export function CVPreview({ html, isLoading }: CVPreviewProps) {
  return (
    <GlassCard className="p-5 h-full min-h-96">
      <h3 className="text-xs font-display font-semibold text-white/50 uppercase tracking-wider mb-3">Preview</h3>
      {isLoading ? (
        <Skeleton className="w-full h-96 rounded-lg" />
      ) : html ? (
        <iframe
          srcDoc={html}
          title="CV Preview"
          className="w-full h-[70vh] rounded-lg border border-white/8 bg-white"
          sandbox="allow-same-origin"
        />
      ) : (
        <div className="flex items-center justify-center h-64 text-sm text-white/20 font-body">
          Extract keywords and click Preview to see your tailored CV
        </div>
      )}
    </GlassCard>
  )
}
