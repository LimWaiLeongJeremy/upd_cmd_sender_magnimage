/**
 * AbsoluteControl.jsx
 * --------------------
 * Section 2: IP dropdown (fetched from API) + brightness input + send button.
 * IPs are grouped by device group in the dropdown for easy navigation.
 */
import { useState } from 'react'

export default function AbsoluteControl({ devices, loading, error, onSend, sending }) {
  const [selectedIp,  setSelectedIp]  = useState('')
  const [brightness,  setBrightness]  = useState(50)
  const [localError,  setLocalError]  = useState(null)
  const [localStatus, setLocalStatus] = useState(null) // null | 'success' | 'error'

  async function handleSend() {
    if (!selectedIp) { setLocalError('Select a device first.'); return }
    if (brightness < 0 || brightness > 100) { setLocalError('Brightness must be 0–100.'); return }
    setLocalError(null)
    setLocalStatus(null)

    const result = await onSend(selectedIp, brightness)
    setLocalStatus(result.error ? 'error' : 'success')
    setTimeout(() => setLocalStatus(null), 3000)
  }

  if (loading) return <p className="panel-placeholder">Loading devices…</p>
  if (error)   return <p className="panel-error">Failed to load devices: {error}</p>

  // Group devices by "group (role)" for dropdown optgroups
  const byGroup = devices.reduce((acc, d) => {
    const key = `${d.group} — ${d.role}`
    if (!acc[key]) acc[key] = []
    acc[key].push(d)
    return acc
  }, {})

  return (
    <div className="absolute-control">

      <div className="control-field">
        <label className="field-label">Target Device</label>
        <select
          className="field-select"
          value={selectedIp}
          onChange={(e) => setSelectedIp(e.target.value)}
        >
          <option value="">— Select IP address —</option>
          {Object.entries(byGroup).map(([groupLabel, devs]) => (
            <optgroup key={groupLabel} label={groupLabel}>
              {devs.map((d) => (
                <option key={d.ip} value={d.ip}>{d.ip}</option>
              ))}
            </optgroup>
          ))}
        </select>
      </div>

      <div className="control-field">
        <label className="field-label">Brightness %</label>
        <input
          type="number"
          min={0}
          max={100}
          value={brightness}
          onChange={(e) => setBrightness(Number(e.target.value))}
          className="field-number"
        />
        <div className="brightness-bar-track">
          <div className="brightness-bar-fill" style={{ width: `${Math.max(0, Math.min(100, brightness))}%` }} />
        </div>
      </div>

      {localError && <p className="field-error">{localError}</p>}

      <button
        className={`send-btn ${localStatus ?? ''}`}
        onClick={handleSend}
        disabled={sending || !selectedIp}
      >
        {localStatus === 'success' ? '✓ Sent' :
         localStatus === 'error'   ? '✗ Failed' :
         sending                   ? '● Sending…' :
         'Set Brightness'}
      </button>

    </div>
  )
}
