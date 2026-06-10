const LOCAL = ['localhost', '127.0.0.1', ''].includes(window.location.hostname)
export const API_BASE = LOCAL ? 'http://localhost:8000' : '/api'

export async function apiFetch(path, opts) {
  const r = await fetch(API_BASE + path, opts)
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}
