import { useEffect, useRef } from 'react'

/**
 * Custom hook for WebSocket connection with auto-reconnect.
 *
 * @param {string} path - WebSocket path (e.g., '/api/ws/status')
 * @param {function} onMessage - Callback when message received
 * @param {boolean} enabled - Whether to connect (default: true)
 */
export function useWebSocket(path, onMessage, enabled = true) {
  const wsRef = useRef(null)
  const retriesRef = useRef(0)
  const maxRetriesRef = useRef(5)
  const onMessageRef = useRef(onMessage)

  // Update callback ref without retriggering effect
  useEffect(() => {
    onMessageRef.current = onMessage
  }, [onMessage])

  useEffect(() => {
    if (!enabled) return

    const connect = () => {
      try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const wsUrl = `${protocol}//${window.location.host}${path}`
        const ws = new WebSocket(wsUrl)

        ws.onopen = () => {
          console.log(`✓ WebSocket connected: ${path}`)
          retriesRef.current = 0
        }

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            if (onMessageRef.current) {
              onMessageRef.current(data)
            }
          } catch (e) {
            console.debug('WebSocket message not JSON:', event.data)
          }
        }

        ws.onerror = (error) => {
          console.error('WebSocket error:', error)
        }

        ws.onclose = () => {
          console.log('WebSocket disconnected, attempting reconnect...')
          wsRef.current = null

          // Exponential backoff: 1s → 2s → 4s → 8s → 16s → 30s max
          if (retriesRef.current < maxRetriesRef.current) {
            const delay = Math.min(1000 * Math.pow(2, retriesRef.current), 30000)
            retriesRef.current++
            setTimeout(connect, delay)
          }
        }

        wsRef.current = ws
      } catch (error) {
        console.error('WebSocket connection error:', error)
      }
    }

    connect()

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [path, enabled])

  return wsRef.current
}
