import request from '@/utils/request'

export const aiAPI = {
  generate(topic) {
    return request({
      url: '/ai/generate',
      method: 'post',
      data: { topic }
    })
  },
  
  summarize(content) {
    return request({
      url: '/ai/summarize',
      method: 'post',
      data: { content }
    })
  },
  
  suggestTags(content) {
    return request({
      url: '/ai/suggest_tags',
      method: 'post',
      data: { content }
    })
  }
}

export const adminAPI = {
  getStats() {
    return request({
      url: '/admin/stats',
      method: 'get'
    })
  },
  
  getUsers() {
    return request({
      url: '/admin/users',
      method: 'get'
    })
  },
  
  deleteUser(id) {
    return request({
      url: `/admin/users/${id}`,
      method: 'delete'
    })
  },
  
  setAdmin(id) {
    return request({
      url: `/admin/set_admin/${id}`,
      method: 'post'
    })
  }
}
