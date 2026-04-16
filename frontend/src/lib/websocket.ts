/** Singleton WebSocket manager with event bus */

type EventHandler = (data: unknown) => void
type EventType = 'evaluation' | 'scan' | 'pipeline' | 'status' | string

class WSManager {
  private ws: WebSocket | null = null
  private url: string = ''
  private handlers: Map<EventType, Set<EventHandler>> = new Map()
  private reconnectTimeout: number | null = null

  connect(url: string) {
    this.url = url
    this._open()
  }

  private _open() {
    if (this.ws?.readyState === WebSocket.OPEN) return
    try {
      this.ws = new WebSocket(this.url)
      this.ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data)
          const type = data.type || 'status'
          this.handlers.get(type)?.forEach(h => h(data))
          this.handlers.get('*')?.forEach(h => h(data))
        } catch {}
      }
      this.ws.onclose = () => {
        this.reconnectTimeout = window.setTimeout(() => this._open(), 3000)
      }
    } catch {}
  }

  on(event: EventType, handler: EventHandler) {
    if (!this.handlers.has(event)) this.handlers.set(event, new Set())
    this.handlers.get(event)!.add(handler)
    return () => this.handlers.get(event)?.delete(handler)
  }

  disconnect() {
    if (this.reconnectTimeout) clearTimeout(this.reconnectTimeout)
    this.ws?.close()
    this.ws = null
  }
}

export const wsManager = new WSManager()

/** Create a dedicated evaluation WebSocket stream */
export function createEvalStream(
  input: string,
  onEvent: (event: EvalStreamEvent) => void,
  onComplete: () => void,
  onError: (err: string) => void,
): () => void {
  const wsBase = window.location.origin.replace('http', 'ws')
  const ws = new WebSocket(`${wsBase}/api/v2/evaluate/stream`)

  ws.onopen = () => {
    ws.send(JSON.stringify({ input, input_type: 'auto', generate_pdf: false, draft_answers: false }))
  }

  ws.onmessage = (e) => {
    try {
      const event: EvalStreamEvent = JSON.parse(e.data)
      if (event.phase === 'error') {
        onError(event.error || 'Unknown error')
        ws.close()
        return
      }
      onEvent(event)
      if (event.done && event.phase === 'score') {
        onComplete()
        ws.close()
      }
    } catch {}
  }

  ws.onerror = () => onError('WebSocket connection failed')

  return () => ws.close()
}

export interface EvalStreamEvent {
  phase: string
  content?: string
  done?: boolean
  score?: number
  archetype?: string
  report_id?: string
  company?: string
  role?: string
  keywords?: string[]
  pdf_path?: string | null
  error?: string
}
