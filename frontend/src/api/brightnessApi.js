/**
 * api/brightnessApi.js
 * ---------------------
 * Every HTTP call to the backend lives here — nowhere else.
 * Returns { data, error } — components never write try/catch.
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
      // FastAPI returns { detail: "string" } for most errors
      // BUT for 422 validation errors it returns { detail: [{type, loc, msg, ...}, ...] }
      // We must handle both shapes and always produce a plain string.
      const detail = json.detail
      let errorMsg

      if (typeof detail === 'string') {
        errorMsg = detail
      } else if (Array.isArray(detail)) {
        // Pydantic validation error — extract the human-readable msg from each item
        errorMsg = detail.map((e) => `${e.loc?.join('.')} — ${e.msg}`).join('; ')
      } else {
        errorMsg = `Server error ${response.status}`
      }

      return { data: null, error: errorMsg }
    }

    return { data: json, error: null }
  } catch (err) {
    return { data: null, error: `Network error: ${err.message}` }
  }
}

export async function setAbsoluteBrightness(ip, brightness) {
  return apiPost('/brightness/absolute', { ip, brightness })
}

export async function rampDeviceBrightness(ip, startBrightness, endBrightness, step, intervalSeconds) {
  return apiPost('/brightness/ramp/device', {
    ip,
    start_brightness: startBrightness,
    end_brightness: endBrightness,
    step,
    interval_seconds: intervalSeconds,
  })
}

export async function rampGroupBrightness(groups, startBrightness, endBrightness, step, intervalSeconds) {
  return apiPost('/brightness/ramp/groups', {
    groups,
    start_brightness: startBrightness,
    end_brightness: endBrightness,
    step,
    interval_seconds: intervalSeconds,
  })
}
