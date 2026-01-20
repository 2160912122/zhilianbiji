import { defineStore } from 'pinia'
import { authService } from '../services/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    loading: false,
    error: null
  }),
  
  getters: {
    username: (state) => state.user?.username,
    isAdmin: (state) => state.user?.is_admin
  },
  
  actions: {
    async login(credentials) {
      this.loading = true
      this.error = null
      
      try {
        const response = await authService.login(credentials)
        this.user = response.user
        this.isAuthenticated = true
        return response
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async register(credentials) {
      this.loading = true
      this.error = null
      
      try {
        const response = await authService.register(credentials)
        return response
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async logout() {
      this.loading = true
      
      try {
        await authService.logout()
        this.user = null
        this.isAuthenticated = false
      } catch (error) {
        // 即使登出失败，也清除本地状态
        this.user = null
        this.isAuthenticated = false
      } finally {
        this.loading = false
      }
    },
    
    // 初始化用户状态（从localStorage或cookie中恢复）
    init() {
      // 这里可以添加从localStorage或cookie中恢复用户状态的逻辑
      // 目前后端使用session，所以不需要客户端存储
    }
  }
})