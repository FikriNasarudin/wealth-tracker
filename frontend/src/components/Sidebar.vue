<template>
  <div v-if="isOpen" class="sidebar-backdrop" @click="$emit('close')"></div>
  <aside class="sidebar" :class="{ open: isOpen }">
    <div class="sidebar-header">
      <h2>Wealth Tracker</h2>
    </div>
    <nav class="sidebar-nav">
      <router-link to="/" class="nav-item">Dashboard</router-link>

      <!-- Budgeting Menu -->
      <div class="menu-group">
        <button class="nav-item menu-toggle" @click="toggleMenu('budgeting')" :class="{ active: openMenus.budgeting || isActivePrefix('/budgeting') }">
          <span>Budgeting</span>
          <span class="chevron" :class="{ open: openMenus.budgeting }">▼</span>
        </button>
        <div class="submenu" v-show="openMenus.budgeting">
          <router-link to="/budgeting" class="submenu-item" exact-active-class="active">Overview</router-link>
          <router-link to="/budgeting/history" class="submenu-item" active-class="active">History</router-link>
        </div>
      </div>

      <!-- Investments Menu -->
      <div class="menu-group">
        <button class="nav-item menu-toggle" @click="toggleMenu('investments')" :class="{ active: openMenus.investments || isActivePrefix('/investments') }">
          <span>Investments</span>
          <span class="chevron" :class="{ open: openMenus.investments }">▼</span>
        </button>
        <div class="submenu" v-show="openMenus.investments">
          <router-link to="/investments" class="submenu-item" exact-active-class="active">Overview</router-link>
          <router-link to="/investments/history" class="submenu-item" active-class="active">History</router-link>
        </div>
      </div>

      <!-- Liabilities Menu -->
      <div class="menu-group">
        <button class="nav-item menu-toggle" @click="toggleMenu('liabilities')" :class="{ active: openMenus.liabilities || isActivePrefix('/liabilities') }">
          <span>Liabilities</span>
          <span class="chevron" :class="{ open: openMenus.liabilities }">▼</span>
        </button>
        <div class="submenu" v-show="openMenus.liabilities">
          <router-link to="/liabilities" class="submenu-item" exact-active-class="active">Overview</router-link>
          <router-link to="/liabilities/history" class="submenu-item" active-class="active">History</router-link>
        </div>
      </div>

    </nav>
    <div class="sidebar-footer">
      <button class="btn btn-secondary" style="width: 100%; margin-bottom: 0.5rem;" @click="replayTutorial">Help / Tutorial</button>
      <button class="btn btn-danger" style="width: 100%" @click="logout">Logout</button>
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
  investments: false,
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
    if (newPath.startsWith('/investments')) openMenus.value.investments = true
    if (newPath.startsWith('/liabilities')) openMenus.value.liabilities = true
  },
  { immediate: true }
)

const replayTutorial = () => {
  localStorage.removeItem('tutorial_completed')
  if (route.path === '/') {
    window.location.search = '?tutorial=1'
  } else {
    router.push('/?tutorial=1')
  }
}

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
  background: var(--bg-card);
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
  background: rgba(10, 15, 28, 0.8);
  backdrop-filter: blur(4px);
  z-index: 1500;
}

.sidebar-header {
  padding: 2rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.sidebar-header h2 {
  font-size: 1.25rem;
  font-weight: 700;
  background: var(--accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
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
  display: block;
}

.nav-item:hover, .menu-toggle:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

.nav-item.router-link-exact-active, .nav-item.router-link-active {
  background: var(--accent-primary);
  color: #fff;
  box-shadow: var(--shadow-glow);
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
