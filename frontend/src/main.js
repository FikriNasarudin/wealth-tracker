import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'

import vue3GoogleLogin from 'vue3-google-login'

const app = createApp(App)

app.use(createPinia())
app.use(router)

async function initApp() {
  try {
    const response = await fetch('/api/auth/config/')
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
