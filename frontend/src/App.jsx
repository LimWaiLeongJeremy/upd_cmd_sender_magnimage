/**
 * App.jsx — Root component. Layout only, no logic.
 */
import { useState } from 'react'
import { useBrightness, GROUPS } from './hooks/useBrightness'
import GroupCard from './components/GroupCard'
import GlobalRampPanel from './components/GlobalRampPanel'
import CommandLog from './components/CommandLog'
import './app.css'

export default function App() {
  const {
    groupStates,
    commandLog,
    serverOnline,
    rampInFlight,
    setGroupBrightness,
    runGroupRamp,
  } = useBrightness()

  const [selectedGroups, setSelectedGroups] = useState([])

  function toggleGroupSelection(groupId) {
    setSelectedGroups((prev) =>
      prev.includes(groupId) ? prev.filter((g) => g !== groupId) : [...prev, groupId]
    )
  }

  const serverStatus =
    serverOnline === null ? 'Connecting…' : serverOnline ? 'Online' : 'Offline'
  const serverStatusClass =
    serverOnline === null ? 'unknown' : serverOnline ? 'online' : 'offline'

  return (
    <div className="app">
      <header className="topbar">
        <div className="topbar-left">
          <span className="topbar-logo">◈</span>
          <span className="topbar-title">LED Controller</span>
          <span className="topbar-model">FW16-C</span>
        </div>
        <div className="topbar-right">
          <span className={`server-dot ${serverStatusClass}`} />
          <span className="server-label">API {serverStatus}</span>
        </div>
      </header>

      <main className="main-layout">
        <section className="groups-section">
          <div className="section-header">
            <h1 className="section-title">Device Groups</h1>
            <span className="section-hint">Slide to set · Release to send</span>
          </div>
          <div className="group-grid">
            {GROUPS.map((group) => (
              <GroupCard
                key={group.id}
                group={group}
                state={groupStates[group.id]}
                onSet={setGroupBrightness}
                isSelected={selectedGroups.includes(group.id)}
                onToggleSelect={() => toggleGroupSelection(group.id)}
              />
            ))}
          </div>
        </section>

        <aside className="sidebar">
          <GlobalRampPanel
            selectedGroups={selectedGroups}
            rampInFlight={rampInFlight}
            onRun={runGroupRamp}
            onSelectAll={() => setSelectedGroups(GROUPS.map((g) => g.id))}
            onClearAll={() => setSelectedGroups([])}
          />
          <div className="log-section">
            <h2 className="section-title log-title">Command Log</h2>
            <CommandLog entries={commandLog} />
          </div>
        </aside>
      </main>
    </div>
  )
}
