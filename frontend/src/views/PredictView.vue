<template>
  <div>
    <div class="predict-grid">
      <!-- Home -->
      <div class="team-picker">
        <span class="picker-label">Home Team</span>
        <div class="team-preview">
          <template v-if="home">
            <ClubLogo :team="home" class="team-preview-logo" />
            <span class="team-preview-name">{{ home }}</span>
          </template>
          <div v-else style="height:46px"></div>
        </div>
        <select class="team-select" v-model="home" @change="onTeamChange">
          <option value="" disabled>Select team…</option>
          <option v-for="t in teams" :key="t" :value="t">{{ t }}</option>
        </select>
        <TeamMiniStats v-if="homePreview" :preview="homePreview" />
      </div>

      <div class="vs-block">
        <span class="vs-text">vs</span>
      </div>

      <!-- Away -->
      <div class="team-picker">
        <span class="picker-label">Away Team</span>
        <div class="team-preview">
          <template v-if="away">
            <ClubLogo :team="away" class="team-preview-logo" />
            <span class="team-preview-name">{{ away }}</span>
          </template>
          <div v-else style="height:46px"></div>
        </div>
        <select class="team-select" v-model="away" @change="onTeamChange">
          <option value="" disabled>Select team…</option>
          <option v-for="t in teams" :key="t" :value="t" :disabled="t === home">{{ t }}</option>
        </select>
        <TeamMiniStats v-if="awayPreview" :preview="awayPreview" />
      </div>
    </div>

    <!-- H2H strip -->
    <div v-if="h2hPreview" class="h2h-card">
      <div class="h2h-tag">Head to Head</div>
      <div class="h2h-stats">
        <div class="h2h-stat">
          <div class="h2h-stat-n" style="color:var(--win)">{{ h2hPreview.home_wins }}</div>
          <div class="h2h-stat-l">{{ getAbbr(home) }} W</div>
        </div>
        <div class="h2h-stat">
          <div class="h2h-stat-n" style="color:var(--draw)">{{ h2hPreview.draws }}</div>
          <div class="h2h-stat-l">Draws</div>
        </div>
        <div class="h2h-stat">
          <div class="h2h-stat-n" style="color:var(--loss)">{{ h2hPreview.away_wins }}</div>
          <div class="h2h-stat-l">{{ getAbbr(away) }} W</div>
        </div>
      </div>
      <div class="h2h-dots">
        <span style="font-size:.62rem;color:var(--muted);margin-right:4px">LAST 5</span>
        <div v-for="(m, i) in h2hPreview.matches.slice(0, 5)" :key="i"
             class="h2h-dot" :style="h2hDotStyle(m.result)"
             :title="`${m.date}: ${h2hPreview.home_team} ${m.home_goals}–${m.away_goals} ${h2hPreview.away_team}`">
          {{ m.result }}
        </div>
      </div>
    </div>

    <button class="predict-btn" :disabled="!home || !away || loading" @click="predict">
      <span v-if="loading"><span class="spinner"></span>&nbsp; Predicting…</span>
      <span v-else>Predict Match</span>
    </button>
    <div v-if="err" class="error-box">{{ err }}</div>

    <!-- Result card -->
    <div v-if="result" class="result-card">
      <div class="result-teams">
        <div class="result-team">
          <ClubLogo :team="result.home_team" class="res-logo" />
          <div>
            <div class="res-name">{{ result.home_team }}</div>
            <div class="res-role">Home</div>
          </div>
        </div>
        <div class="result-verdict">
          <div :class="vpClass(result.prediction)">{{ result.prediction }}</div>
          <div class="verdict-conf">{{ (result.confidence * 100).toFixed(0) }}% confidence</div>
        </div>
        <div class="result-team away">
          <ClubLogo :team="result.away_team" class="res-logo" style="margin-left:auto" />
          <div>
            <div class="res-name">{{ result.away_team }}</div>
            <div class="res-role">Away</div>
          </div>
        </div>
      </div>

      <div class="sep"></div>
      <div class="prob-section">
        <div class="prob-row">
          <div class="prob-name">Home Win</div>
          <div class="prob-track"><div class="prob-fill" :style="{ width: pct(result.home_win_prob), background: 'var(--win)' }"></div></div>
          <div class="prob-pct" style="color:var(--win)">{{ pct(result.home_win_prob) }}</div>
        </div>
        <div class="prob-row">
          <div class="prob-name">Draw</div>
          <div class="prob-track"><div class="prob-fill" :style="{ width: pct(result.draw_prob), background: 'var(--draw)' }"></div></div>
          <div class="prob-pct" style="color:var(--draw)">{{ pct(result.draw_prob) }}</div>
        </div>
        <div class="prob-row">
          <div class="prob-name">Away Win</div>
          <div class="prob-track"><div class="prob-fill" :style="{ width: pct(result.away_win_prob), background: 'var(--loss)' }"></div></div>
          <div class="prob-pct" style="color:var(--loss)">{{ pct(result.away_win_prob) }}</div>
        </div>
      </div>

      <div class="sep"></div>
      <div class="form-section">
        <div>
          <div class="form-lbl">{{ result.home_team }} form</div>
          <div class="form-dots">
            <div v-for="f in result.home_form" :key="f.date" :class="'fdot fdot-' + f.result"
                 :title="`${f.result} ${f.goals_for}–${f.goals_against} vs ${f.opponent} (${f.date})`">
              {{ f.result }}
            </div>
          </div>
        </div>
        <div>
          <div class="form-lbl">{{ result.away_team }} form</div>
          <div class="form-dots">
            <div v-for="f in result.away_form" :key="f.date" :class="'fdot fdot-' + f.result"
                 :title="`${f.result} ${f.goals_for}–${f.goals_against} vs ${f.opponent} (${f.date})`">
              {{ f.result }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAppState } from '@/composables/useAppState.js'
