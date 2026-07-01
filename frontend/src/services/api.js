import axios from 'axios'
import router from '../router'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config
    
    // If it's a 401 error and not on an auth endpoint
    if (
      error.response &&
      error.response.status === 401 &&
      !originalRequest.url.includes('/auth/login/') &&
      !originalRequest.url.includes('/auth/google/') &&
      !originalRequest._retry
    ) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then(token => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return api(originalRequest)
          })
          .catch(err => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          // Use axios directly to avoid interceptors on the refresh call
          const { data } = await axios.post('/api/auth/login/refresh/', {
            refresh: refreshToken
          })
          
          const newAccessToken = data.access
          localStorage.setItem('access_token', newAccessToken)
          
          api.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
          
          processQueue(null, newAccessToken)
          isRefreshing = false
          
          return api(originalRequest)
        } catch (refreshError) {
          processQueue(refreshError, null)
          isRefreshing = false
          
          // Clear credentials and logout
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          if (router.currentRoute.value.path !== '/login') {
            router.push('/login')
          }
          return Promise.reject(refreshError)
        }
      } else {
        // No refresh token, logout
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        if (router.currentRoute.value.path !== '/login') {
          router.push('/login')
        }
      }
    }
    
    return Promise.reject(error)
  }
)

export default api
