/**
 * hooks/useBrightness.js
 * -----------------------
 * Handles sending commands and tracking the command log.
 * Also runs the server health check every 30 seconds.
 */
import { useState, useCallback, useEffect } from 'react'
import { setAbsoluteBrightness, rampGroupBrightness } from '../api/brightnessApi'

export function useBrightness() {
  const [serverOnline, setServerOnline] = useState(null)
  const [commandLog,   setCommandLog]   = useState([])
  const [sending,      setSending]      = useState(false)

  // Health check on mount and every 30s
  useEffect(() => {
    async function ping() {
      try {
        const res = await fetch('/api/health')
        setServerOnline(res.ok)
      } catch {
        setServerOnline(false)
      }
    }
    ping()
    const id = setInterval(ping, 30000)
    return () => clearInterval(id)
  }, [])

  const addLog = useCallback((entry) => {
    setCommandLog((prev) =>
      [{ id: Date.now(), timestamp: new Date(), ...entry }, ...prev].slice(0, 50)
    )
  }, [])

  // Send absolute brightness to a single device
  const sendAbsolute = useCallback(async (ip, brightness) => {
    setSending(true)
    const { data, error } = await setAbsoluteBrightness(ip, brightness)
    setSending(false)
    if (error) {
      addLog({ type: 'absolute', ip, brightness, status: 'error', message: String(error) })
      return { error }
    }
    addLog({ type: 'absolute', ip, brightness, status: 'success', message: data.message })
    return { data }
  }, [addLog])

  // Ramp brightness across selected groups
  const sendGroupRamp = useCallback(async ({ groups, startBrightness, endBrightness, step, intervalSeconds }) => {
    setSending(true)
    const { data, error } = await rampGroupBrightness(groups, startBrightness, endBrightness, step, intervalSeconds)
    setSending(false)
    if (error) {
      addLog({ type: 'ramp', groups, startBrightness, endBrightness, status: 'error', message: String(error) })
      return { error }
    }
    addLog({ type: 'ramp', groups, startBrightness, endBrightness, status: 'success', message: data.message })
    return { data }
  }, [addLog])

  return { serverOnline, commandLog, sending, sendAbsolute, sendGroupRamp }
}
