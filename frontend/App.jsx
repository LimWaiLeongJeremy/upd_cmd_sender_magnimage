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

