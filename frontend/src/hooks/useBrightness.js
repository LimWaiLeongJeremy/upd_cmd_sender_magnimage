/**
 * hooks/useBrightness.js
 * -----------------------
 * Central state for the entire dashboard.
 *
 * WHY A CUSTOM HOOK?
 *   Components should be dumb — they render and call handlers.
 *   All state logic lives here: isolated, testable, reusable.
 *
 * This hook imports from your existing brightnessApi.js — no duplication.
 */

import { useState, useCallback, useEffect, useRef } from 'react'
import {
  rampGroupBrightness,
  setAbsoluteBrightness as apiSetAbsolute,
} from '../api/brightnessApi'

// Group registry — keep in sync with config/ip_groups.py
export const GROUPS = [
  { id: 'm',    label: 'Main',       ipCount: 6 },
  { id: 'ac',   label: 'AC',         ipCount: 2 },
  { id: 'b',    label: 'B Panel',    ipCount: 2 },
  { id: 'e',    label: 'E Panel',    ipCount: 2 },
  { id: 'ctrl', label: 'Controller', ipCount: 1 },
]

const ALL_IDS = GROUPS.map((g) => g.id)

function initGroupStates() {
  return Object.fromEntries(
    ALL_IDS.map((id) => [id, { brightness: null, status: 'idle', error: null, lastUpdated: null }])
  )
}

export function useBrightness() {
  const [groupStates, setGroupStates]   = useState(initGroupStates)
  const [commandLog,  setCommandLog]    = useState([])
  const [serverOnline, setServerOnline] = useState(null)
  const rampInFlight = useRef(false)

  // ── Health check every 30s ──
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
    const id = setInterval(ping, 30_000)
    return () => clearInterval(id)
  }, [])

  const patchGroup = useCallback((id, patch) => {
    setGroupStates((prev) => ({ ...prev, [id]: { ...prev[id], ...patch } }))
  }, [])

  const addLog = useCallback((entry) => {
    setCommandLog((prev) => [{ id: Date.now(), ...entry }, ...prev].slice(0, 50))
  }, [])

  // ── Set one group to an absolute brightness ──
  // Trick: ramp from X to X with step=1, interval=0 — same as instant set
  // but goes through the group endpoint so all devices in the group are hit.
  const setGroupBrightness = useCallback(async (groupId, brightness) => {
    patchGroup(groupId, { status: 'loading', error: null })

    const { data, error } = await rampGroupBrightness([groupId], brightness, brightness, 1, 0)

    if (error) {
      patchGroup(groupId, { status: 'error', error })
      addLog({ type: 'absolute', groups: [groupId], brightness, status: 'error', message: error, timestamp: new Date() })
      return
    }

    patchGroup(groupId, { status: 'success', brightness, error: null, lastUpdated: new Date() })
    addLog({ type: 'absolute', groups: [groupId], brightness, status: 'success', message: data.message, timestamp: new Date() })
    setTimeout(() => patchGroup(groupId, { status: 'idle' }), 2000)
  }, [patchGroup, addLog])

  // ── Ramp across multiple groups ──
  const runGroupRamp = useCallback(async ({ groups, startBrightness, endBrightness, step, intervalSeconds }) => {
    if (rampInFlight.current) return
    rampInFlight.current = true

    groups.forEach((g) => patchGroup(g, { status: 'loading', error: null }))

    const { data, error } = await rampGroupBrightness(groups, startBrightness, endBrightness, step, intervalSeconds)
    rampInFlight.current = false

    if (error) {
      groups.forEach((g) => patchGroup(g, { status: 'error', error }))
      addLog({ type: 'ramp', groups, startBrightness, endBrightness, status: 'error', message: error, timestamp: new Date() })
      return
    }

    groups.forEach((g) => patchGroup(g, { status: 'success', brightness: endBrightness, error: null, lastUpdated: new Date() }))
    addLog({ type: 'ramp', groups, startBrightness, endBrightness, status: 'success', message: data.message, timestamp: new Date() })
    setTimeout(() => groups.forEach((g) => patchGroup(g, { status: 'idle' })), 2000)
  }, [patchGroup, addLog])

  return { groupStates, commandLog, serverOnline, rampInFlight, setGroupBrightness, runGroupRamp }
}
