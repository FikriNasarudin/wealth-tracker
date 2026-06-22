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
      
      <!-- Placeholder for Google Auth -->
      <button class="btn btn-secondary" style="width: 100%;">
        <svg style="width: 20px; height: 20px; margin-right: 0.5rem;" viewBox="0 0 24 24">
          <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
        </svg>
        Continue with Google
      </button>
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
