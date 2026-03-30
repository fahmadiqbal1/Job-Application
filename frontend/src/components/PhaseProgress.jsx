export function PhaseProgress({ phase, phaseDetail }) {
  const phases = [
    { id: 'scraping', label: 'Scrape' },
    { id: 'ats', label: 'ATS' },
    { id: 'cover_letter', label: 'Cover' },
    { id: 'applying', label: 'Apply' },
    { id: 'notifying', label: 'Done' },
  ]

  const currentIndex = phases.findIndex((p) => p.id === phase)

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-2">
        {phases.map((p, idx) => (
          <div key={p.id} className="flex items-center flex-1">
            {/* Circle */}
            <div
              className={`
                w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm
                ${
                  idx < currentIndex
                    ? 'bg-green-600 text-white'
                    : idx === currentIndex
                      ? 'bg-blue-600 text-white animate-pulse'
                      : 'bg-zinc-700 text-zinc-400'
                }
              `}
            >
              {idx < currentIndex ? '✓' : idx + 1}
            </div>

            {/* Connector line */}
            {idx < phases.length - 1 && (
              <div
                className={`
                  flex-1 h-1 mx-1
                  ${idx < currentIndex ? 'bg-green-600' : 'bg-zinc-700'}
                `}
              />
            )}
          </div>
        ))}
      </div>

      {/* Phase labels */}
      <div className="flex justify-between text-xs text-zinc-400 px-1">
        {phases.map((p) => (
          <span key={p.id}>{p.label}</span>
        ))}
      </div>

      {/* Current phase detail */}
      {phaseDetail && (
        <div className="text-sm text-zinc-300 bg-zinc-800 px-3 py-2 rounded">
          {phaseDetail}
        </div>
      )}
    </div>
  )
}
