<template>
  <div class="app-container">
    <Sidebar v-if="route.meta.requiresAuth" :is-open="isSidebarOpen" @close="isSidebarOpen = false" />
    <div class="main-wrapper">
      <GlobalHeader v-if="route.meta.requiresAuth" @open-menu="isSidebarOpen = true" />
      <router-view />
    </div>
    <MobileNav v-if="route.meta.requiresAuth" @open-menu="isSidebarOpen = true" />

    <!-- Toast Notification -->
    <Transition name="toast">
      <div v-if="toast" class="toast-notification" :class="toast.type">
        <span class="toast-icon">{{ toast.icon }}</span>
        <div class="toast-content">
          <div class="toast-title">{{ toast.title }}</div>
          <div class="toast-message">{{ toast.message }}</div>
        </div>
        <button @click="dismissToast" class="toast-close">&times;</button>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, provide } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from './components/Sidebar.vue'
import MobileNav from './components/MobileNav.vue'
import GlobalHeader from './components/GlobalHeader.vue'

const route = useRoute()
const isSidebarOpen = ref(false)
const toast = ref(null)
let toastTimeout = null

// Close sidebar on route change automatically
watch(() => route.path, () => {
  isSidebarOpen.value = false
})

const showToast = (title, message, type = 'info', icon = 'ℹ️') => {
  toast.value = { title, message, type, icon }
  if (toastTimeout) clearTimeout(toastTimeout)
  toastTimeout = setTimeout(() => {
    dismissToast()
  }, 7000)
}

const dismissToast = () => {
  toast.value = null
}

provide('showToast', showToast)

onMounted(() => {
  if (localStorage.getItem('show_offline_toast') === 'true') {
    showToast(
      'Offline Demo Mode',
      'The backend server is not running or not configured. You are using the frontend offline mode with simulated local operations.',
      'warning',
      '⚠️'
    )
    localStorage.removeItem('show_offline_toast')
  }
})
</script>

<style>
/* Base styles handled in main.css */

/* Toast Notification Styles */
.toast-notification {
  position: fixed;
  bottom: 24px;
  right: 24px;
  max-width: 400px;
  background: rgba(15, 19, 30, 0.95);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.4);
  z-index: 9999;
}

.toast-notification.warning {
  border-left: 4px solid var(--warning, #f59e0b);
}
.toast-notification.success {
  border-left: 4px solid var(--success, #10b981);
}
.toast-notification.error {
  border-left: 4px solid var(--danger, #ef4444);
}
.toast-notification.info {
  border-left: 4px solid var(--accent-secondary, #6366f1);
}

.toast-icon {
  font-size: 1.25rem;
  line-height: 1;
}

.toast-content {
  flex: 1;
}

.toast-title {
  font-weight: 700;
  font-size: 0.95rem;
  color: #fff;
  margin-bottom: 0.25rem;
}

.toast-message {
  font-size: 0.85rem;
  color: var(--text-secondary, #94a3b8);
  line-height: 1.4;
}

.toast-close {
  background: none;
  border: none;
  color: var(--text-muted, #64748b);
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.toast-close:hover {
  color: #fff;
}

/* Toast Transitions */
.toast-enter-active,
.toast-leave-active {
  transition: all var(--transition-normal, 0.25s cubic-bezier(0.4, 0, 0.2, 1));
}
.toast-enter-from {
  opacity: 0;
  transform: translateY(30px) scale(0.95);
}
.toast-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}
</style>
