import { useState, useCallback, useRef } from 'react'
import { useMutation } from '@tanstack/react-query'
import { createEvalStream, type EvalStreamEvent } from '@/lib/websocket'
import { compareOffers } from '@/lib/api'

export interface BlockState {
  phase: string
  label: string
  content: string
  status: 'pending' | 'streaming' | 'done'
}

const BLOCK_LABELS: Record<string, string> = {
  A: 'Role Summary',
  B: 'CV Match',
  C: 'Level & Strategy',
  D: 'Comp & Market',
  E: 'Personalization Plan',
  F: 'Interview Prep',
}

const INITIAL_BLOCKS: BlockState[] = Object.entries(BLOCK_LABELS).map(([phase, label]) => ({
  phase, label, content: '', status: 'pending' as const,
}))

export interface EvalFinalState {
  score: number
  archetype: string
  report_id: string
  company: string
  role: string
  keywords: string[]
}

export function useEvaluation() {
  const [isRunning, setIsRunning] = useState(false)
  const [blocks, setBlocks] = useState<BlockState[]>(INITIAL_BLOCKS)
  const [finalResult, setFinalResult] = useState<EvalFinalState | null>(null)
  const [jdText, setJdText] = useState('')
  const [error, setError] = useState<string | null>(null)
  const closeRef = useRef<(() => void) | null>(null)

  const startEvaluation = useCallback((input: string, _isUrl: boolean) => {
    setIsRunning(true)
    setError(null)
    setFinalResult(null)
    setJdText('')
    setBlocks(INITIAL_BLOCKS.map(b => ({ ...b, content: '', status: 'pending' })))

    const cleanup = createEvalStream(
      input,
      (event: EvalStreamEvent) => {
        if (event.phase === 'jd') {
          setJdText(event.content ?? '')
          return
        }
        if (event.phase === 'score') {
          setFinalResult({
            score: event.score ?? 0,
            archetype: event.archetype ?? '',
            report_id: event.report_id ?? '',
            company: event.company ?? '',
            role: event.role ?? '',
            keywords: event.keywords ?? [],
          })
          setIsRunning(false)
          return
        }
        const phase = event.phase.toUpperCase()
        if (!BLOCK_LABELS[phase]) return
        setBlocks(prev => prev.map(b => {
          if (b.phase !== phase) return b
          if (event.done) return { ...b, status: 'done' }
          return { ...b, status: 'streaming', content: b.content + (event.content ?? '') }
        }))
      },
      () => setIsRunning(false),
      (err) => { setError(err); setIsRunning(false) },
    )
    closeRef.current = cleanup
  }, [])

  const cancel = useCallback(() => {
    closeRef.current?.()
    setIsRunning(false)
  }, [])

  const reset = useCallback(() => {
    cancel()
    setBlocks(INITIAL_BLOCKS.map(b => ({ ...b, content: '', status: 'pending' })))
    setFinalResult(null)
    setJdText('')
    setError(null)
  }, [cancel])

  return { isRunning, blocks, finalResult, jdText, error, startEvaluation, reset }
}

export function useCompareOffers() {
  return useMutation({
    mutationFn: (reportIds: string[]) => compareOffers(reportIds),
  })
}
