import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/',
  timeout: 60000, // 增加超时时间到60秒，适应AI生成内容的长时间处理
  withCredentials: true,
  responseType: 'json',
  headers: {
    'Content-Type': 'application/json;charset=utf-8'
  }
})

request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

request.interceptors.response.use(
  response => {
    const res = response.data || {}
    console.log('响应拦截器解析结果：', res)
    return res
  },
  error => {
    console.error('请求错误:', error)
    // 核心修复1：增加错误容错，避免无response时报错
    if (!error.response) {
      ElMessage.error('无法连接后端，请确认http://localhost:5000能访问')
      return Promise.reject(error)
    }

    const { status, data } = error.response
    console.error('错误状态:', status)
    console.error('错误数据:', data)
    // 核心修复2：只在明确的"token过期/无效"时才清token，且只删token不删全部
    if (status === 401 || status === 422) {
      // 增加判断：只有当前不在登录页，且确实有token时才处理（避免登录接口本身401触发）
      const currentToken = localStorage.getItem('token')
      if (window.location.pathname !== '/login' && currentToken) {
        // 修复：只删除token，不清空所有localStorage！
        localStorage.removeItem('token')
        // 修复：用Vue Router跳转（如果有的话），避免强制刷新
        ElMessage.error('登录已过期，请重新登录')
        // 延迟跳转，确保提示能显示
        setTimeout(() => {
          window.location.href = '/login'
        }, 1000)
      } else {
        ElMessage.error('登录失败，请检查用户名和密码')
      }
    } else if (status === 403) {
      ElMessage.error(data?.msg || '无管理员权限')
    } else if (status === 404) {
      ElMessage.error('后端接口路径不匹配，请检查/app.py的路由')
    } else if (status === 500) {
      ElMessage.error(data?.msg || '服务器错误')
    } else if (status !== 200) { // 只在非200时提示，避免正常请求被干扰
      ElMessage.error(`请求失败：${status}`)
    }

    return Promise.reject(error)
  }
)

export default request