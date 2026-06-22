<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2 style="text-align: center; margin-bottom: 2rem; color: var(--text-primary);">Wealth Tracker</h2>
      
      <div class="form-group">
        <label class="form-label">Email</label>
        <input v-model="email" type="email" class="form-input" placeholder="you@example.com" />
      </div>
      
      <div class="form-group">
        <label class="form-label">Password</label>
        <input v-model="password" type="password" class="form-input" placeholder="••••••••" />
      </div>
      
      <div style="color: var(--danger); margin-bottom: 1rem; font-size: 0.875rem;" v-if="error">
        {{ error }}
      </div>
      
      <button class="btn btn-primary" style="width: 100%; margin-bottom: 1rem;" @click="login">
        Sign In
      </button>
      
      <div style="text-align: center; color: var(--text-muted); margin: 1.5rem 0;">OR</div>
      
      <!-- Optional Google Auth -->
      <GoogleLogin v-if="googleEnabled" :callback="handleGoogleLogin" style="width: 100%; display: flex; justify-content: center; margin-top: 1rem;" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref('')
const googleEnabled = !!import.meta.env.VITE_GOOGLE_CLIENT_ID

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
    error.value = 'Invalid email or password'
  }
}
</script>
