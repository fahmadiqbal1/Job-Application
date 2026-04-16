import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { startScan, getScanStatus, getScanResults, addToPipeline, getPipeline } from '@/lib/api'
import type { ScanResult, ScanJobStatus } from '@/lib/api'

export function useStartScan() {
  return useMutation({
    mutationFn: (levels?: string[]) => startScan(levels),
  })
}

export function useScanStatus(jobId: string | null) {
  return useQuery({
    queryKey: ['scan-status', jobId],
    queryFn: () => getScanStatus(jobId!),
    enabled: !!jobId,
    refetchInterval: (query) => {
      const status = query.state.data?.status
      return status === 'running' ? 2000 : false
    },
  })
}

export function useScanResults() {
  return useQuery({
    queryKey: ['scan-results'],
    queryFn: () => getScanResults().then(r => r.results),
  })
}

export function usePipeline() {
  return useQuery({
    queryKey: ['pipeline'],
    queryFn: () => getPipeline().then(r => r.pending),
  })
}

export function useAddToPipeline() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (req: { url: string; company: string; title: string }) =>
      addToPipeline(req.url, req.company, req.title),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['pipeline'] }),
  })
}

export { ScanResult, ScanJobStatus }
