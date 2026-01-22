import request from '../utils/request'

// 用户登录（以 application/x-www-form-urlencoded 提交，兼容后端 Flask 表单解析）
export const userLogin = (data) => {
  return request({
    url: '/api/login',
    method: 'POST',
    // 采用 JSON 提交，避免后端返回 415 Unsupported Media Type
    data
  })
}

// 用户注册
export const userRegister = (data) => {
  return request({
    url: '/api/register',
    method: 'POST',
    data
  })
}

// 用户登出
export const userLogout = () => {
  return request({
    url: '/api/logout',
    method: 'POST'
  })
}

// 获取当前用户信息
export const getUserInfo = () => {
  return request({
    url: '/api/me',
    method: 'GET'
  })
}

// 校验是否为管理员
export const checkAdmin = () => {
  return request({
    url: '/api/check-admin',
    method: 'GET'
  })
}

// 管理员登录
export function adminLogin(data) {
  return request({
    url: '/api/admin/login',
    method: 'post',
    data
  })
}

// 获取管理员信息
export const getAdminInfo = () => {
  return request({
    url: '/api/admin/me', // ✅ 改成后端真实存在的接口，100%匹配
    method: 'GET'
  })
}

// 管理员登出
export const adminLogout = () => {
  return request({
    url: '/api/admin/logout',
    method: 'POST'
  })
}