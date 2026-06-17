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
      <a class="nav-btn nav-github" href="https://github.com/zaheerqur/epl-predictor" target="_blank" rel="noopener noreferrer" aria-label="GitHub">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
        </svg>
      </a>
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
