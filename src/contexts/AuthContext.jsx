import { createContext, useState, useContext, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export default function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('inventory_token'))
  const [loading, setLoading] = useState(true)

  const isAuthenticated = !!token && !!user

  // Check auth on mount
  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const savedToken = localStorage.getItem('inventory_token')
    if (savedToken) {
      try {
        const response = await api.get('/auth/me')
        setUser(response.data)
        setToken(savedToken)
      } catch (error) {
        localStorage.removeItem('inventory_token')
        setToken(null)
        setUser(null)
      }
    }
    setLoading(false)
  }

  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password })
      const { access_token, user: userData } = response.data

      localStorage.setItem('inventory_token', access_token)
      setToken(access_token)
      setUser(userData)

      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Error de conexión'
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('inventory_token')
    setToken(null)
    setUser(null)
    window.location.href = '/login'
  }

  const value = {
    user,
    token,
    isAuthenticated,
    loading,
    login,
    logout,
    checkAuth
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
