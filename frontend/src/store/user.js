import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authAPI } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')

  function setUser(userData) {
    user.value = userData
    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData))
    } else {
      localStorage.removeItem('user')
    }
  }

  function setToken(newToken) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('token', newToken)
    } else {
      localStorage.removeItem('token')
    }
  }

  async function login(credentials) {
    const res = await authAPI.login(credentials)
    setToken(res.access_token)
    setUser(res.user)
    return res
  }

  async function register(userData) {
    const res = await authAPI.register(userData)
    return res
  }

  async function logout() {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setToken('')
      setUser(null)
    }
  }

  async function fetchCurrentUser() {
    if (!token.value) return null
    try {
      const res = await authAPI.getCurrentUser()
      setUser(res.user)
      return res.user
    } catch (error) {
      console.error('Fetch user error:', error)
      return null
    }
  }

  function initFromStorage() {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      try {
        user.value = JSON.parse(savedUser)
      } catch (error) {
        console.error('Parse user error:', error)
      }
    }
  }

  return {
    user,
    token,
    setUser,
    setToken,
    login,
    register,
    logout,
    fetchCurrentUser,
    initFromStorage
  }
})
