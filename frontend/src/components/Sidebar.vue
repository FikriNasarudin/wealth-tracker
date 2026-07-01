<template>
  <div v-if="isOpen" class="sidebar-backdrop" @click="$emit('close')"></div>
  <aside class="sidebar" :class="{ open: isOpen }">
    <div class="sidebar-header" style="display: flex; align-items: center; gap: 0.75rem;">
      <div class="brand-logo" style="display: flex; align-items: center; justify-content: center; width: 32px; height: 32px;">
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
          <circle cx="16" cy="16" r="14" stroke="url(#logoGrad)" stroke-width="2.5" />
          <path d="M11 20L16 11L21 20H11Z" fill="url(#logoGrad)" />
          <circle cx="16" cy="15" r="2" fill="#fff" />
          <defs>
            <linearGradient id="logoGrad" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
              <stop stop-color="#10b981" />
              <stop offset="1" stop-color="#6366f1" />
            </linearGradient>
          </defs>
        </svg>
      </div>
      <h2 style="font-size: 1.25rem; font-weight: 700; letter-spacing: 0.5px; background: linear-gradient(135deg, #fff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Aether Wealth</h2>
    </div>
    
    <nav class="sidebar-nav">
      <router-link to="/" class="nav-item" style="display: flex; align-items: center; gap: 0.75rem;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/></svg>
        <span>Dashboard</span>
      </router-link>

      <!-- Banking Link -->
      <router-link to="/banking" class="nav-item" style="display: flex; align-items: center; gap: 0.75rem;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>
        <span>Cash & Banking</span>
      </router-link>

      <!-- Goals Link -->
      <router-link to="/goals" class="nav-item" style="display: flex; align-items: center; gap: 0.75rem;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
        <span>Financial Goals</span>
      </router-link>

      <!-- Budgeting Menu -->
      <div class="menu-group">
        <button class="nav-item menu-toggle" @click="toggleMenu('budgeting')" :class="{ active: openMenus.budgeting || isActivePrefix('/budgeting') }" style="display: flex; align-items: center; gap: 0.75rem; justify-content: flex-start;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
          <span style="flex: 1; text-align: left;">Budgeting</span>
          <span class="chevron" :class="{ open: openMenus.budgeting }">▼</span>
        </button>
        <div class="submenu" v-show="openMenus.budgeting">
          <router-link to="/budgeting" class="submenu-item" exact-active-class="active">Monthly Budget</router-link>
          <router-link to="/budgeting/targets" class="submenu-item" active-class="active">Budgets & Limits</router-link>
          <router-link to="/budgeting/recurring" class="submenu-item" active-class="active">Bills & Subscriptions</router-link>
          <router-link to="/budgeting/history" class="submenu-item" active-class="active">Transaction Logs</router-link>
        </div>
      </div>

      <!-- Assets Menu -->
      <div class="menu-group">
        <button class="nav-item menu-toggle" @click="toggleMenu('assets')" :class="{ active: openMenus.assets || isActivePrefix('/assets') }" style="display: flex; align-items: center; gap: 0.75rem; justify-content: flex-start;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
          <span style="flex: 1; text-align: left;">Assets</span>
          <span class="chevron" :class="{ open: openMenus.assets }">▼</span>
        </button>
        <div class="submenu" v-show="openMenus.assets">
          <router-link to="/assets" class="submenu-item" exact-active-class="active">Asset Portfolio</router-link>
          <router-link to="/assets/history" class="submenu-item" active-class="active">Performance History</router-link>
          <router-link to="/assets/manage" class="submenu-item" active-class="active">Platforms & Categories</router-link>
        </div>
      </div>

      <!-- Liabilities Menu -->
      <div class="menu-group">
        <button class="nav-item menu-toggle" @click="toggleMenu('liabilities')" :class="{ active: openMenus.liabilities || isActivePrefix('/liabilities') }" style="display: flex; align-items: center; gap: 0.75rem; justify-content: flex-start;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>
          <span style="flex: 1; text-align: left;">Liabilities</span>
          <span class="chevron" :class="{ open: openMenus.liabilities }">▼</span>
        </button>
        <div class="submenu" v-show="openMenus.liabilities">
          <router-link to="/liabilities" class="submenu-item" exact-active-class="active">Debt Overview</router-link>
          <router-link to="/liabilities/history" class="submenu-item" active-class="active">Payment History</router-link>
          <router-link to="/liabilities/credit-cards" class="submenu-item" active-class="active">Manage Credit Cards</router-link>
          <router-link to="/liabilities/manage" class="submenu-item" active-class="active">Lenders & Categories</router-link>
        </div>
      </div>
    </nav>
    <div class="sidebar-footer">
      <button class="btn btn-danger" style="width: 100%; display: flex; align-items: center; justify-content: center; gap: 0.5rem;" @click="logout">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
        <span>Logout</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

