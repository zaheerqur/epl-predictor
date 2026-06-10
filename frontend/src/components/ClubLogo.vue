<template>
  <div class="club-logo" :style="style">
    <img v-if="logoUrl" :src="logoUrl" :class="{ loaded: imgLoaded }"
         @load="imgLoaded = true" @error="imgLoaded = false" />
    <span class="abbr">{{ abbrText }}</span>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { COLORS, LOGOS, getAbbr } from '@/data/teams.js'

const props = defineProps({ team: String })

const imgLoaded = ref(false)

const style = computed(() => {
  const [bg, fg] = COLORS[props.team] || ['#334155', '#fff']
  return { '--team-bg': bg, '--team-fg': fg }
})

const logoUrl  = computed(() => LOGOS[props.team] || '')
const abbrText = computed(() => getAbbr(props.team))
</script>
