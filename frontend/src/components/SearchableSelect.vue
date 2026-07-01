<template>
  <div class="searchable-select" ref="containerRef" :class="{ 'is-disabled': disabled }">
    <div 
      class="select-trigger" 
      :class="{ 'is-open': isOpen }"
      @click="toggleDropdown"
      tabindex="0"
      @keydown.down.prevent="onKeyDownDown"
      @keydown.up.prevent="onKeyDownUp"
      @keydown.enter.prevent="onKeyDownEnter"
      @keydown.esc.prevent="isOpen = false"
    >
      <span v-if="selectedLabel" class="selected-text">{{ selectedLabel }}</span>
      <span v-else class="placeholder-text">{{ placeholder || 'Select option...' }}</span>
      <span class="chevron-arrow">▼</span>
    </div>

    <transition name="fade-slide">
      <div v-if="isOpen" class="dropdown-menu">
        <div class="search-container">
          <input 
            ref="searchInputRef"
            v-model="searchQuery" 
            type="text" 
            class="form-input search-input" 
            placeholder="Search..." 
            @click.stop
            @keydown.down.prevent="onKeyDownDown"
            @keydown.up.prevent="onKeyDownUp"
            @keydown.enter.prevent="onKeyDownEnter"
            @keydown.esc.prevent="isOpen = false"
          />
        </div>
        <ul class="options-list" ref="listRef">
          <li 
            v-if="filteredOptions.length === 0" 
            class="no-results"
          >
            No matches found
          </li>
          <li 
            v-for="(opt, idx) in filteredOptions" 
            :key="opt.value" 
            class="option-item"
            :class="{ 'is-selected': modelValue === opt.value, 'is-highlighted': highlightedIndex === idx }"
            @click.stop="selectOption(opt)"
          >
            {{ opt.label }}
          </li>
        </ul>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number, Boolean],
    default: null
  },
  options: {
    type: Array,
    required: true
  },
  placeholder: {
    type: String,
    default: 'Select or search...'
  },
  required: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const isOpen = ref(false)
const searchQuery = ref('')
const containerRef = ref(null)
const searchInputRef = ref(null)
const listRef = ref(null)
const highlightedIndex = ref(-1)

// Normalize options to ensure they always have value & label
const normalizedOptions = computed(() => {
  return props.options.map(opt => {
    if (typeof opt === 'object' && opt !== null) {
      return {
        value: opt.value !== undefined ? opt.value : (opt.id !== undefined ? opt.id : opt.name),
        label: opt.label || opt.name || String(opt.value || opt.id || '')
      }
    }
    return { value: opt, label: String(opt) }
  })
})

const selectedLabel = computed(() => {
  const matched = normalizedOptions.value.find(opt => opt.value === props.modelValue)
  return matched ? matched.label : ''
})

const filteredOptions = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()
  if (!query) return normalizedOptions.value
  return normalizedOptions.value.filter(opt => 
    opt.label.toLowerCase().includes(query)
  )
})

watch(isOpen, (newVal) => {
  if (newVal) {
    searchQuery.value = ''
    highlightedIndex.value = -1
    nextTick(() => {
      if (searchInputRef.value) {
        searchInputRef.value.focus()
      }
    })
  }
})

const toggleDropdown = () => {
  if (props.disabled) return
  isOpen.value = !isOpen.value
}

const selectOption = (opt) => {
  emit('update:modelValue', opt.value)
  emit('change', opt.value)
  isOpen.value = false
}

// Click outside logic
const handleClickOutside = (event) => {
  if (containerRef.value && !containerRef.value.contains(event.target)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})

// Keyboard navigation
const onKeyDownDown = () => {
  if (!isOpen.value) {
    isOpen.value = true
    return
  }
  if (filteredOptions.value.length === 0) return
  highlightedIndex.value = (highlightedIndex.value + 1) % filteredOptions.value.length
  scrollToHighlighted()
}

const onKeyDownUp = () => {
  if (!isOpen.value) return
  if (filteredOptions.value.length === 0) return
  if (highlightedIndex.value <= 0) {
    highlightedIndex.value = filteredOptions.value.length - 1
  } else {
    highlightedIndex.value--
  }
  scrollToHighlighted()
}

const onKeyDownEnter = () => {
  if (!isOpen.value) {
    isOpen.value = true
    return
  }
  if (highlightedIndex.value >= 0 && highlightedIndex.value < filteredOptions.value.length) {
    selectOption(filteredOptions.value[highlightedIndex.value])
  }
}

const scrollToHighlighted = () => {
  nextTick(() => {
    if (!listRef.value) return
    const listEl = listRef.value
    const highlightedEl = listEl.children[highlightedIndex.value]
    if (!highlightedEl) return

    const elTop = highlightedEl.offsetTop
    const elBottom = elTop + highlightedEl.offsetHeight
    const viewTop = listEl.scrollTop
    const viewBottom = viewTop + listEl.offsetHeight

    if (elTop < viewTop) {
      listEl.scrollTop = elTop
    } else if (elBottom > viewBottom) {
      listEl.scrollTop = elBottom - listEl.offsetHeight
    }
  })
}
</script>

<style scoped>
.searchable-select {
  position: relative;
  width: 100%;
  user-select: none;
}

.select-trigger {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 0.6rem 1rem;
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  color: var(--text-primary);
  font-size: 0.875rem;
  transition: all var(--transition-fast);
  outline: none;
  height: 42px; /* Standard form input height */
  box-sizing: border-box;
}

.select-trigger:focus, .select-trigger.is-open {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.placeholder-text {
  color: var(--text-muted);
}

.chevron-arrow {
  font-size: 0.7rem;
  color: var(--text-muted);
  transition: transform var(--transition-fast);
}

.select-trigger.is-open .chevron-arrow {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 105%;
  left: 0;
  right: 0;
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  max-height: 250px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.search-container {
  padding: 0.5rem;
  border-bottom: 1px solid var(--border-color);
  background-color: rgba(255, 255, 255, 0.01);
}

.search-input {
  width: 100%;
  padding: 0.4rem 0.75rem;
  font-size: 0.875rem;
  background-color: var(--bg-background) !important;
  border-color: var(--border-color) !important;
  height: 34px;
}

.options-list {
  list-style: none;
  padding: 0;
  margin: 0;
  overflow-y: auto;
  max-height: 180px;
}

.option-item {
  padding: 0.6rem 1rem;
  font-size: 0.875rem;
  color: var(--text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.option-item:hover, .option-item.is-highlighted {
  background-color: rgba(59, 130, 246, 0.15);
  color: white;
}

.option-item.is-selected {
  background-color: var(--primary);
  color: white;
  font-weight: 500;
}

.no-results {
  padding: 1rem;
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.is-disabled .select-trigger {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
}

/* Animations */
.fade-slide-enter-active, .fade-slide-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.fade-slide-enter-from, .fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-5px);
}
</style>
