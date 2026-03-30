export function StatusBadge({ status }) {
  const styles = {
    applied: 'bg-green-900/30 text-green-400',
    skipped: 'bg-zinc-700 text-zinc-300',
    pending: 'bg-blue-900/30 text-blue-400',
    confirmed: 'bg-blue-900/30 text-blue-400',
    cover_written: 'bg-yellow-900/30 text-yellow-400',
    failed: 'bg-red-900/30 text-red-400',
  }

  const labels = {
    applied: 'Applied',
    skipped: 'Skipped',
    pending: 'Pending',
    confirmed: 'Confirmed',
    cover_written: 'Cover Written',
    failed: 'Failed',
  }

  const style = styles[status] || styles.pending
  const label = labels[status] || status

  return (
    <span className={`px-2 py-1 rounded text-sm font-medium ${style}`}>
      {label}
    </span>
  )
}
