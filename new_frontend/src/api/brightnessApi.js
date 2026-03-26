/**
 * api/brightnessApi.js
 * ---------------------
 * All HTTP calls to the FastAPI backend live here — nowhere else.
 *
 * Pattern: every function returns { data, error }.
 * Components never write try/catch — they just check if error !== null.
 */

const BASE_URL = '/api'

async function apiPost(endpoint, body) {
  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })

    const json = await response.json()

    if (!response.ok) {
      return { data: null, error: json.detail ?? `Server error ${response.status}` }
    }

    return { data: json, error: null }
  } catch (err) {
    return { data: null, error: `Network error: ${err.message}` }
  }
}

/**
 * Set absolute brightness on a single device.
 * @param {string} ip
 * @param {number} brightness - 0–100
 */
export async function setAbsoluteBrightness(ip, brightness) {
  return apiPost('/brightness/absolute', { ip, brightness })
}

/**
 * Ramp brightness on a single device.
 */
export async function rampDeviceBrightness(ip, startBrightness, endBrightness, step, intervalSeconds) {
  return apiPost('/brightness/ramp/device', {
    ip,
    start_brightness: startBrightness,
    end_brightness: endBrightness,
    step,
    interval_seconds: intervalSeconds,
  })
}

/**
 * Ramp brightness across device groups.
 * @param {string[]} groups
 */
export async function rampGroupBrightness(groups, startBrightness, endBrightness, step, intervalSeconds) {
  return apiPost('/brightness/ramp/groups', {
    groups,
    start_brightness: startBrightness,
    end_brightness: endBrightness,
    step,
    interval_seconds: intervalSeconds,
  })
}
