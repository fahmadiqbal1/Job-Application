import { useMutation } from '@tanstack/react-query'
import { generateCV, previewCV } from '@/lib/api'

export function useExtractKeywords() {
  return useMutation({
    mutationFn: async (req: { jd_text: string }): Promise<string[]> => {
      // Preview returns HTML but we need keywords — call generate with a flag
      const result = await generateCV({ jd_text: req.jd_text })
      return result.keywords_injected ?? []
    },
  })
}

export function usePreviewCV() {
  return useMutation({
    mutationFn: (req: { jd_text: string; report_id?: string }) =>
      previewCV({ jd_text: req.jd_text, report_id: req.report_id }),
  })
}

export function useGenerateCV() {
  return useMutation({
    mutationFn: (req: { jd_text: string; format: 'A4' | 'Letter'; report_id?: string }) =>
      generateCV({ jd_text: req.jd_text, format: req.format, report_id: req.report_id }),
  })
}
