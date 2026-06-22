<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2 style="text-align: center; margin-bottom: 2rem; color: var(--text-primary);">Create Account</h2>
      
      <div class="form-group">
        <label class="form-label">First Name</label>
        <input v-model="firstName" type="text" class="form-input" placeholder="John" />
      </div>

      <div class="form-group">
        <label class="form-label">Last Name</label>
        <input v-model="lastName" type="text" class="form-input" placeholder="Doe" />
      </div>

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
      
      <button class="btn btn-primary" style="width: 100%; margin-bottom: 1rem;" @click="register">
        Sign Up
      </button>

      <div style="text-align: center; margin-top: 1rem; font-size: 0.875rem;">
        <span style="color: var(--text-muted);">Already have an account? </span>
        <router-link to="/login" style="color: var(--primary); text-decoration: none; font-weight: 500;">Sign In</router-link>
      </div>
      
      <div v-if="googleEnabled" style="text-align: center; color: var(--text-muted); margin: 1.5rem 0;">OR</div>
      
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
const firstName = ref('')
const lastName = ref('')
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
    error.value = err.response?.data?.non_field_errors?.[0] || 'Google registration failed or is disabled'
  }
}

const register = async () => {
  if (!email.value || !password.value) {
    error.value = 'Email and password are required'
    return
  }

  try {
    error.value = ''
    // 1. Register the user
    await api.post('/auth/register/', {
      email: email.value,
      password: password.value,
      first_name: firstName.value,
      last_name: lastName.value
    })
    
    // 2. Automatically log them in after registration
    const { data } = await api.post('/auth/login/', {
      email: email.value,
      password: password.value
    })
    
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    router.push('/')
  } catch (err) {
    if (err.response?.data?.email) {
      error.value = err.response.data.email[0]
    } else {
      error.value = 'Registration failed. Please try again.'
    }
  }
}
</script>
