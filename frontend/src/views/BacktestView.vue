<template>
  <div>
    <div v-if="loadingBt" class="empty"><span class="spinner"></span></div>
    <div v-else-if="!btData" class="empty">Validation data unavailable – run pipeline.py first.</div>
    <div v-else>
      <div class="page-header">
        <div class="page-title">2025–26 Season Backtesting</div>
        <div class="page-sub">Predictions made using only pre-match data – no look-ahead leakage. Model trained on 2015–16 through 2024–25.</div>
      </div>

      <div class="metric-row">
        <div class="metric-card m-overall">
          <div class="metric-num">{{ (btData.accuracy * 100).toFixed(1) }}%</div>
          <div class="metric-lbl">Overall Accuracy</div>
          <div class="metric-sub">{{ btData.correct }} / {{ btData.total }} correct</div>
        </div>
        <div class="metric-card m-hw">
          <div class="metric-num">{{ (btData.by_outcome.H.accuracy * 100).toFixed(1) }}%</div>
          <div class="metric-lbl">Home Win</div>
          <div class="metric-sub">{{ btData.by_outcome.H.correct }} / {{ btData.by_outcome.H.total }}</div>
        </div>
        <div class="metric-card m-draw">
          <div class="metric-num">{{ (btData.by_outcome.D.accuracy * 100).toFixed(1) }}%</div>
          <div class="metric-lbl">Draw</div>
          <div class="metric-sub">{{ btData.by_outcome.D.correct }} / {{ btData.by_outcome.D.total }}</div>
        </div>
        <div class="metric-card m-aw">
          <div class="metric-num">{{ (btData.by_outcome.A.accuracy * 100).toFixed(1) }}%</div>
          <div class="metric-lbl">Away Win</div>
          <div class="metric-sub">{{ btData.by_outcome.A.correct }} / {{ btData.by_outcome.A.total }}</div>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-head">
          <div class="chart-title">Running Accuracy Over the Season</div>
          <div class="chart-legend">
            <div class="leg-item"><div class="leg-line"></div> Model</div>
            <div class="leg-item"><div class="leg-dash"></div> Home baseline</div>
          </div>
        </div>
        <div style="width:100%;overflow:hidden">
          <svg viewBox="0 0 800 120" preserveAspectRatio="xMidYMid meet"
               xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;display:block">
            <line x1="40" y1="10"  x2="790" y2="10"  stroke="#e2e8f0" stroke-width="1"/>
            <line x1="40" y1="35"  x2="790" y2="35"  stroke="#e2e8f0" stroke-width="1"/>
            <line x1="40" y1="60"  x2="790" y2="60"  stroke="#e2e8f0" stroke-width="1"/>
            <line x1="40" y1="85"  x2="790" y2="85"  stroke="#e2e8f0" stroke-width="1"/>
            <line x1="40" y1="108" x2="790" y2="108" stroke="#e2e8f0" stroke-width="1"/>
            <text x="34" y="13"  text-anchor="end" fill="#94a3b8" font-size="9" font-family="Inter,sans-serif">100%</text>
            <text x="34" y="38"  text-anchor="end" fill="#94a3b8" font-size="9" font-family="Inter,sans-serif">75%</text>
            <text x="34" y="63"  text-anchor="end" fill="#94a3b8" font-size="9" font-family="Inter,sans-serif">50%</text>
            <text x="34" y="88"  text-anchor="end" fill="#94a3b8" font-size="9" font-family="Inter,sans-serif">25%</text>
            <text x="34" y="111" text-anchor="end" fill="#94a3b8" font-size="9" font-family="Inter,sans-serif">0%</text>
            <line :x1="40" :y1="chartY(btData.by_outcome.H.total / btData.total)"
                  x2="790" :y2="chartY(btData.by_outcome.H.total / btData.total)"
                  stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="5,4"/>
            <path :d="chartAreaPath" fill="rgba(124,58,237,0.06)"/>
            <path :d="chartLinePath" fill="none" stroke="#7c3aed" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle v-if="chartPoints.length"
                    :cx="chartPoints[chartPoints.length - 1].x"
                    :cy="chartPoints[chartPoints.length - 1].y"
                    r="4" fill="#7c3aed"/>
          </svg>
        </div>
      </div>

      <div class="filter-bar">
        <div class="filter-row">
          <div class="filter-lbl">Confidence ≥</div>
          <div class="slider-wrap">
            <input type="range" class="conf-slider" min="0" max="80" step="5" v-model.number="btConfThresh" />
            <div class="conf-val">{{ btConfThresh }}%</div>
          </div>
          <div class="match-count">
            Showing <strong>{{ filteredMatches.length }}</strong> of <strong>{{ btData.total }}</strong> matches
          </div>
        </div>
        <div class="filter-row">
          <div class="filter-lbl">Outcome</div>
          <div class="chip-group">
            <button class="chip"       :class="{ active: btOutcomeFilter === 'ALL' }" @click="btOutcomeFilter = 'ALL'">All</button>
            <button class="chip chip-H" :class="{ active: btOutcomeFilter === 'H' }"  @click="btOutcomeFilter = 'H'">Home</button>
            <button class="chip chip-D" :class="{ active: btOutcomeFilter === 'D' }"  @click="btOutcomeFilter = 'D'">Draw</button>
            <button class="chip chip-A" :class="{ active: btOutcomeFilter === 'A' }"  @click="btOutcomeFilter = 'A'">Away</button>
          </div>
          <div class="filter-lbl" style="margin-left:.5rem">Prediction</div>
          <div class="chip-group">
            <button class="chip"          :class="{ active: btResultFilter === 'ALL' }"     @click="btResultFilter = 'ALL'">All</button>
            <button class="chip chip-ok"  :class="{ active: btResultFilter === 'CORRECT' }" @click="btResultFilter = 'CORRECT'">Correct</button>
            <button class="chip chip-bad" :class="{ active: btResultFilter === 'WRONG' }"   @click="btResultFilter = 'WRONG'">Wrong</button>
          </div>
        </div>
        <div class="filter-row">
          <div class="filter-lbl">Team</div>
          <select class="team-filter-sel" v-model="btTeamFilter">
            <option value="">All Teams</option>
            <option v-for="t in btTeams" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>
      </div>

      <div v-if="filteredMatches.length" class="cards-grid">
        <div v-for="m in filteredMatches" :key="m.date + m.home_team"
             class="match-card" :class="m.correct ? 'correct-card' : 'wrong-card'">
          <div class="card-top">
            <span class="gw-badge">GW {{ m.gameweek }}</span>
            <span class="card-date">{{ m.date }}</span>
            <div class="card-result-dot" :class="m.correct ? 'ri-correct' : 'ri-wrong'">
              {{ m.correct ? '✓' : '✗' }}
            </div>
          </div>
          <div class="card-teams">
            <div class="card-team">
              <ClubLogo :team="m.home_team" class="card-team-logo" />
              <span class="card-team-name">{{ m.home_team }}</span>
            </div>
            <div class="card-score">{{ m.home_goals }} – {{ m.away_goals }}</div>
            <div class="card-team away-s">
              <ClubLogo :team="m.away_team" class="card-team-logo" />
              <span class="card-team-name" style="text-align:right">{{ m.away_team }}</span>
            </div>
          </div>
          <div class="card-foot">
            <span class="pred-chip" :class="'pred-' + m.predicted">
              {{ m.predicted === 'H' ? 'Home Win' : m.predicted === 'D' ? 'Draw' : 'Away Win' }}
            </span>
            <span class="card-conf">{{ (m.confidence * 100).toFixed(0) }}% conf</span>
            <div class="mini-probs">
              <span class="mini-p">H <strong>{{ (m.home_win_prob * 100).toFixed(0) }}%</strong></span>
              <span class="mini-p">D <strong>{{ (m.draw_prob * 100).toFixed(0) }}%</strong></span>
              <span class="mini-p">A <strong>{{ (m.away_win_prob * 100).toFixed(0) }}%</strong></span>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="empty-cards">No matches match the current filters.</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiFetch } from '@/composables/useApi.js'
