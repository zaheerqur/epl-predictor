<template>
  <div>
    <div class="teams-grid">
      <button v-for="t in teams" :key="t"
              class="team-chip" :class="{ active: selectedTeam === t }"
              @click="selectTeam(t)">
        <ClubLogo :team="t" class="chip-logo" />
        {{ t }}
      </button>
    </div>

    <div v-if="loadingTeam" class="empty"><span class="spinner"></span></div>
    <div v-else-if="teamData">
      <div class="team-profile-header">
        <ClubLogo :team="teamData.team" class="profile-logo" />
        <div style="flex:1">
          <div class="team-profile-name">{{ teamData.team }}</div>
          <div class="team-profile-sub">{{ teamData.season }} – {{ teamData.played }} games played</div>
        </div>
        <select class="season-sel" v-model="teamSeason" @change="selectTeam(selectedTeam)">
          <option v-for="s in seasons" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>

      <div class="stats-row">
        <div class="stat-card"><div class="stat-num" style="color:var(--win)">{{ teamData.won }}</div><div class="stat-lbl">Wins</div></div>
        <div class="stat-card"><div class="stat-num" style="color:var(--draw)">{{ teamData.drawn }}</div><div class="stat-lbl">Draws</div></div>
        <div class="stat-card"><div class="stat-num" style="color:var(--loss)">{{ teamData.lost }}</div><div class="stat-lbl">Losses</div></div>
        <div class="stat-card"><div class="stat-num">{{ teamData.goals_for }}</div><div class="stat-lbl">Goals For</div></div>
        <div class="stat-card"><div class="stat-num">{{ teamData.goals_against }}</div><div class="stat-lbl">Goals Against</div></div>
        <div class="stat-card">
          <div class="stat-num" :style="{ color: teamData.points_per_game >= 1.9 ? 'var(--win)' : teamData.points_per_game >= 1.3 ? 'var(--draw)' : 'var(--loss)' }">
            {{ teamData.points_per_game }}
          </div>
          <div class="stat-lbl">Pts / Game</div>
        </div>
      </div>

      <div class="record-grid">
        <div class="rec-card">
          <div class="rec-title">Home Record</div>
          <div class="rec-line"><span>Played</span><span>{{ teamData.home_record.played }}</span></div>
          <div class="rec-line"><span style="color:var(--win)">Won</span><span>{{ teamData.home_record.won }}</span></div>
          <div class="rec-line"><span style="color:var(--draw)">Drawn</span><span>{{ teamData.home_record.drawn }}</span></div>
          <div class="rec-line"><span style="color:var(--loss)">Lost</span><span>{{ teamData.home_record.lost }}</span></div>
          <div class="rec-line"><span>Goals</span><span>{{ teamData.home_record.gf }}–{{ teamData.home_record.ga }}</span></div>
        </div>
        <div class="rec-card">
          <div class="rec-title">Away Record</div>
          <div class="rec-line"><span>Played</span><span>{{ teamData.away_record.played }}</span></div>
          <div class="rec-line"><span style="color:var(--win)">Won</span><span>{{ teamData.away_record.won }}</span></div>
          <div class="rec-line"><span style="color:var(--draw)">Drawn</span><span>{{ teamData.away_record.drawn }}</span></div>
          <div class="rec-line"><span style="color:var(--loss)">Lost</span><span>{{ teamData.away_record.lost }}</span></div>
          <div class="rec-line"><span>Goals</span><span>{{ teamData.away_record.gf }}–{{ teamData.away_record.ga }}</span></div>
        </div>
      </div>

      <div class="results-card" style="margin-top:10px">
        <div class="form-lbl" style="margin-bottom:10px">Recent Results</div>
        <div v-for="f in [...teamData.form].reverse()" :key="f.date" class="result-row">
          <div :class="'fdot fdot-' + f.result" style="width:26px;height:26px;border-radius:7px;flex-shrink:0">{{ f.result }}</div>
          <div class="rdate">{{ f.date }}</div>
          <div class="ropp">vs {{ f.opponent }}</div>
          <div class="rscore">{{ f.goals_for }}–{{ f.goals_against }}</div>
        </div>
      </div>
    </div>
    <div v-else-if="!selectedTeam" class="empty">Select a team above to view their stats</div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useAppState } from '@/composables/useAppState.js'
import { apiFetch } from '@/composables/useApi.js'
import ClubLogo from '@/components/ClubLogo.vue'

const { teams, seasons } = useAppState()

const selectedTeam = ref(null)
const teamData     = ref(null)
const loadingTeam  = ref(false)
const teamSeason   = ref('')

watch(seasons, s => {
  if (s.length && !teamSeason.value) teamSeason.value = s[s.length - 1]
}, { immediate: true })

onMounted(() => {
  if (seasons.value.length) teamSeason.value = seasons.value[seasons.value.length - 1]
})

async function selectTeam(t) {
  selectedTeam.value = t
  loadingTeam.value = true
  teamData.value = null
  try { teamData.value = await apiFetch(`/team/${encodeURIComponent(t)}?season=${teamSeason.value}`) }
  catch { teamData.value = null }
  finally { loadingTeam.value = false }
}
</script>
