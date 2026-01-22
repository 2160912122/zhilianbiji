// 你的 request.js 原版代码 ✔️ 完全正确，零改动！
import axios from 'axios'

const request = axios.create({
  timeout: 10000,
  withCredentials: true // 保留这行，和代理配合携带Cookie ✔️ 核心配置正确
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 仅在未显式设置时提供默认 Content-Type，避免覆盖调用处传入的类型（例如表单提交）
    if (!config.headers['Content-Type'] && !config.headers['content-type']) {
      config.headers['Content-Type'] = 'application/json;charset=utf-8'
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response
  },
  error => {
    console.error('请求错误：', error)
    if (error.response && error.response.status === 401) {
      // 根据当前路径决定跳转到哪个登录页面
      const currentPath = window.location.pathname
      const redirectPath = currentPath.includes('admin') ? '/admin-login' : '/login'
      // 使用 router.push 而不是 window.location.href，避免页面刷新
      const router = require('@/router').default
      router.push(redirectPath)
    }
    return Promise.reject(error)
  }
)

export default request