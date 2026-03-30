import { useState, useCallback } from 'react'

/**
 * Custom hook for API calls with error handling.
 */
export function useApi() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const apiCall = useCallback(async (method, path, body = null) => {
    setLoading(true)
    setError(null)

    try {
      const options = {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
      }

      if (body) {
        options.body = JSON.stringify(body)
      }

      const response = await fetch(path, options)

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`${response.status}: ${errorText}`)
      }

      const data = await response.json()
      return { data, error: null }
    } catch (err) {
      setError(err.message)
      return { data: null, error: err.message }
    } finally {
      setLoading(false)
    }
  }, [])

  const get = useCallback((path) => apiCall('GET', path), [apiCall])
  const post = useCallback((path, body) => apiCall('POST', path, body), [apiCall])
  const put = useCallback((path, body) => apiCall('PUT', path, body), [apiCall])
  const del = useCallback((path) => apiCall('DELETE', path), [apiCall])

  return {
    get,
    post,
    put,
    del,
    loading,
    error,
  }
}
