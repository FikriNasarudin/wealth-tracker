<template>
  <div class="tooltip-wrapper" @mouseenter="show = true" @mouseleave="show = false">
    <div class="tooltip-icon">
      <svg style="width: 16px; height: 16px;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    </div>
    <div v-if="show" class="tooltip-box">
      <p style="margin: 0; font-weight: 600;">{{ title }}</p>
      <p style="margin: 0.5rem 0 0 0; font-size: 0.875rem;">{{ description }}</p>
      <div v-if="example" style="margin-top: 0.5rem; font-size: 0.875rem; color: var(--accent-primary);">
        <em>e.g., {{ example }}</em>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  title: String,
  description: String,
  example: String
})

const show = ref(false)
</script>

<style scoped>
.tooltip-wrapper {
  position: relative;
  display: inline-block;
  margin-left: 0.25rem;
  cursor: help;
  vertical-align: middle;
}

.tooltip-wrapper:hover {
  z-index: 9999;
}

.tooltip-icon {
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
}

.tooltip-icon:hover {
  color: var(--primary);
}

.tooltip-box {
  position: absolute;
  bottom: 125%;
  left: 50%;
  transform: translateX(-50%);
  width: max-content;
  max-width: 250px;
  background: rgb(18, 25, 41);
  border: 1px solid var(--border-color);
  padding: 1rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  color: var(--text-primary);
  text-align: left;
}

.tooltip-box::after {
  content: "";
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: var(--border-color) transparent transparent transparent;
}
</style>
