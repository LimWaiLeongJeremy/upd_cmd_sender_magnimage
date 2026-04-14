import { useState } from 'react'

const DEFAULT_PARAMS = {
  startBrightness: 0,
  endBrightness: 100,
  step: 5,
  intervalSeconds: 0.3,
}

export default function GlobalRampPanel({ selectedGroups, rampInFlight, onRun, onSelectAll, onClearAll }) {
  const [params, setParams] = useState(DEFAULT_PARAMS)
  const isRunning = rampInFlight.current
  const hasSelection = selectedGroups.length > 0

  function handleChange(field, value) {
    const num = Number(value)
    if (!isNaN(num)) setParams((prev) => ({ ...prev, [field]: num }))
  }

  function handleSubmit() {
    if (!hasSelection || isRunning) return
    onRun({ groups: selectedGroups, ...params })
  }

  const steps = Math.abs(params.endBrightness - params.startBrightness) / (params.step || 1)
  const estimatedSeconds = Math.ceil(steps * params.intervalSeconds)

  return (
    <div className="ramp-panel">
      <div className="ramp-panel-header">
        <h2 className="panel-title">Group Ramp</h2>
        <div className="selection-controls">
          <button className="text-btn" onClick={onSelectAll}>Select all</button>
          <span className="divider">·</span>
          <button className="text-btn" onClick={onClearAll}>Clear</button>
        </div>
      </div>

      <div className="selected-groups-row">
        {hasSelection
          ? selectedGroups.map((g) => <span key={g} className="group-pill">{g}</span>)
          : <span className="no-selection-hint">Select groups on the cards above</span>
        }
      </div>

      <div className="ramp-params">
        <label className="param-field">
          <span className="param-label">Start %</span>
          <input type="number" min="0" max="100" value={params.startBrightness}
            onChange={(e) => handleChange('startBrightness', e.target.value)} className="param-input" />
        </label>

        <span className="param-arrow">→</span>

        <label className="param-field">
          <span className="param-label">End %</span>
          <input type="number" min="0" max="100" value={params.endBrightness}
            onChange={(e) => handleChange('endBrightness', e.target.value)} className="param-input" />
        </label>

        <label className="param-field">
          <span className="param-label">Step</span>
          <input type="number" min="1" max="100" value={params.step}
            onChange={(e) => handleChange('step', e.target.value)} className="param-input" />
        </label>

        <label className="param-field">
          <span className="param-label">Interval (s)</span>
          <input type="number" min="0" step="0.1" value={params.intervalSeconds}
            onChange={(e) => handleChange('intervalSeconds', e.target.value)} className="param-input" />
        </label>
      </div>

      <div className="ramp-footer">
        <span className="estimate">
          ~{estimatedSeconds}s · <strong>{selectedGroups.length}</strong> group{selectedGroups.length !== 1 ? 's' : ''}
        </span>
        <button className="run-btn" disabled={!hasSelection || isRunning} onClick={handleSubmit}>
          {isRunning ? <span className="spinner-text">● Running…</span> : 'Run Ramp'}
        </button>
      </div>
    </div>
  )
}