import { apiFetch } from '@/composables/useApi.js'
import { getAbbr } from '@/data/teams.js'
import ClubLogo from '@/components/ClubLogo.vue'
import TeamMiniStats from '@/components/TeamMiniStats.vue'

const { teams, offline } = useAppState()

const home        = ref('')
const away        = ref('')
const loading     = ref(false)
const result      = ref(null)
const err         = ref(null)
const h2hPreview  = ref(null)
const homePreview = ref(null)
const awayPreview = ref(null)

async function predict() {
  if (!home.value || !away.value) return
  loading.value = true; result.value = null; err.value = null
  try {
    result.value = await apiFetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ home_team: home.value, away_team: away.value }),
    })
  } catch (e) {
    err.value = offline.value ? 'Start the API: uvicorn api.main:app --port 8000' : e.message
  } finally {
    loading.value = false
  }
}

async function onTeamChange() {
  result.value = null
  h2hPreview.value = null
  homePreview.value = null
  awayPreview.value = null
  const fetches = []
  if (home.value) fetches.push(
    apiFetch(`/team/${encodeURIComponent(home.value)}`).then(d => { homePreview.value = d }).catch(() => {})
  )
  if (away.value) fetches.push(
    apiFetch(`/team/${encodeURIComponent(away.value)}`).then(d => { awayPreview.value = d }).catch(() => {})
  )
  if (home.value && away.value && home.value !== away.value) fetches.push(
    apiFetch(`/h2h/${encodeURIComponent(home.value)}/${encodeURIComponent(away.value)}`)
      .then(d => { h2hPreview.value = d }).catch(() => {})
  )
  await Promise.all(fetches)
}

function pct(v) { return (v * 100).toFixed(1) + '%' }

function vpClass(p) {
  return p === 'Home Win' ? 'verdict-pill vp-home'
       : p === 'Draw'     ? 'verdict-pill vp-draw'
       :                    'verdict-pill vp-away'
}

function h2hDotStyle(r) {
  const map = {
    H: { background: 'rgba(22,163,74,.12)',  color: '#16a34a' },
    D: { background: 'rgba(217,119,6,.12)',  color: '#d97706' },
    A: { background: 'rgba(220,38,38,.12)',  color: '#dc2626' },
  }
  return map[r] || { background: '#f1f5f9', color: '#64748b' }
}
</script>
