<template>
  <div class="auth-container">
    <div class="auth-card">
      <div style="display: flex; align-items: center; justify-content: center; gap: 0.75rem; margin-bottom: 0.75rem;">
        <div class="brand-logo" style="display: flex; align-items: center; justify-content: center; width: 36px; height: 36px;">
          <svg width="36" height="36" viewBox="0 0 32 32" fill="none">
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
        <h2 style="font-size: 2.25rem; font-weight: 800; letter-spacing: 0.5px; background: linear-gradient(135deg, #fff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;">Aether Wealth</h2>
      </div>
      <p style="text-align: center; color: var(--text-secondary); margin-bottom: 2rem; font-size: 0.95rem;">Configure Server Settings</p>
      
      <div class="form-group">
        <label class="form-label">Backend Server URL</label>
        <input v-model="serverUrl" type="url" class="form-input" placeholder="https://wealth-api.example.com" />
        <span style="font-size: 0.75rem; color: var(--text-muted); display: block; margin-top: 0.5rem;">
          Enter the URL where your wealth tracker backend is hosted.
        </span>
      </div>
      
      <div v-if="statusMessage" :style="{ color: isSuccess ? 'var(--success)' : 'var(--danger)', marginBottom: '1.5rem', fontSize: '0.875rem' }">
        {{ statusMessage }}
      </div>
      
      <button class="btn btn-secondary" style="width: 100%; margin-bottom: 0.75rem; padding: 0.875rem;" :disabled="loading" @click="testConnection">
        {{ loading ? 'Testing...' : 'Test Connection' }}
      </button>
      
      <button class="btn btn-primary" style="width: 100%; padding: 0.875rem;" :disabled="!isSuccess" @click="saveSettings">
        Save & Continue
      </button>
      
      <div v-if="isCapacitor" style="text-align: center; font-size: 0.875rem; margin-top: 1.5rem;">
        <router-link to="/login" style="color: var(--text-muted); text-decoration: none;">Back to Login</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const serverUrl = ref('')
const loading = ref(false)
const isSuccess = ref(false)
const statusMessage = ref('')
const isCapacitor = ref(false)

onMounted(() => {
  isCapacitor.value = !!window.Capacitor
  const savedUrl = localStorage.getItem('backend_url')
  if (savedUrl) {
    serverUrl.value = savedUrl
    isSuccess.value = true
  }
})

const testConnection = async () => {
  if (!serverUrl.value) {
    statusMessage.value = 'Please enter a valid server URL.'
    isSuccess.value = false
    return
  }

  // Sanitize trailing slash
  let cleanUrl = serverUrl.value.trim().replace(/\/$/, '')
  if (!/^https?:\/\//i.test(cleanUrl)) {
    cleanUrl = 'https://' + cleanUrl
  }
  serverUrl.value = cleanUrl

  loading.value = true
  statusMessage.value = ''
  isSuccess.value = false

  try {
    const response = await axios.get(`${cleanUrl}/api/auth/config/`, { timeout: 8000 })
    if (response.status === 200) {
      statusMessage.value = 'Connection successful! Server is online.'
      isSuccess.value = true
    } else {
      statusMessage.value = 'Server responded, but configuration is invalid.'
    }
  } catch (err) {
    console.error(err)
    statusMessage.value = 'Failed to connect to the server. Make sure the URL is correct and CORS is enabled.'
  } finally {
    loading.value = false
  }
}

const saveSettings = () => {
  if (isSuccess.value) {
    localStorage.setItem('backend_url', serverUrl.value.trim())
    // Hard refresh/reload to let api.js pick up the new base URL configuration
    window.location.href = '/'
  }
}
</script>
