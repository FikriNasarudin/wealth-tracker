<template>
  <div class="app-container">
    <Sidebar v-if="route.meta.requiresAuth" :is-open="isSidebarOpen" @close="isSidebarOpen = false" />
    <div class="main-wrapper">
      <GlobalHeader v-if="route.meta.requiresAuth" @open-menu="isSidebarOpen = true" />
      <router-view />
    </div>
    <MobileNav v-if="route.meta.requiresAuth" @open-menu="isSidebarOpen = true" />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from './components/Sidebar.vue'
import MobileNav from './components/MobileNav.vue'
import GlobalHeader from './components/GlobalHeader.vue'

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
