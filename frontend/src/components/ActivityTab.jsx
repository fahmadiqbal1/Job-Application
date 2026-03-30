import { usePipeline } from '../context/PipelineContext'
import { BrowserStream } from './BrowserStream'

export function ActivityTab() {
  const { browserFrame, actionLog } = usePipeline()

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 h-full">
      {/* Browser Stream - 60% */}
      <div className="lg:col-span-2">
        <div className="bg-zinc-800 border border-zinc-700 rounded-lg overflow-hidden h-full flex flex-col">
          <BrowserStream frame={browserFrame} />
        </div>
      </div>

      {/* Action Log - 40% */}
      <div className="bg-zinc-800 border border-zinc-700 rounded-lg p-4 flex flex-col h-full">
        <h3 className="text-sm font-bold text-zinc-300 mb-3">Action Log</h3>
        <div className="flex-1 overflow-y-auto space-y-2">
          {actionLog.length === 0 ? (
            <p className="text-xs text-zinc-500">Waiting for activity...</p>
          ) : (
            actionLog.map((entry, idx) => (
              <div key={idx} className="text-xs text-zinc-400 border-l border-zinc-700 pl-2 py-1">
                <span className="text-zinc-500">{entry.timestamp}</span>
                <p className="text-zinc-300">{entry.action}</p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
