/* Paired range slider + numeric input.
 * They stay in sync — changing either updates both.
 */

export function BrightnessSlider({ label, value, onChange, disabled }) {
  const pct = Math.max(0, Math.min(100, value ?? 0));

  function handleSlider(e) {
    const newValue = Number(e.target.value);
    onChange(newValue);
  }

  function handleInput(e) {
    const newValue = parseInt(e.target.value, 10);
    if (!isNaN(newValue)) {
      onChange(Math.max(0, Math.min(100, newValue)));
    }
  }

  return (
    <div>
      <div className="flex-between" style={{ marginBottom: 8 }}>
        <span className="label">{label}</span>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <input
            type="number"
            min={0}
            max={100}
            value={pct}
            onChange={handleInput}
            disabled={disabled}
            style={{
              width: 54,
              textAlign: "center",
              padding: "4px 6px",
              fontSize: 13,
            }}
          />
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: 11,
              color: "var(--text-muted)",
            }}
          >
            %
          </span>
        </div>
      </div>
      <input
        type="range"
        min={0}
        max={100}
        value={pct}
        onChange={handleSlider}
        disabled={disabled}
        style={{ "--fill": `${pct}%` }}
      />
      <div className="brightness-bar-track" style={{ marginTop: 6 }}>
        <div className="brightness-bar-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
