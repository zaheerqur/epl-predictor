import { ref } from 'vue'
import { apiFetch } from './useApi.js'

const teams = ref([])
const seasons = ref([])
const offline = ref(false)
const initialized = ref(false)

const FALLBACK_TEAMS = [
  'Arsenal','Aston Villa','Bournemouth','Brentford','Brighton',
  'Chelsea','Crystal Palace','Everton','Fulham','Ipswich','Leicester',
  'Liverpool','Man City','Man United','Newcastle',"Nott'm Forest",
  'Southampton','Tottenham','West Ham','Wolves',
]

export function useAppState() {
  async function init() {
    if (initialized.value) return
    try {
      const [t, s] = await Promise.all([apiFetch('/teams'), apiFetch('/seasons')])
      teams.value = t
      seasons.value = s
    } catch {
      offline.value = true
      teams.value = FALLBACK_TEAMS
      seasons.value = ['2025-26']
    }
    initialized.value = true
  }
  return { teams, seasons, offline, init }
}
