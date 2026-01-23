import request from '@/utils/request'

export const aiAPI = {
  generate(topic) {
    return request({
      url: '/api/ai/generate',
      method: 'post',
      data: { topic }
    })
  },
  
  summarize(content) {
    return request({
      url: '/api/ai/summarize',
      method: 'post',
      data: { content }
    })
  },
  
  suggestTags(content) {
    return request({
      url: '/api/ai/suggest_tags',
      method: 'post',
      data: { content }
    })
  }
}

export const adminAPI = {
  getStats() {
    return request({
      url: '/api/admin/stats',
      method: 'get'
    })
  },
  
  getUsers() {
    return request({
      url: '/api/admin/users',
      method: 'get'
    })
  },
  
  deleteUser(id) {
    return request({
      url: `/api/admin/users/${id}`,
      method: 'delete'
    })
  },
  
  setAdmin(id) {
    return request({
      url: `/api/admin/set_admin/${id}`,
      method: 'post'
    })
  }
}
