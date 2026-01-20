import axios from 'axios'
import { getCurrentUser } from '../utils/auth'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  withCredentials: true // 允许携带cookie
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    const user = getCurrentUser()
    if (user) {
      // 如果需要token验证，可以在这里添加
      // config.headers.Authorization = `Bearer ${user.token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    // 处理401未授权错误
    if (error.response && error.response.status === 401) {
      // 清除用户信息并跳转到登录页
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 用户认证API
export const authAPI = {
  login: (credentials) => api.post('/login', credentials),
  register: (userData) => api.post('/register', userData),
  logout: () => api.post('/logout'),
  checkLogin: () => api.get('/check-login')
}

// 用户资料API
export const userAPI = {
  getProfile: () => api.get('/user/profile'),
  updateProfile: (data) => api.put('/user/profile', data)
}

// 文档管理API
export const documentAPI = {
  getDocuments: () => api.get('/documents'),
  newTable: (title) => api.post('/table/new', { title }),
  getTable: (id) => api.get(`/table?id=${id}`),
  saveTable: (data) => api.post('/table/save', data),
  newWhiteboard: (title) => api.post('/whiteboard/new', { title }),
  getWhiteboard: (id) => api.get(`/whiteboard?id=${id}`),
  saveWhiteboard: (data) => api.post('/whiteboard/save', data)
}

// 分享功能API
export const shareAPI = {
  getSharedDocument: (shareId) => api.get(`/share/${shareId}`),
  createShare: (data) => api.post('/share/create', data)
}

// 管理后台API
export const adminAPI = {
  getUsers: () => api.get('/admin/users'),
  getStats: () => api.get('/admin/stats'),
  updateUserRole: (userId, role) => api.put(`/admin/users/${userId}/role`, { role })
}

export default api