 /* Root component. Owns:
 *  - Tab navigation (Absolute | Ramp Device | Ramp Groups | Registry)
 *  - IP groups config (mirrors ip_groups.py — update this when you add IPs)
 *  - Toast state passed down to children
 *  - BrightnessProvider wrapping everything
 */



// ─────────────────────────────────────────────────────────────────────────────
// MIRROR OF ip_groups.py — keep these in sync.
// When you add IPs to ip_groups.py, add them here too.
// ─────────────────────────────────────────────────────────────────────────────
const IP_GROUPS = {
  m:    [],
  ac:   [],
  b:    [],
  e:    [],
  ctrl: ['127.0.0.1'],
}

// Flat list of all unique IPs across all groups
const ALL_IPS = [...new Set(Object.values(IP_GROUPS).flat())]

function Inner() {
    const [activeTab, setActiveTab] = useState('absolute')
    const { toasts, toast } = useToast()
    const { setDeviceBrightness, setGroupBrightness } = useBrightness()

    // Ramp device state
    const [rampDeviceIp, setRampDeviceIp] = useState('')
    const [rampDeviceLoading, setRampDeviceLoading] = useState(false)

    // Ramp groups state
    const [selectedGroups, setSelectedGroups] = useState(Object.keys(IP_GROUPS))
    const [rampGroupsLoading, setRampGroupsLoading] = useState(false)

    async function handleRampDevice({ startBrightness, endBrightness, step, intervalSeconds }) {
        setRampDeviceLoading(true)
        const { data, error } = await rampDevice(
        rampDeviceIp.trim(), startBrightness, endBrightness, step, intervalSeconds
        )
        setRampDeviceLoading(false)
        if (error) {    
            toast(`[${rampDeviceIp}] ${error}`, 'error')
        } else {
            setDeviceBrightness(rampDeviceIp.trim(), endBrightness)
            toast(`[${rampDeviceIp}] Brightness ramped successfully → ${endBrightness}`, 'success')
        }
    }
    
    async function handleRampGroups({ startBrightness, endBrightness, step, intervalSeconds }) {
        setRampGroupsLoading(true)
        const { data, error } = await rampGroups(
        selectedGroups, startBrightness, endBrightness, step, intervalSeconds
        )
        setRampGroupsLoading(false)
        if (error) {
            toast(`[Groups] ${error}`, 'error')
        } else {
            setGroupBrightness(selectedGroups, endBrightness)
            toast(`[Groups] Brightness ramped successfully → ${endBrightness}`, 'success')
        }
    }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <StatusBar />

      <main style={{ flex: 1, maxWidth: 900, width: '100%', margin: '0 auto', padding: '28px 24px' }}>

        {/* Page title */}
        <div style={{ marginBottom: 28 }}>
          <h1 style={{
            fontFamily: 'var(--font-display)',
            fontSize: 26,
            fontWeight: 700,
            letterSpacing: '0.04em',
            textTransform: 'uppercase',
            color: 'var(--text-primary)',
            lineHeight: 1,
          }}>
            Brightness Control
          </h1>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-muted)', marginTop: 6 }}>
            {ALL_IPS.length} device{ALL_IPS.length !== 1 ? 's' : ''} registered ·{' '}
            {Object.keys(IP_GROUPS).length} groups
          </div>
        </div>

        {/* Tab bar */}
        <div className="tab-bar">
          {TABS.map(t => (
            <button
              key={t.id}
              className={`tab${activeTab === t.id ? ' active' : ''}`}
              onClick={() => setActiveTab(t.id)}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* ── Tab: Absolute ──────────────────────────────────── */}
        {activeTab === 'absolute' && (
          <div>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-muted)', marginBottom: 20 }}>
              Set an immediate brightness level on individual devices.
            </p>
            {ALL_IPS.length === 0 ? (
              <EmptyState message="No IPs configured yet. Add IPs to IP_GROUPS in App.jsx." />
            ) : (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
                gap: 16,
              }}>
                {ALL_IPS.map(ip => {
                  const group = Object.entries(IP_GROUPS).find(([, ips]) => ips.includes(ip))?.[0]
                  return <DeviceCard key={ip} ip={ip} groupName={group} toast={toast} />
                })}
              </div>
            )}
          </div>
        )}

        {/* ── Tab: Ramp / Device ─────────────────────────────── */}
        {activeTab === 'ramp-device' && (
          <div style={{ maxWidth: 480 }}>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-muted)', marginBottom: 20 }}>
              Gradually transition brightness on a single controller.
            </p>
            <div className="panel">
              <RampForm
                mode="device"
                onSubmit={handleRampDevice}
                loading={rampDeviceLoading}
                deviceIp={rampDeviceIp}
                onDeviceIpChange={setRampDeviceIp}
              />
            </div>
            {rampDeviceLoading && (
              <RampProgressIndicator />
            )}
          </div>
        )}

        {/* ── Tab: Ramp / Groups ─────────────────────────────── */}
        {activeTab === 'ramp-groups' && (
          <div style={{ maxWidth: 480 }}>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-muted)', marginBottom: 20 }}>
              Run a concurrent brightness ramp across multiple device groups.
            </p>
            <div className="panel">
              <RampForm
                mode="groups"
                onSubmit={handleRampGroups}
                loading={rampGroupsLoading}
                groups={Object.keys(IP_GROUPS)}
                selectedGroups={selectedGroups}
                onGroupsChange={setSelectedGroups}
              />
            </div>
            {rampGroupsLoading && (
              <RampProgressIndicator />
            )}
          </div>
        )}

        {/* ── Tab: Registry ──────────────────────────────────── */}
        {activeTab === 'registry' && (
          <div>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-muted)', marginBottom: 20 }}>
              Configured groups and devices. Brightness values are persisted locally.
            </p>
            <GroupsPanel ipGroups={IP_GROUPS} />
          </div>
        )}

      </main>

      <ToastContainer toasts={toasts} />
    </div>
  )
}

function EmptyState({ message }) {
  return (
    <div style={{   
        padding: 40,
        textAlign: 'center',
        fontFamily: 'var(--font-mono)',
        fontSize: 12,
        color: 'var(--text-muted)',
        border: '1px dashed var(--border-mid)',
        borderRadius: 'var(--radius-lg)',
    }}>
      {message}
    </div>
  )
}

function RampProgressIndicator() {
    return (
        <div style={{
            marginTop: 16,
            padding: '12px 16px',
            background: 'var(--bg-input)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-accent)',
            fontFamily: 'var(--font-mono)',
            fontSize: 12,
            color: 'var(--text-accent)',
            display: 'flex',
            alignItems: 'center',
            gap: 10,
        }}>
            <span style={{ animation: 'spin 1s linear infinite', display: 'inline-block' }}>◌</span>
            Ramp in progress — request will complete when all steps are done…
            <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </div>
    )
}

export default function App() {
  return (
    <BrightnessProvider>
      <Inner />
    </BrightnessProvider>
  )
}