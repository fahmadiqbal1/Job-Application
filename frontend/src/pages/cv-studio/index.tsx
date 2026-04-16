import { useState } from 'react'
import { useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { GlassCard } from '@/components/GlassCard'
import { JDInput } from './JDInput'
import { KeywordPanel } from './KeywordPanel'
import { CVPreview } from './CVPreview'
import { GeneratePanel } from './GeneratePanel'
import { useExtractKeywords, useGenerateCV, usePreviewCV } from '@/hooks/useCVStudio'

export default function CVStudioPage() {
  const location = useLocation()
  const [jdText, setJdText] = useState('')
  const { mutate: extract, data: keywords, isPending: extracting } = useExtractKeywords()
  const { mutate: preview, data: previewHtml, isPending: previewing } = usePreviewCV()
  const { mutate: generate, data: cvResult, isPending: generating } = useGenerateCV()

  const handleExtract = (text: string) => {
    setJdText(text)
    extract({ jd_text: text })
  }

  const handlePreview = () => {
    if (!jdText) return
    preview({ jd_text: jdText, report_id: location.state?.report_id })
  }

  const handleGenerate = (format: 'A4' | 'Letter') => {
    generate({ jd_text: jdText, format, report_id: location.state?.report_id })
  }

  return (
    <div className="p-8">
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className="mb-6">
        <h1 className="text-2xl font-display font-bold text-white">CV Studio</h1>
        <p className="text-sm text-white/40 font-body mt-1">Generate a tailored CV from any job description</p>
      </motion.div>

      <div className="grid grid-cols-2 gap-4">
        {/* Left column */}
        <div className="space-y-4">
          <JDInput onExtract={handleExtract} isLoading={extracting} />
          {keywords && keywords.length > 0 && (
            <KeywordPanel keywords={keywords} onPreview={handlePreview} isPreviewing={previewing} />
          )}
          <GeneratePanel onGenerate={handleGenerate} isGenerating={generating} result={cvResult} />
        </div>
        {/* Right column */}
        <CVPreview html={previewHtml ?? null} isLoading={previewing} />
      </div>
    </div>
  )
}
