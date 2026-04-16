import { motion } from 'framer-motion'
import { EvalInput } from './EvalInput'
import { SplitView } from './SplitView'
import { useEvaluation } from '@/hooks/useEvaluation'

export default function EvaluatePage() {
  const { blocks, finalResult, jdText, isRunning, startEvaluation, reset } = useEvaluation()

  const showSplit = isRunning || finalResult !== null

  return (
    <div className="p-8">
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="mb-6"
      >
        <h1 className="text-2xl font-display font-bold text-white">Evaluate Offer</h1>
        <p className="text-sm text-white/40 font-body mt-1">Paste a job URL or description — get a full A–F evaluation</p>
      </motion.div>

      {!showSplit ? (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="max-w-2xl"
        >
          <EvalInput onSubmit={startEvaluation} isLoading={isRunning} />
        </motion.div>
      ) : (
        <SplitView
          jdText={jdText}
          blocks={blocks}
          finalResult={finalResult}
          onReset={reset}
        />
      )}
    </div>
  )
}
