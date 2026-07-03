import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'
import { Capacitor } from '@capacitor/core'

import vue3GoogleLogin from 'vue3-google-login'

const app = createApp(App)

app.use(createPinia())
app.use(router)

const getBackendUrl = () => {
  const savedUrl = localStorage.getItem('backend_url')
  return savedUrl ? savedUrl.trim().replace(/\/$/, '') : ''
}

const getBaseURL = () => {
  const backend = getBackendUrl()
  return backend ? `${backend}/api` : '/api'
}

async function initApp() {
  const backendUrl = localStorage.getItem('backend_url')
  const isNative = Capacitor.isNativePlatform()
  
  if (isNative && !backendUrl) {
    app.provide('googleEnabled', false)
    app.mount('#app')
    return
  }

  try {
    const response = await fetch(`${getBaseURL()}/auth/config/`)
    if (response.ok) {
      const data = await response.json()
      if (data.google_client_id) {
        app.use(vue3GoogleLogin, { clientId: data.google_client_id })
        app.provide('googleEnabled', true)
      } else {
        app.provide('googleEnabled', false)
      }
    } else {
      app.provide('googleEnabled', false)
    }
  } catch (error) {
    console.error('Failed to fetch auth config:', error)
    app.provide('googleEnabled', false)
  }

  app.mount('#app')
}

initApp()
