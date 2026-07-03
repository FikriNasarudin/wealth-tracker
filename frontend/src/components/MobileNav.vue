<template>
  <nav class="mobile-nav">
    <router-link to="/" class="mobile-nav-item" exact-active-class="active">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
        <polyline points="9 22 9 12 15 12 15 22"/>
      </svg>
      <span>Home</span>
    </router-link>

    <router-link to="/assets" class="mobile-nav-item" active-class="active">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="18" y1="20" x2="18" y2="10"/>
        <line x1="12" y1="20" x2="12" y2="4"/>
        <line x1="6" y1="20" x2="6" y2="14"/>
      </svg>
      <span>Assets</span>
    </router-link>

    <router-link to="/budgeting" class="mobile-nav-item" active-class="active">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="12" y1="1" x2="12" y2="23"/>
        <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
      </svg>
      <span>Budget</span>
    </router-link>

    <router-link to="/liabilities" class="mobile-nav-item" active-class="active">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/>
        <polyline points="17 18 23 18 23 12"/>
      </svg>
      <span>Liabilities</span>
    </router-link>

    <button class="mobile-nav-item more-button" @click="$emit('open-menu')">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="3" y1="12" x2="21" y2="12"/>
        <line x1="3" y1="6" x2="21" y2="6"/>
        <line x1="3" y1="18" x2="21" y2="18"/>
      </svg>
      <span>More</span>
    </button>
  </nav>
</template>

<script setup>
defineEmits(['open-menu'])
</script>

<style scoped>
.mobile-nav {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 64px;
  background: rgba(12, 16, 27, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid var(--border-color);
  justify-content: space-around;
  align-items: center;
  z-index: 1000;
  padding: 0 0.5rem;
}

.mobile-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  height: 100%;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.65rem;
  font-weight: 500;
  gap: 4px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  transition: color var(--transition-fast), transform var(--transition-fast);
}

.mobile-nav-item svg {
  transition: transform var(--transition-fast), stroke var(--transition-fast);
}

.mobile-nav-item:active svg {
  transform: scale(0.9);
}

.mobile-nav-item.active,
.mobile-nav-item.router-link-active {
  color: var(--accent-primary);
}

.mobile-nav-item.active svg,
.mobile-nav-item.router-link-active svg {
  stroke: var(--accent-primary);
}

.more-button {
  font-family: inherit;
}

@media (max-width: 768px) {
  .mobile-nav {
    display: flex;
  }
}
</style>
