<template>
  <div class="app-container">
    <button id="tour-mobile-menu" v-if="route.meta.requiresAuth" class="mobile-menu-toggle" @click="isSidebarOpen = true" aria-label="Open menu">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M3 12h18M3 6h18M3 18h18" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>
    <Sidebar v-if="route.meta.requiresAuth" :is-open="isSidebarOpen" @close="isSidebarOpen = false" />
    <div class="main-wrapper">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from './components/Sidebar.vue'

const route = useRoute()
const isSidebarOpen = ref(false)

// Close sidebar on route change automatically
watch(() => route.path, () => {
  isSidebarOpen.value = false
})
</script>

<style>
/* Base styles handled in main.css */
</style>
