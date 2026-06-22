import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'

import vue3GoogleLogin from 'vue3-google-login'

const app = createApp(App)

app.use(createPinia())
app.use(router)

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
if (googleClientId) {
  app.use(vue3GoogleLogin, {
    clientId: googleClientId
  })
}

app.mount('#app')
