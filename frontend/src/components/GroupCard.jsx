/**
 * Displays one group's status and provides a brightness slider.
 *
 * PROPS:
 *   group       — { id, label, ipCount }
 *   state       — { brightness, status, error, lastUpdated }
 *   onSet       — (groupId, brightness) => void
 *   isSelected  — bool
 *   onToggleSelect — () => void
 */

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
  // Local slider value — only committed to API on mouse release
  const [localValue, setLocalValue] = useState(state.brightness ?? 0)
  const isLoading = state.status === 'loading'

  // Sync local slider when remote state changes (e.g. after a global ramp)
  // Only sync if the card isn't being actively dragged
  const displayBrightness = state.brightness ?? localValue

  function handleSliderChange(e) {
    setLocalValue(Number(e.target.value))
  }

  function handleSliderCommit(e) {
    const value = Number(e.target.value)
    setLocalValue(value)
    onSet(group.id, value)
  }

  const statusColor = STATUS_COLORS[state.status] ?? STATUS_COLORS.idle

  return (
    <div
      className={`group-card ${isSelected ? 'selected' : ''} ${state.status}`}
      style={{ '--status-color': statusColor }}
    >
      {/* Header */}
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

      {/* Brightness display */}
      <div className="brightness-display">
        <span className="brightness-value">
          {displayBrightness.toString().padStart(3, '0')}
        </span>
        <span className="brightness-unit">%</span>
      </div>

      {/* Visual bar */}
      <div className="brightness-bar-track">
        <div
          className="brightness-bar-fill"
          style={{ width: `${displayBrightness}%` }}
        />
      </div>

      {/* Slider */}
      <input
        type="range"
        min="0"
        max="100"
        step="1"
        value={localValue}
        disabled={isLoading}
        onChange={handleSliderChange}
        onMouseUp={handleSliderCommit}
        onTouchEnd={handleSliderCommit}
        className="brightness-slider"
        aria-label={`${group.label} brightness`}
      />

      {/* Footer: last updated + select toggle */}
      <div className="card-footer">
        <span className="last-updated">
          {state.lastUpdated
            ? `Updated ${formatTime(state.lastUpdated)}`
            : 'Not yet set'}
        </span>
        <button
          className={`select-btn ${isSelected ? 'active' : ''}`}
          onClick={onToggleSelect}
          title={isSelected ? 'Remove from group ramp' : 'Add to group ramp'}
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
