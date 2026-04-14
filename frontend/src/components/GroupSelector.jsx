/**
 * GroupSelector.jsx
 * ------------------
 * Section 1: Group toggle buttons + ramp controls.
 * Select groups, set parameters, hit Run.
 */
import { useState } from 'react'

const DEFAULT_PARAMS = {
  startBrightness: 0,
  endBrightness: 100,
  step: 5,
  intervalSeconds: 0.3,
}

export default function GroupSelector({ groups, selected, onToggle, onRun, sending, loading, error }) {
  const [params, setParams] = useState(DEFAULT_PARAMS)
  const [localStatus, setLocalStatus] = useState(null) // null | 'success' | 'error'
  const [localError, setLocalError] = useState(null)

  function handleChange(field, value) {
    const num = Number(value)
    if (!isNaN(num)) setParams((prev) => ({ ...prev, [field]: num }))
  }

  async function handleRun() {
    if (selected.length === 0) { setLocalError('Select at least one group.'); return }
    if (params.step < 1) { setLocalError('Step must be at least 1.'); return }
    if (params.intervalSeconds < 0) { setLocalError('Interval must be 0 or more.'); return }
    setLocalError(null)
    setLocalStatus(null)

    const result = await onRun({
      groups: selected,
      startBrightness: params.startBrightness,
      endBrightness: params.endBrightness,
      step: params.step,
      intervalSeconds: params.intervalSeconds,
    })

    setLocalStatus(result.error ? 'error' : 'success')
    setTimeout(() => setLocalStatus(null), 3000)
  }

  // Estimate how long the ramp will take
  const steps = params.step > 0
    ? Math.abs(params.endBrightness - params.startBrightness) / params.step
    : 0
  const estimatedSeconds = Math.ceil(steps * params.intervalSeconds)

  if (loading) return <p className="panel-placeholder">Loading groups…</p>
  if (error)   return <p className="panel-error">Failed to load groups: {error}</p>

  return (
    <div className="group-selector">

      {/* ── Group toggle buttons ── */}
      <div className="group-btn-grid">
        {groups.map((g) => (
          <button
            key={g}
            className={`group-btn ${selected.includes(g) ? 'active' : ''}`}
            onClick={() => onToggle(g)}
          >
            {g}
          </button>
        ))}
      </div>

      {/* ── Ramp parameters ── */}
      <div className="ramp-section">
        <p className="ramp-section-label">Ramp parameters</p>

        <div className="ramp-params">
          <div className="control-field">
            <label className="field-label">Start %</label>
            <input
              type="number" min={0} max={100}
              value={params.startBrightness}
              onChange={(e) => handleChange('startBrightness', e.target.value)}
              className="param-input"
            />
          </div>

          <div className="param-arrow-col">
            <span className="param-arrow">→</span>
          </div>

          <div className="control-field">
            <label className="field-label">End %</label>
            <input
              type="number" min={0} max={100}
              value={params.endBrightness}
              onChange={(e) => handleChange('endBrightness', e.target.value)}
              className="param-input"
            />
          </div>

          <div className="control-field">
            <label className="field-label">Step</label>
            <input
              type="number" min={1} max={100}
              value={params.step}
              onChange={(e) => handleChange('step', e.target.value)}
              className="param-input"
            />
          </div>

          <div className="control-field">
            <label className="field-label">Interval (s)</label>
            <input
              type="number" min={0} step={0.1}
              value={params.intervalSeconds}
              onChange={(e) => handleChange('intervalSeconds', e.target.value)}
              className="param-input"
            />
          </div>
        </div>

        <div className="ramp-estimate">
          ~{estimatedSeconds}s · {selected.length} group{selected.length !== 1 ? 's' : ''} selected
        </div>

        {localError && <p className="field-error">{localError}</p>}

        <button
          className={`send-btn ${localStatus ?? ''}`}
          onClick={handleRun}
          disabled={sending || selected.length === 0}
        >
          {localStatus === 'success' ? '✓ Done' :
           localStatus === 'error'   ? '✗ Failed' :
           sending                   ? '● Running…' :
           'Run Ramp'}
        </button>
      </div>

    </div>
  )
}
