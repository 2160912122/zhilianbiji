import request from '@/utils/request'

export const authAPI = {
  login(data) {
    return request({
      url: '/api/login',
      method: 'post',
      data
    })
  },
  
  register(data) {
    return request({
      url: '/api/register',
      method: 'post',
      data
    })
  },
  
  logout() {
    return request({
      url: '/api/logout',
      method: 'post'
    })
  },
  
  getCurrentUser() {
    return request({
      url: '/api/user',
      method: 'get'
    })
  },
  
  updateUser(data) {
    return request({
      url: '/api/user',
      method: 'put',
      data
    })
  }
}
