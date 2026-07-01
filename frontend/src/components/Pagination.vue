<template>
  <div v-if="totalPages > 1 || totalItems > 0" class="pagination-container">
    <div class="pagination-info">
      Showing <span>{{ startItem }}</span> to <span>{{ endItem }}</span> of <span>{{ totalItems }}</span> entries
    </div>
    <div class="pagination-buttons">
      <button 
        class="pagination-btn" 
        :disabled="modelValue === 1" 
        @click="changePage(modelValue - 1)"
      >
        Prev
      </button>
      
      <template v-for="(page, idx) in visiblePages" :key="idx">
        <span v-if="page === '...'" class="pagination-ellipsis">...</span>
        <button 
          v-else
          class="pagination-btn" 
          :class="{ active: modelValue === page }"
          @click="changePage(page)"
        >
          {{ page }}
        </button>
      </template>

      <button 
        class="pagination-btn" 
        :disabled="modelValue === totalPages" 
        @click="changePage(modelValue + 1)"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Number,
    required: true
  },
  totalItems: {
    type: Number,
    required: true
  },
  itemsPerPage: {
    type: Number,
    default: 10
  }
})

const emit = defineEmits(['update:modelValue'])

const totalPages = computed(() => Math.ceil(props.totalItems / props.itemsPerPage) || 1)

const startItem = computed(() => {
  if (props.totalItems === 0) return 0
  return (props.modelValue - 1) * props.itemsPerPage + 1
})

const endItem = computed(() => {
  return Math.min(props.modelValue * props.itemsPerPage, props.totalItems)
})

const visiblePages = computed(() => {
  const current = props.modelValue
  const total = totalPages.value
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }
  
  const pages = [1]
  
  if (current > 3) {
    pages.push('...')
  }
  
  const start = Math.max(2, current - 1)
  const end = Math.min(total - 1, current + 1)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  if (current < total - 2) {
    pages.push('...')
  }
  
  pages.push(total)
  
  return pages
})

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    emit('update:modelValue', page)
  }
}
</script>

<style scoped>
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
  font-size: 0.875rem;
  color: var(--text-secondary);
  flex-wrap: wrap;
  gap: 1rem;
}

.pagination-info span {
  font-weight: 600;
  color: var(--text-primary);
}

.pagination-buttons {
  display: flex;
  gap: 0.35rem;
  align-items: center;
}

.pagination-btn {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 0.4rem 0.8rem;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-size: 0.875rem;
  transition: all var(--transition-fast);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
}

.pagination-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--text-secondary);
}

.pagination-btn.active {
  background: var(--accent-gradient);
  color: #fff;
  border-color: transparent;
  font-weight: 600;
}

.pagination-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pagination-ellipsis {
  padding: 0 0.25rem;
  color: var(--text-muted);
}
</style>
