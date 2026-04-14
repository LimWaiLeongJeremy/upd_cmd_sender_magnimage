/**
 * hooks/useDevices.js
 * --------------------
 * Fetches group names and device IPs from the backend on mount.
 * Keeps device config separate from brightness state.
 */
import { useState, useEffect } from 'react'
import { fetchGroups, fetchDevices } from '../api/brightnessApi'

export function useDevices() {
  const [groups,  setGroups]  = useState([])
  const [devices, setDevices] = useState([])
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  useEffect(() => {
    async function load() {
      setLoading(true)
      setError(null)
      const [groupsRes, devicesRes] = await Promise.all([
        fetchGroups(),
        fetchDevices(),
      ])
      if (groupsRes.error || devicesRes.error) {
        setError(groupsRes.error ?? devicesRes.error)
      } else {
        setGroups(groupsRes.data.groups)
        setDevices(devicesRes.data.devices)
      }
      setLoading(false)
    }
    load()
  }, [])

  return { groups, devices, loading, error }
}
