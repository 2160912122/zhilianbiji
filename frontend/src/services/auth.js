import axios from 'axios'

const API_URL = '/api'

const authService = {
  async login(credentials) {
    const response = await axios.post(`${API_URL}/login`, credentials)
    return response.data
  },
  
  async register(credentials) {
    const response = await axios.post(`${API_URL}/register`, credentials)
    return response.data
  },
  
  async logout() {
    const response = await axios.post(`${API_URL}/logout`)
    return response.data
  },
  
  // 获取当前用户信息（如果需要）
  async getCurrentUser() {
    const response = await axios.get(`${API_URL}/user`)
    return response.data
  }
}

export { authService }