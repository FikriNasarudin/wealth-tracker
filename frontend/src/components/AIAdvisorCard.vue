<template>
  <div class="ai-advisor-card card">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
      <h3 style="font-weight: 600; display: flex; align-items: center; gap: 0.5rem;">
        <svg style="width: 20px; height: 20px; color: var(--primary);" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        AI Financial Advisor
      </h3>
      <button class="btn btn-secondary" style="font-size: 0.75rem; padding: 0.25rem 0.5rem;" @click="fetchInsights(true)" :disabled="loading">
        {{ loading ? 'Analyzing...' : 'Refresh Insights' }}
      </button>
    </div>

    <div v-if="loading" class="skeleton-container">
      <div class="skeleton skeleton-score"></div>
      <div class="skeleton skeleton-text" style="width: 100%; margin-bottom: 0.5rem;"></div>
      <div class="skeleton skeleton-text" style="width: 90%; margin-bottom: 0.5rem;"></div>
      <div class="skeleton skeleton-text" style="width: 95%;"></div>
    </div>
    
    <div v-else-if="error" class="text-danger" style="padding: 1rem 0;">
      {{ error }}
    </div>

    <div v-else style="display: flex; gap: 1.5rem; align-items: flex-start;">
      <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; background: var(--bg-background); padding: 1rem; border-radius: 50%; width: 80px; height: 80px; border: 2px solid var(--primary);">
        <span style="font-size: 1.5rem; font-weight: 700; color: var(--primary);">{{ insights.health_score }}</span>
        <span style="font-size: 0.6rem; text-transform: uppercase; letter-spacing: 1px; color: var(--text-muted);">Health</span>
      </div>
      
      <div style="flex: 1;">
        <ul style="padding-left: 1.25rem; margin: 0; color: var(--text-color); line-height: 1.6;">
          <li v-for="(rec, index) in insights.recommendations" :key="index" style="margin-bottom: 0.5rem;">
            {{ rec }}
          </li>
        </ul>
        <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 1rem; text-align: right;">
          Last updated: {{ new Date(insights.updated_at).toLocaleString() }} 
          <span v-if="insights.cached">(Cached)</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import api from '../services/api'

const props = defineProps({
  dashboardType: {
    type: String,
    required: true
  },
  month: {
    type: Number,
    required: true
  },
  year: {
    type: Number,
    required: true
  }
})

const loading = ref(true)
const error = ref(null)
const insights = ref({
  health_score: '-',
  recommendations: [],
  cached: false,
  updated_at: null
})

const fetchInsights = async (force = false) => {
  loading.value = true
  error.value = null
  try {
    const res = await api.get(`/insights/${props.dashboardType}/?month=${props.month}&year=${props.year}&force=${force}`)
    insights.value = res.data
  } catch (err) {
    console.error(err)
    error.value = 'Failed to load AI insights. Please ensure Ollama is running.'
  } finally {
    loading.value = false
  }
}

watch(() => [props.month, props.year], () => {
  fetchInsights(false)
})

onMounted(() => {
  fetchInsights(false)
})
</script>

<style scoped>
.ai-advisor-card {
  background: linear-gradient(145deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.7));
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.skeleton-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.5rem 0;
}

.skeleton {
  background: linear-gradient(90deg, var(--bg-background) 25%, var(--border-color) 50%, var(--bg-background) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.skeleton-score {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  margin-bottom: 0.5rem;
}

.skeleton-text {
  height: 16px;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
