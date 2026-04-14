export default function CommandLog({ entries }) {
  if (entries.length === 0) {
    return (
      <div className="command-log empty">
        <span className="log-empty-text">No commands sent yet this session</span>
      </div>
    )
  }

  return (
    <div className="command-log">
      <div className="log-entries">
        {entries.map((entry) => (
          <div key={entry.id} className={`log-entry ${entry.status}`}>
            <span className="log-time">{formatTime(entry.timestamp)}</span>
            <span className="log-indicator">{entry.status === 'success' ? '✓' : '✗'}</span>
            <span className="log-description">
              {entry.type === 'absolute'
                ? `${entry.ip} → ${entry.brightness}%`
                : `[${entry.groups?.join(', ')}] ${entry.startBrightness}% → ${entry.endBrightness}%`}
            </span>
            {entry.status === 'error' && (
              <span className="log-error">{entry.message}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}
