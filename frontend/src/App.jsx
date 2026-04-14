/**
 * App.jsx
 * --------
 * Root layout. 3 sections side by side:
 *   1. Groups   — toggle buttons + ramp controls
 *   2. Absolute — IP dropdown + brightness input
 *   3. Log      — command history
 */
import { useState } from 'react'
import { useDevices }    from './hooks/useDevices'
import { useBrightness } from './hooks/useBrightness'
import GroupSelector   from './components/GroupSelector'
import AbsoluteControl from './components/AbsoluteControl'
import CommandLog      from './components/CommandLog'
import './app.css'

export default function App() {
  const { groups, devices, loading, error } = useDevices()
  const { serverOnline, commandLog, sending, sendAbsolute, sendGroupRamp } = useBrightness()
  const [selectedGroups, setSelectedGroups] = useState([])

  function toggleGroup(g) {
    setSelectedGroups((prev) =>
      prev.includes(g) ? prev.filter((x) => x !== g) : [...prev, g]
    )
  }

  const statusClass = serverOnline === null ? 'unknown' : serverOnline ? 'online' : 'offline'
  const statusLabel = serverOnline === null ? 'Connecting…' : serverOnline ? 'Online' : 'Offline'

  return (
    <div className="app">

      <header className="topbar">
        <div className="topbar-left">
          <span className="topbar-logo">◈</span>
          <span className="topbar-title">LED Controller</span>
          <span className="topbar-model">FW16-C</span>
        </div>
        <div className="topbar-right">
          <span className={`server-dot ${statusClass}`} />
          <span className="server-label">API {statusLabel}</span>
        </div>
      </header>

      <main className="main-layout">

        {/* ── Section 1: Groups + Ramp ── */}
        <section className="panel">
          <div className="panel-header">
            <h2 className="panel-title">Group Ramp</h2>
            {selectedGroups.length > 0 && (
              <button className="clear-btn" onClick={() => setSelectedGroups([])}>
                Clear
              </button>
            )}
          </div>
          <p className="panel-hint">Select groups, then set ramp parameters</p>

          <GroupSelector
            groups={groups}
            selected={selectedGroups}
            onToggle={toggleGroup}
            onRun={sendGroupRamp}
            sending={sending}
            loading={loading}
            error={error}
          />
        </section>

        {/* ── Section 2: Absolute Brightness ── */}
        <section className="panel">
          <div className="panel-header">
            <h2 className="panel-title">Absolute Brightness</h2>
          </div>
          <p className="panel-hint">Set one device to an exact level instantly</p>

          <AbsoluteControl
            devices={devices}
            loading={loading}
            error={error}
            onSend={sendAbsolute}
            sending={sending}
          />
        </section>

        {/* ── Section 3: Command Log ── */}
        <section className="panel panel-log">
          <div className="panel-header">
            <h2 className="panel-title">Command Log</h2>
            <span className="log-count">{commandLog.length} entries</span>
          </div>
          <CommandLog entries={commandLog} />
        </section>

      </main>
    </div>
  )
}
