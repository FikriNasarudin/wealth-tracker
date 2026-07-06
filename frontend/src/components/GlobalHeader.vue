<template>
  <header class="global-header">
    <div class="header-left">
      <div class="mobile-toggle-btn" @click="$emit('open-menu')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="3" y1="12" x2="21" y2="12"/>
          <line x1="3" y1="6" x2="21" y2="6"/>
          <line x1="3" y1="18" x2="21" y2="18"/>
        </svg>
      </div>
      <div class="breadcrumb-container">
        <span class="breadcrumb-parent">Aether</span>
        <span class="breadcrumb-separator">/</span>
        <span class="breadcrumb-current">{{ pageTitle }}</span>
      </div>
    </div>

    <div class="header-right">
      <!-- Quick Action Menu -->
      <div class="quick-action-wrapper" ref="dropdownRef">
        <button class="btn btn-primary quick-action-btn" @click="toggleDropdown">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          <span class="btn-text">Quick Action</span>
        </button>

        <transition name="slide-up">
          <div v-show="isDropdownOpen" class="quick-dropdown">
            <div class="dropdown-header">Quick Creation</div>
            <button class="dropdown-item" @click="handleAction('/budgeting/history?add=true')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
              </svg>
              <span>Add Transaction</span>
            </button>
            <button class="dropdown-item" @click="handleAction('/assets/history?add=true')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
              </svg>
              <span>Add Asset Record</span>
            </button>
            <button class="dropdown-item" @click="handleAction('/liabilities/history?add=true')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/>
              </svg>
              <span>Add Liability Record</span>
            </button>
            <div class="dropdown-divider"></div>
            <button class="dropdown-item settings-item" @click="handleAction('/server-settings')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
              </svg>
              <span>Server Connection Settings</span>
            </button>
          </div>
        </transition>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

defineEmits(['open-menu'])

const route = useRoute()
const router = useRouter()
const isDropdownOpen = ref(false)
const isOnline = ref(true)
const dropdownRef = ref(null)
let connectionInterval = null

const pageTitle = computed(() => {
  const name = route.name
  if (!name) return 'Overview'
  
  const titleMap = {
    'dashboard': 'Dashboard Overview',
    'banking': 'Cash & Banking',
    'goals': 'Financial Goals',
    'budgeting': 'Monthly Budget',
    'budgeting-targets': 'Budgets & Limits',
    'budgeting-recurring': 'Bills & Subscriptions',
    'budgeting-history': 'Transaction Logs',
    'assets': 'Asset Portfolio',
    'assets-history': 'Performance History',
    'manage-assets': 'Platforms & Categories',
    'liabilities': 'Debt Overview',
    'liabilities-history': 'Payment History',
    'credit-cards': 'Manage Credit Cards',
    'manage-liabilities': 'Lenders & Categories',
    'server-settings': 'Server Connection Settings'
  }
  
  return titleMap[name] || name.charAt(0).toUpperCase() + name.slice(1)
})

const connectionTooltip = computed(() => {
  return isOnline.value 
    ? 'Successfully connected to backend server' 
    : 'Offline: Cannot contact the server'
})

const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}

const handleAction = (path) => {
  isDropdownOpen.value = false
  
  // Parse out query params if any
  const parts = path.split('?')
  if (parts.length > 1) {
    const queryParts = parts[1].split('=')
    router.push({ 
      path: parts[0], 
      query: { [queryParts[0]]: queryParts[1] } 
    })
  } else {
    router.push(path)
  }
}

const checkConnectivity = async () => {
  const backendUrl = localStorage.getItem('backend_url')
  if (!backendUrl) {
    isOnline.value = false
    return
  }
  
  try {
    // Perform a lightweight connectivity check
    await axios.get(`${backendUrl.replace(/\/$/, '')}/api/auth/config/`, { timeout: 4000 })
    isOnline.value = true
  } catch (err) {
    isOnline.value = false
  }
}

const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    isDropdownOpen.value = false
  }
}

