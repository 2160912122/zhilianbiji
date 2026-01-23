import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authAPI } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  // 初始化：从localStorage读取，保持字段名统一（下划线，和路由/后端一致）
  const user = ref(JSON.parse(localStorage.getItem('user')) || null)
  const token = ref(localStorage.getItem('token') || '')
  // 修复1：字段名改为is_admin，和路由/后端一致，确保转换为数字
  const is_admin = ref(Number(localStorage.getItem('is_admin')) || 0)

  // 设置用户信息，同步is_admin到localStorage
  function setUser(userData) {
    user.value = userData
    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData))
      // 修复：存储为is_admin（下划线），适配路由判断，确保转换为数字
      is_admin.value = Number(userData.is_admin) || 0
      localStorage.setItem('is_admin', is_admin.value)
    } else {
      localStorage.removeItem('user')
      is_admin.value = 0
      localStorage.removeItem('is_admin')
    }
  }

  // 设置token，只在主动登出时删除
  function setToken(newToken) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('token', newToken)
    } else {
      localStorage.removeItem('token')
    }
  }

  // 登录逻辑：适配后端返回，不主动触发fetchCurrentUser
  async function login(credentials) {
    try {
      const res = await authAPI.login(credentials)
      // 调试：查看登录响应
      console.log('登录响应：', res)
      // 优先从data中获取token，兼容其他格式
      const loginToken = res.data?.token || res.token || res.access_token
      if (!loginToken) {
        throw new Error('登录失败：未获取到token')
      }
      // 存储token和用户信息
      setToken(loginToken)
      // 修复：直接使用res.data作为userData，确保包含is_admin字段
      const userData = res.data || res.userInfo || res.user || {}
      setUser(userData)
      console.log('登录成功，存储的token：', loginToken)
      console.log('登录成功，存储的userData：', userData)
      console.log('登录成功，存储的is_admin：', is_admin.value)
      return res
    } catch (error) {
      console.error('Login error:', error)
      throw error // 抛出错误，让登录页提示
    }
  }

  // 注册逻辑：保持不变
  async function register(userData) {
    try {
      const res = await authAPI.register(userData)
      return res
    } catch (error) {
      console.error('Register error:', error)
      throw error
    }
  }

  // 登出逻辑：主动登出时才清空状态
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

  // 修复2：获取用户信息失败，不删除token（只提示错误，不影响登录状态）
  async function fetchCurrentUser() {
    if (!token.value) return null
    try {
      const res = await authAPI.getCurrentUser()
      // 调试：查看获取用户信息响应
      console.log('获取用户信息响应：', res)
      // 适配后端返回结构：{ user: { ... } }
      setUser(res.user || res.data || res || {}) // 同步最新信息
      return res.user || res.data || res || {}
    } catch (error) {
      console.error('Fetch user error:', error)
      // 只提示错误，不清空token！避免登录后立刻丢状态
      return null
    }
  }

  // 修复3：简化初始化逻辑，避免覆盖正确状态
  function initFromStorage() {
    // 只有当内存中无token，但localStorage有，才同步（防止重复初始化）
    if (!token.value && localStorage.getItem('token')) {
      token.value = localStorage.getItem('token')
    }
    // 同步is_admin，确保转换为数字
    if (!is_admin.value && localStorage.getItem('is_admin')) {
      is_admin.value = Number(localStorage.getItem('is_admin')) || 0
    }
  }

  return {
    user,
    token,
    is_admin, // 暴露下划线版本，和路由一致
    setUser,
    setToken,
    login,
    register,
    logout,
    fetchCurrentUser,
    initFromStorage
  }
})