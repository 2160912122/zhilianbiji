import request from '@/utils/request'

export const authAPI = {
  login(data) {
    return request({
      url: '/login',
      method: 'post',
      data
    })
  },
  
  register(data) {
    return request({
      url: '/register',
      method: 'post',
      data
    })
  },
  
  logout() {
    return request({
      url: '/logout',
      method: 'post'
    })
  },
  
  getCurrentUser() {
    return request({
      url: '/user',
      method: 'get'
    })
  },
  
  updateUser(data) {
    return request({
      url: '/user',
      method: 'put',
      data
    })
  }
}
