import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api'
})

// Request interceptor: Add token to headers
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('inventory_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor: Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('inventory_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
