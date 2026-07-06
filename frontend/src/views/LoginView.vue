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
      <p style="text-align: center; color: var(--text-secondary); margin-bottom: 2rem; font-size: 0.95rem;">Track your assets, budgets, and investment performance</p>
      
      <div class="form-group">
        <label class="form-label">Email Address</label>
        <input v-model="email" type="email" class="form-input" placeholder="you@example.com" />
      </div>
      
      <div class="form-group">
        <label class="form-label">Password</label>
        <input v-model="password" type="password" class="form-input" placeholder="••••••••" />
      </div>
      
      <div style="color: var(--danger); margin-bottom: 1.5rem; font-size: 0.875rem;" v-if="error">
        {{ error }}
      </div>
      
      <button class="btn btn-primary" style="width: 100%; margin-bottom: 1.5rem; padding: 0.875rem;" @click="login">
        Sign In
      </button>
      
      <div style="text-align: center; font-size: 0.875rem; margin-bottom: 0.5rem;">
        <span style="color: var(--text-muted);">Don't have an account? </span>
        <router-link to="/register" style="color: var(--accent-primary); text-decoration: none; font-weight: 600;">Sign Up</router-link>
      </div>
      
      <div style="text-align: center; color: var(--text-muted); margin: 1.5rem 0;">OR</div>
      
      <!-- Optional Google Auth -->
      <GoogleLogin v-if="googleEnabled" :callback="handleGoogleLogin" style="width: 100%; display: flex; justify-content: center; margin-top: 1rem;" />
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref('')
const googleEnabled = inject('googleEnabled', false)

const handleGoogleLogin = async (response) => {
  try {
    error.value = ''
    const { data } = await api.post('/auth/google/', {
      token: response.credential
    })
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    router.push('/')
  } catch (err) {
    console.error('Google login failed:', err)
    error.value = err.response?.data?.non_field_errors?.[0] || 'Google login failed or is disabled on the server'
  }
}

const login = async () => {
  try {
    error.value = ''
    const { data } = await api.post('/auth/login/', {
      email: email.value,
      password: password.value
    })
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    router.push('/')
  } catch (err) {
    console.error('Login failed:', err)
    if (!err.response) {
      // Backend not setup/reachable, fallback to frontend-only demo
      localStorage.setItem('access_token', 'mock_access_token')
      localStorage.setItem('refresh_token', 'mock_refresh_token')
      localStorage.setItem('show_offline_toast', 'true')
      router.push('/')
    } else {
      error.value = 'Invalid email or password'
    }
  }
}
</script>
