import axios from 'axios'
// 关键修复：导入ElMessage组件
import { ElMessage } from 'element-plus'

// 创建axios实例
const service = axios.create({
  baseURL: 'http://localhost:8000', // 后端地址
  timeout: 5000,
  withCredentials: true // 允许携带cookie（跨域认证必备）
})

// 请求拦截器：添加token等请求头
service.interceptors.request.use(
  (config) => {
    // 从localStorage获取token并添加到请求头
    const token = localStorage.getItem('token')
    if (token) {
      // 确保Authorization字段格式正确（Bearer + 空格 + Token）
      config.headers['Authorization'] = `Bearer ${token}`
    }
    // 统一设置Content-Type，避免后端解析参数失败
    if (!config.headers['Content-Type']) {
      config.headers['Content-Type'] = 'application/json'
    }
    return config
  },
  (error) => {
    // 请求错误处理
    console.error('请求拦截器错误：', error)
    return Promise.reject(error)
  }
)

// 响应拦截器：统一处理响应数据/错误
service.interceptors.response.use(
  (response) => {
    // 只返回响应的data部分
    return response.data
  },
  (error) => {
    // 详细打印错误信息，方便排查
    console.error('响应错误详情：', {
      url: error.config?.url, // 请求地址
      method: error.config?.method, // 请求方法
      status: error.response?.status, // 状态码
      data: error.response?.data // 后端返回的错误信息
    })
    
    // 针对性错误提示
    if (error.response?.status === 401) {
      // 401未授权：清除无效token，提示登录
      localStorage.removeItem('token')
      ElMessage.warning('登录已过期，请重新登录')
      // 跳转到登录页
      window.location.href = '/login'
    } else if (error.response?.status === 404) {
      ElMessage.error(`接口不存在：${error.config.url}`)
    } else {
      ElMessage.error(`请求失败：${error.message}`)
    }
    
    return Promise.reject(error)
  }
)

// 导出实例
export default service