onMounted(() => {
  checkConnectivity()
  document.addEventListener('click', handleClickOutside)
  // Poll backend health status every 20 seconds
  connectionInterval = setInterval(checkConnectivity, 20000)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  if (connectionInterval) clearInterval(connectionInterval)
})
</script>

<style scoped>
.global-header {
  height: 70px;
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  background: rgba(8, 11, 17, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.mobile-toggle-btn {
  display: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.mobile-toggle-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

.breadcrumb-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
}

.breadcrumb-parent {
  color: var(--text-muted);
  font-weight: 500;
}

.breadcrumb-separator {
  color: var(--text-muted);
  font-size: 0.8rem;
}

.breadcrumb-current {
  color: var(--text-primary);
  font-weight: 600;
  letter-spacing: 0.2px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

/* Connectivity Indicator Styling */
.connection-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-color);
  font-size: 0.75rem;
  font-weight: 600;
  transition: all var(--transition-normal);
}

.pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  position: relative;
}

.connection-badge.online {
  color: var(--success);
  border-color: rgba(16, 185, 129, 0.2);
  background: rgba(16, 185, 129, 0.04);
}

.connection-badge.online .pulse-dot {
  background: var(--success);
  box-shadow: 0 0 8px var(--success);
  animation: pulse-green 2s infinite;
}

.connection-badge.offline {
  color: var(--danger);
  border-color: rgba(239, 68, 68, 0.2);
  background: rgba(239, 68, 68, 0.04);
}

.connection-badge.offline .pulse-dot {
  background: var(--danger);
  box-shadow: 0 0 8px var(--danger);
  animation: pulse-red 2s infinite;
}

@keyframes pulse-green {
  0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
  70% { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
  100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

@keyframes pulse-red {
  0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
  70% { box-shadow: 0 0 0 6px rgba(239, 68, 68, 0); }
  100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}

/* Quick Actions Dropdown */
.quick-action-wrapper {
  position: relative;
}

.quick-action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem !important;
  font-size: 0.85rem !important;
  border-radius: var(--border-radius-sm) !important;
  font-weight: 600 !important;
}

.quick-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0 !important;
  left: auto !important;
  width: 240px;
  padding: 0.5rem 0 !important;
  z-index: 1000;
  background: #0f131e !important;
  border: 1px solid var(--border-color) !important;
  border-radius: var(--border-radius-md) !important;
  box-shadow: var(--shadow-lg) !important;
}

.dropdown-header {
  padding: 0.5rem 1rem 0.25rem 1rem;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
  letter-spacing: 0.5px;
}

.dropdown-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem 1rem;
  background: none;
  border: none;
  color: var(--text-secondary);
  font-family: var(--font-family);
  font-size: 0.875rem;
  text-align: left;
  cursor: pointer;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.dropdown-item:hover {
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-primary);
}

.dropdown-item svg {
  color: var(--text-muted);
  transition: color var(--transition-fast);
}

.dropdown-item:hover svg {
  color: var(--accent-primary);
}

.dropdown-divider {
  height: 1px;
  background: var(--border-color);
  margin: 0.5rem 0;
}

.settings-item:hover svg {
  color: var(--accent-secondary) !important;
}

/* User Profile Badge */
.user-profile-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(99, 102, 241, 0.15) 100%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  transition: transform var(--transition-fast), border-color var(--transition-fast);
}

.user-profile-badge:hover {
  transform: scale(1.05);
  border-color: rgba(255, 255, 255, 0.2);
}

.avatar-placeholder {
  font-size: 0.8rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.5px;
}

/* Transitions */
.slide-up-enter-active, .slide-up-leave-active {
  transition: opacity 0.2s cubic-bezier(0.16, 1, 0.3, 1), transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-up-enter-from, .slide-up-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

@media (max-width: 768px) {
  .global-header {
    padding: 0 1rem;
  }
  .mobile-toggle-btn {
    display: block;
  }
  .btn-text {
    display: none;
  }
  .quick-action-btn {
    padding: 0.5rem !important;
  }
  .quick-dropdown {
    right: 0 !important;
    left: auto !important;
    width: 200px !important;
  }
}
</style>
