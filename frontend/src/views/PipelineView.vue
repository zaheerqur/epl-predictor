<template>
  <div>
    <div v-if="loadingPipe" class="empty"><span class="spinner"></span></div>
    <div v-else-if="!pipe" class="empty">Pipeline data unavailable – run pipeline.py first.</div>
    <div v-else>
      <div class="page-header">
        <div class="page-title">ML Pipeline</div>
        <div class="page-sub">Real EPL match data ingested, cleaned, feature-engineered, and fed into a calibrated gradient-boosted classifier – all served via REST API.</div>
      </div>

      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-val" style="color:var(--accent)">{{ pipe.total_matches.toLocaleString() }}</div>
          <div class="kpi-lbl">Matches</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-val" style="color:#2563eb">{{ pipe.n_seasons }}</div>
          <div class="kpi-lbl">Seasons</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-val" style="color:var(--draw)">{{ pipe.n_features }}</div>
          <div class="kpi-lbl">Features</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-val" style="color:var(--win)">{{ (pipe.test_accuracy * 100).toFixed(1) }}%</div>
          <div class="kpi-lbl">Test Accuracy</div>
        </div>
      </div>

      <div class="pipe-flow">
        <div v-for="step in pipe.pipeline_steps" :key="step.name" class="pipe-step">
          <div class="pipe-icon">{{ pipeIcon(step.name) }}</div>
          <div class="pipe-name">{{ step.name }}</div>
          <div class="pipe-detail">{{ step.detail }}</div>
        </div>
      </div>

      <div class="two-col">
        <div class="info-card">
          <div class="info-title">Model Performance</div>
          <div class="acc-display">
            <div class="acc-num">{{ (pipe.test_accuracy * 100).toFixed(1) }}%</div>
            <div class="acc-sub">Test accuracy on {{ pipe.test_seasons.join(', ') }}</div>
          </div>
          <div class="vs-baseline">
            <div class="vs-item">
              <div class="vs-num" style="color:var(--accent)">{{ (pipe.test_accuracy * 100).toFixed(1) }}%</div>
              <div class="vs-lbl">Model</div>
            </div>
            <div class="vs-item">
              <div class="vs-num" style="color:var(--muted)">{{ (pipe.baseline_home * 100).toFixed(1) }}%</div>
              <div class="vs-lbl">Baseline</div>
            </div>
            <div class="vs-item">
              <div class="vs-num" style="color:var(--win)">+{{ ((pipe.test_accuracy - pipe.baseline_home) * 100).toFixed(1) }}%</div>
              <div class="vs-lbl">Lift</div>
            </div>
          </div>
          <div class="split-divider" style="margin-top:1.25rem"></div>
          <div style="display:flex;flex-direction:column;gap:4px">
            <div class="split-row"><span class="split-label">Algorithm</span><span class="split-val" style="font-size:.8rem">HistGradientBoosting</span></div>
            <div class="split-row"><span class="split-label">Calibration</span><span class="split-val" style="font-size:.8rem">Isotonic (cv=5)</span></div>
            <div class="split-row"><span class="split-label">Log-loss</span><span class="split-val">{{ pipe.test_log_loss }}</span></div>
            <div class="split-row"><span class="split-label">Train seasons</span><span class="split-val">{{ pipe.train_seasons.length }}</span></div>
            <div class="split-row"><span class="split-label">Test seasons</span><span class="split-val" style="font-size:.78rem">{{ pipe.test_seasons.join(', ') }}</span></div>
          </div>
        </div>

        <div class="info-card">
          <div class="info-title">Top Features by Importance</div>
          <div v-if="pipe.feature_importance.length">
            <div v-for="f in pipe.feature_importance" :key="f.feature" class="feat-row">
              <div class="feat-label" :title="f.feature">{{ f.label }}</div>
              <div class="feat-bar-bg">
                <div class="feat-bar-fill" :style="{ width: featPct(f.importance, pipe.feature_importance[0].importance) }"></div>
              </div>
              <div class="feat-pct">{{ (f.importance * 100).toFixed(1) }}%</div>
            </div>
          </div>
          <div v-else class="empty" style="padding:1rem">Feature data unavailable</div>
        </div>
      </div>

      <div class="info-card" style="margin-top:1.25rem">
        <div class="info-title">Historical Outcome Distribution ({{ pipe.total_matches.toLocaleString() }} matches)</div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1.25rem;margin-top:.75rem">
          <div>
            <div style="display:flex;justify-content:space-between;font-size:.8rem;margin-bottom:6px">
              <span style="font-weight:700;color:var(--win)">Home Win</span>
              <span style="color:var(--sub)">{{ (pipe.baseline_home * 100).toFixed(1) }}%</span>
            </div>
            <div style="height:6px;background:var(--bg);border:1px solid var(--border);border-radius:3px;overflow:hidden">
              <div :style="{ width: (pipe.baseline_home * 100) + '%', height: '100%', background: 'var(--win)', borderRadius: '3px' }"></div>
            </div>
          </div>
          <div>
            <div style="display:flex;justify-content:space-between;font-size:.8rem;margin-bottom:6px">
              <span style="font-weight:700;color:var(--draw)">Draw</span>
              <span style="color:var(--sub)">{{ (pipe.baseline_draw * 100).toFixed(1) }}%</span>
            </div>
            <div style="height:6px;background:var(--bg);border:1px solid var(--border);border-radius:3px;overflow:hidden">
              <div :style="{ width: (pipe.baseline_draw * 100) + '%', height: '100%', background: 'var(--draw)', borderRadius: '3px' }"></div>
            </div>
          </div>
          <div>
            <div style="display:flex;justify-content:space-between;font-size:.8rem;margin-bottom:6px">
              <span style="font-weight:700;color:var(--loss)">Away Win</span>
              <span style="color:var(--sub)">{{ (pipe.baseline_away * 100).toFixed(1) }}%</span>
            </div>
            <div style="height:6px;background:var(--bg);border:1px solid var(--border);border-radius:3px;overflow:hidden">
              <div :style="{ width: (pipe.baseline_away * 100) + '%', height: '100%', background: 'var(--loss)', borderRadius: '3px' }"></div>
            </div>
          </div>
        </div>
        <div style="font-size:.72rem;color:var(--muted);margin-top:.875rem;line-height:1.5">
          Home teams win ~{{ (pipe.baseline_home * 100).toFixed(0) }}% of the time. The model beats the home-win baseline by {{ ((pipe.test_accuracy - pipe.baseline_home) * 100).toFixed(1) }} percentage points.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '@/composables/useApi.js'

const pipe        = ref(null)
const loadingPipe = ref(false)

function pipeIcon(name) {
  return { Ingest: '📥', Features: '⚙️', Train: '🧠', Serve: '🚀', Deploy: '☁️' }[name] || '•'
}

function featPct(val, max) {
  return max > 0 ? ((val / max) * 100).toFixed(1) + '%' : '0%'
}

onMounted(async () => {
  loadingPipe.value = true
  try { pipe.value = await apiFetch('/model/info') }
  catch { pipe.value = null }
  finally { loadingPipe.value = false }
})
</script>
