<template>
  <div>
    <div class="tbl-outer">
      <div class="tbl-wrap">
        <div class="tbl-head">
          <span class="tbl-title">Premier League Table</span>
          <select class="season-sel" v-model="season" @change="loadTable">
            <option v-for="s in seasons" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
        <div v-if="loadingTable" class="empty"><span class="spinner"></span></div>
        <table v-else>
          <thead>
            <tr>
              <th>#</th><th>Club</th><th>P</th><th>W</th><th>D</th><th>L</th>
              <th>GF</th><th>GA</th><th>GD</th><th>Pts</th><th>Form</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in table" :key="row.team">
              <td><span class="pos-badge" :class="posCls(row.position, season)">{{ row.position }}</span></td>
              <td>
                <div class="club-cell">
                  <ClubLogo :team="row.team" class="club-logo-sm" />
                  {{ row.team }}
                </div>
              </td>
              <td>{{ row.played }}</td>
              <td>{{ row.won }}</td>
              <td>{{ row.drawn }}</td>
              <td>{{ row.lost }}</td>
              <td>{{ row.goals_for }}</td>
              <td>{{ row.goals_against }}</td>
              <td :class="row.goal_difference > 0 ? 'gd-pos' : row.goal_difference < 0 ? 'gd-neg' : ''">
                {{ row.goal_difference > 0 ? '+' : '' }}{{ row.goal_difference }}
              </td>
              <td class="pts-bold">{{ row.points }}</td>
              <td>
                <div class="form-mini">
                  <div v-for="(r, i) in row.form" :key="i" class="fmini"
                       :style="{ background: r === 'W' ? 'var(--win)' : r === 'D' ? 'var(--draw)' : 'var(--loss)' }">
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="zone-legend">
      <div class="zone-item"><div class="zone-dot" style="background:rgba(37,99,235,.6)"></div>
        Champions League ({{ parseInt(season.split('-')[0]) >= 2024 ? 'Top 5' : 'Top 4' }})
      </div>
      <div class="zone-item"><div class="zone-dot" style="background:rgba(234,88,12,.6)"></div> Europa League</div>
      <div v-if="parseInt(season.split('-')[0]) >= 2021" class="zone-item">
        <div class="zone-dot" style="background:rgba(147,51,234,.6)"></div> Conference League
      </div>
      <div class="zone-item"><div class="zone-dot" style="background:rgba(220,38,38,.6)"></div> Relegation</div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useAppState } from '@/composables/useAppState.js'
import { apiFetch } from '@/composables/useApi.js'
import ClubLogo from '@/components/ClubLogo.vue'

const { seasons } = useAppState()

const season       = ref('')
const table        = ref([])
const loadingTable = ref(false)

watch(seasons, s => {
  if (s.length && !season.value) season.value = s[s.length - 1]
}, { immediate: true })

async function loadTable() {
  if (!season.value) return
  loadingTable.value = true; table.value = []
  try { table.value = await apiFetch(`/standings?season=${season.value}`) }
  catch { table.value = [] }
  finally { loadingTable.value = false }
}

function posCls(p, s) {
  const yr = parseInt((s || '').split('-')[0]) || 0
  const clSpots = yr >= 2024 ? 5 : 4
  const elPos   = clSpots + 1
  const eclPos  = yr >= 2021 ? clSpots + 2 : null
  if (p <= clSpots)            return 'pos-badge pos-cl'
  if (p === elPos)             return 'pos-badge pos-el'
  if (eclPos && p === eclPos)  return 'pos-badge pos-ecl'
  if (p >= 18)                 return 'pos-badge pos-rel'
  return 'pos-badge pos-def'
}

onMounted(() => {
  if (seasons.value.length) {
    season.value = seasons.value[seasons.value.length - 1]
    loadTable()
  }
})

watch(seasons, s => {
  if (s.length && !table.value.length) {
    season.value = s[s.length - 1]
    loadTable()
  }
})
</script>
