// 保存用户信息到localStorage
export const saveUser = (user) => {
  if (user && typeof user === 'object') {
    localStorage.setItem('user', JSON.stringify(user))
  } else {
    console.error('无效的用户信息:', user)
    localStorage.removeItem('user')
  }
}

// 从localStorage获取用户信息
export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user')
  // 检查是否为undefined字符串或实际的undefined
  if (!userStr || userStr === 'undefined' || userStr === 'null') {
    localStorage.removeItem('user')
    return null
  }
  try {
    return JSON.parse(userStr)
  } catch (error) {
    console.error('解析用户信息失败:', error)
    localStorage.removeItem('user')
    return null
  }
}

// 清除用户信息
export const clearUser = () => {
  localStorage.removeItem('user')
}

// 检查用户是否已登录
export const isLoggedIn = () => {
  return !!getCurrentUser()
}

// 检查用户是否是管理员
export const isAdmin = () => {
  const user = getCurrentUser()
  return user && user.role === 'admin'
}