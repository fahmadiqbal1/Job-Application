import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '@/lib/api'

export const useApplications = (filters?: { status?: string; min_score?: number; limit?: number }) =>
  useQuery({
    queryKey: ['applications', filters],
    queryFn: () => api.getApplications(filters),
    staleTime: 30_000,
  })

export const useTrackerStats = () =>
  useQuery({ queryKey: ['tracker-stats'], queryFn: api.getTrackerStats, staleTime: 60_000 })

export const useTrackerFunnel = () =>
  useQuery({ queryKey: ['tracker-funnel'], queryFn: api.getTrackerFunnel, staleTime: 60_000 })

export const useScoreTrends = () =>
  useQuery({ queryKey: ['score-trends'], queryFn: api.getScoreTrends, staleTime: 120_000 })

export const useUpdateStatus = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ num, status }: { num: number; status: string }) => api.updateStatus(num, status),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['applications'] }); qc.invalidateQueries({ queryKey: ['tracker-stats'] }) },
  })
}

export const useUpdateNotes = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ num, notes }: { num: number; notes: string }) => api.updateNotes(num, notes),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['applications'] }),
  })
}
