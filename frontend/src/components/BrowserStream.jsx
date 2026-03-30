export function BrowserStream({ frame }) {
  return (
    <div className="w-full h-full flex flex-col bg-zinc-900">
      {frame?.data ? (
        <>
          <img
            src={`data:image/jpeg;base64,${frame.data}`}
            alt="Browser stream"
            className="flex-1 object-contain bg-black"
          />
          <div className="bg-zinc-800 border-t border-zinc-700 p-3 space-y-1">
            <div className="text-xs text-zinc-500">Current URL</div>
            <div className="text-sm text-zinc-300 truncate font-mono">{frame.url}</div>
            {frame.action && (
              <>
                <div className="text-xs text-zinc-500 mt-2">Action</div>
                <div className="text-sm text-zinc-300">{frame.action}</div>
              </>
            )}
          </div>
        </>
      ) : (
        <div className="flex-1 flex items-center justify-center text-zinc-500">
          <div className="text-center">
            <p className="mb-2">Waiting for browser activity...</p>
            <p className="text-sm text-zinc-600">
              Screenshots will appear here (1 FPS)
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