import ClubLogo from '@/components/ClubLogo.vue'

const btData          = ref(null)
const loadingBt       = ref(false)
const btConfThresh    = ref(0)
const btOutcomeFilter = ref('ALL')
const btResultFilter  = ref('ALL')
const btTeamFilter    = ref('')

const X_MIN = 40, X_MAX = 790, Y_MIN = 10, Y_MAX = 108

function toX(i, total) { return X_MIN + (i / (total - 1)) * (X_MAX - X_MIN) }
function toY(pct)       { return Y_MAX - pct * (Y_MAX - Y_MIN) }

const chartPoints = computed(() => {
  if (!btData.value) return []
  return btData.value.matches.map((m, i) => ({
    x: toX(i, btData.value.matches.length),
    y: toY(m.running_accuracy),
  }))
})

const chartLinePath = computed(() => {
  const pts = chartPoints.value
  if (!pts.length) return ''
  let d = `M ${pts[0].x} ${pts[0].y}`
  for (let i = 1; i < pts.length; i++) {
    const cx = (pts[i - 1].x + pts[i].x) / 2
    d += ` C ${cx} ${pts[i - 1].y}, ${cx} ${pts[i].y}, ${pts[i].x} ${pts[i].y}`
  }
  return d
})

const chartAreaPath = computed(() => {
  const pts = chartPoints.value
  if (!pts.length) return ''
  let d = `M ${pts[0].x} ${Y_MAX} L ${pts[0].x} ${pts[0].y}`
  for (let i = 1; i < pts.length; i++) {
    const cx = (pts[i - 1].x + pts[i].x) / 2
    d += ` C ${cx} ${pts[i - 1].y}, ${cx} ${pts[i].y}, ${pts[i].x} ${pts[i].y}`
  }
  d += ` L ${pts[pts.length - 1].x} ${Y_MAX} Z`
  return d
})

function chartY(pct) { return toY(pct) }

const btTeams = computed(() => {
  if (!btData.value) return []
  const s = new Set()
  btData.value.matches.forEach(m => { s.add(m.home_team); s.add(m.away_team) })
  return [...s].sort()
})

const filteredMatches = computed(() => {
  if (!btData.value) return []
  const thresh = btConfThresh.value / 100
  return btData.value.matches.filter(m => {
    if (m.confidence < thresh) return false
    if (btOutcomeFilter.value !== 'ALL' && m.actual !== btOutcomeFilter.value) return false
    if (btResultFilter.value === 'CORRECT' && !m.correct) return false
    if (btResultFilter.value === 'WRONG' && m.correct) return false
    if (btTeamFilter.value && m.home_team !== btTeamFilter.value && m.away_team !== btTeamFilter.value) return false
    return true
  })
})

onMounted(async () => {
  loadingBt.value = true
  try { btData.value = await apiFetch('/validation') }
  catch { btData.value = null }
  finally { loadingBt.value = false }
})
</script>
