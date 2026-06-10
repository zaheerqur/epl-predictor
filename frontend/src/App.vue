<template>
  <header>
    <div class="logo">
      <div class="logo-mark"><img src="/assets/epl-logo.png" alt="EPL" /></div>
      EPL Predictor
    </div>
    <button class="nav-toggle" :class="{ open: menuOpen }" @click="menuOpen = !menuOpen" aria-label="Menu">
      <span></span>
      <span></span>
      <span></span>
    </button>
    <nav :class="{ open: menuOpen }">
      <router-link class="nav-btn" to="/about"    @click="menuOpen = false">About</router-link>
      <router-link class="nav-btn" to="/predict"  @click="menuOpen = false">Predict</router-link>
      <router-link class="nav-btn" to="/backtest" @click="menuOpen = false">Backtesting</router-link>
      <router-link class="nav-btn" to="/table"    @click="menuOpen = false">Table</router-link>
      <router-link class="nav-btn" to="/teams"    @click="menuOpen = false">Teams</router-link>
      <router-link class="nav-btn" to="/pipeline" @click="menuOpen = false">Pipeline</router-link>
    </nav>
  </header>

  <main>
    <div v-if="offline" class="notice">
      API unavailable – if running locally, start with
      <code>uvicorn api.main:app --port 8000</code>
    </div>
    <router-view />
  </main>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAppState } from '@/composables/useAppState.js'

const { offline, init } = useAppState()
const menuOpen = ref(false)
const route = useRoute()

watch(route, () => { menuOpen.value = false })
onMounted(init)
</script>
