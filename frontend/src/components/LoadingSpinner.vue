<template>
  <div class="spinner-container" :class="{ overlay: isOverlay }">
    <div class="spinner-ring">
      <div class="spinner-circle"></div>
    </div>
    <span v-if="label" class="spinner-label">{{ label }}</span>
  </div>
</template>

<script setup>
defineProps({
  isOverlay: {
    type: Boolean,
    default: false
  },
  label: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.spinner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem;
}

.spinner-container.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(7, 9, 14, 0.75);
  backdrop-filter: blur(4px);
  z-index: 50;
  padding: 0;
}

.spinner-ring {
  width: 42px;
  height: 42px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner-circle {
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  border: 3px solid rgba(16, 185, 129, 0.1);
  border-radius: 50%;
  border-top-color: var(--accent-primary);
  border-right-color: var(--accent-secondary);
  animation: spin 0.8s cubic-bezier(0.5, 0.1, 0.5, 0.9) infinite;
}

.spinner-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  letter-spacing: 0.5px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