const router = useRouter()
const route = useRoute()

const openMenus = ref({
  budgeting: false,
  assets: false,
  liabilities: false
})

const toggleMenu = (menu) => {
  openMenus.value[menu] = !openMenus.value[menu]
}

const isActivePrefix = (prefix) => {
  return route.path.startsWith(prefix)
}

// Automatically open the menu if the user is on a route within it
watch(
  () => route.path,
  (newPath) => {
    if (newPath.startsWith('/budgeting')) openMenus.value.budgeting = true
    if (newPath.startsWith('/assets')) openMenus.value.assets = true
    if (newPath.startsWith('/liabilities')) openMenus.value.liabilities = true
  },
  { immediate: true }
)



const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  router.push('/login')
}
</script>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  background: rgba(12, 16, 27, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: transform var(--transition-normal);
  z-index: 2000;
}

.sidebar-backdrop {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(5, 7, 12, 0.85);
  backdrop-filter: blur(8px);
  z-index: 1500;
}

.sidebar-header {
  padding: 2rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.sidebar-header h2 {
  font-size: 1.25rem;
  font-weight: 700;
}

.sidebar-nav {
  flex: 1;
  padding: 1.5rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  overflow-y: auto;
}

.nav-item {
  padding: 0.75rem 1rem;
  border-radius: var(--border-radius-sm);
  color: var(--text-secondary);
  font-weight: 500;
  transition: all var(--transition-fast);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border-left: 3px solid transparent;
}

.nav-item:hover, .menu-toggle:hover {
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-primary);
}

.nav-item.router-link-exact-active, .nav-item.router-link-active {
  background: rgba(16, 185, 129, 0.08);
  color: var(--accent-primary);
  border-left: 3px solid var(--accent-primary);
  box-shadow: none;
}

/* Menu Toggle Button */
.menu-group {
  display: flex;
  flex-direction: column;
}

.menu-toggle {
  background: none;
  border: none;
  width: 100%;
  text-align: left;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  font-family: inherit;
  font-size: 1rem;
}

.menu-toggle.active {
  color: var(--text-primary);
}

/* We don't want the toggle button to be fully blue like an active link, just highlighted text */
button.nav-item.router-link-active {
  background: transparent;
  box-shadow: none;
}

.chevron {
  font-size: 0.75rem;
  transition: transform var(--transition-fast);
}

.chevron.open {
  transform: rotate(180deg);
}

.submenu {
  display: flex;
  flex-direction: column;
  padding-left: 1rem;
  margin-top: 0.25rem;
  gap: 0.25rem;
}

.submenu-item {
  padding: 0.5rem 1rem;
  border-radius: var(--border-radius-sm);
  color: var(--text-muted);
  font-size: 0.875rem;
  transition: all var(--transition-fast);
  text-decoration: none;
}

.submenu-item:hover {
  color: var(--text-primary);
}

.submenu-item.active {
  color: var(--accent-primary);
  font-weight: 600;
  background: rgba(59, 130, 246, 0.1);
}

.sidebar-footer {
  padding: 1.5rem;
  border-top: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
  }
  
  .sidebar.open {
    transform: translateX(0);
  }
  
  .sidebar-backdrop {
    display: block;
  }
}
</style>
