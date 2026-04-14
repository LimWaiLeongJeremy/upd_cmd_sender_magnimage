import { useState } from 'react'

const STATUS_COLORS = {
  idle:    'var(--c-border)',
  loading: 'var(--c-amber)',
  success: 'var(--c-green)',
  error:   'var(--c-red)',
}

const STATUS_LABELS = {
  idle:    '',
  loading: 'Sending…',
  success: 'Sent',
  error:   'Failed',
}

export default function GroupCard({ group, state, onSet, isSelected, onToggleSelect }) {
  const [localValue, setLocalValue] = useState(state.brightness ?? 0)
  const isLoading = state.status === 'loading'
  const displayBrightness = state.brightness ?? localValue
  const statusColor = STATUS_COLORS[state.status] ?? STATUS_COLORS.idle

  function handleSliderChange(e) {
    setLocalValue(Number(e.target.value))
  }

  function handleSliderCommit(e) {
    const value = Number(e.target.value)
    setLocalValue(value)
    onSet(group.id, value)
  }

  return (
    <div
      className={`group-card ${isSelected ? 'selected' : ''} ${state.status}`}
      style={{ '--status-color': statusColor }}
    >
      <div className="card-header">
        <div className="card-title-row">
          <span className="card-label">{group.label}</span>
          <span className="card-id">{group.id}</span>
        </div>
        <div className="card-meta">
          <span className="ip-count">{group.ipCount} device{group.ipCount !== 1 ? 's' : ''}</span>
          {state.status !== 'idle' && (
            <span className="status-badge" style={{ color: statusColor }}>
              {STATUS_LABELS[state.status]}
              {state.status === 'error' && state.error && ` — ${state.error}`}
            </span>
          )}
        </div>
      </div>

      <div className="brightness-display">
        <span className="brightness-value">
          {displayBrightness.toString().padStart(3, '0')}
        </span>
        <span className="brightness-unit">%</span>
      </div>

      <div className="brightness-bar-track">
        <div className="brightness-bar-fill" style={{ width: `${displayBrightness}%` }} />
      </div>

      <input
        type="range"
        min="0" max="100" step="1"
        value={localValue}
        disabled={isLoading}
        onChange={handleSliderChange}
        onMouseUp={handleSliderCommit}
        onTouchEnd={handleSliderCommit}
        className="brightness-slider"
        aria-label={`${group.label} brightness`}
      />

      <div className="card-footer">
        <span className="last-updated">
          {state.lastUpdated ? `Updated ${formatTime(state.lastUpdated)}` : 'Not yet set'}
        </span>
        <button
          className={`select-btn ${isSelected ? 'active' : ''}`}
          onClick={onToggleSelect}
          title={isSelected ? 'Remove from ramp' : 'Add to ramp'}
        >
          {isSelected ? '✓ Selected' : '+ Select'}
        </button>
      </div>
    </div>
  )
}

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}
