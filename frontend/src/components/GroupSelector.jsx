/**
 * GroupSelector.jsx
 * ------------------
 * Section 1: Group buttons fetched from the API.
 * Each button toggles selection. Selected groups are highlighted.
 */
export default function GroupSelector({ groups, selected, onToggle, loading, error }) {
  if (loading) return <p className="panel-placeholder">Loading groups…</p>
  if (error)   return <p className="panel-error">Failed to load groups: {error}</p>

  return (
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
  )
}
