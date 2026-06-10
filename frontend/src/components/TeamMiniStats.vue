<template>
  <div class="team-mini-stats">
    <div class="tms-form">
      <div v-for="f in preview.form.slice(0, 5)" :key="f.date"
           :class="'fdot fdot-' + f.result"
           :title="`${f.result} ${f.goals_for}-${f.goals_against} vs ${f.opponent}`">
        {{ f.result }}
      </div>
    </div>
    <div class="tms-row">
      <div class="tms-stat">
        <div class="tms-n" style="color:var(--win)">{{ preview.won }}</div>
        <div class="tms-l">W</div>
      </div>
      <div class="tms-stat">
        <div class="tms-n" style="color:var(--draw)">{{ preview.drawn }}</div>
        <div class="tms-l">D</div>
      </div>
      <div class="tms-stat">
        <div class="tms-n" style="color:var(--loss)">{{ preview.lost }}</div>
        <div class="tms-l">L</div>
      </div>
      <div class="tms-sep"></div>
      <div class="tms-stat">
        <div class="tms-n">{{ preview.goals_for }}</div>
        <div class="tms-l">GF</div>
      </div>
      <div class="tms-stat">
        <div class="tms-n">{{ preview.goals_against }}</div>
        <div class="tms-l">GA</div>
      </div>
      <div class="tms-sep"></div>
      <div class="tms-stat">
        <div class="tms-n tms-pts">{{ Number(preview.points_per_game).toFixed(2) }}</div>
        <div class="tms-l">PPG</div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({ preview: Object })
</script>
