import request from '@/utils/request'

export const categoryAPI = {
  getList() {
    return request({
      url: '/api/categories',
      method: 'get'
    })
  },
  
  create(data) {
    return request({
      url: '/api/categories',
      method: 'post',
      data
    })
  },
  
  update(id, data) {
    return request({
      url: `/api/categories/${id}`,
      method: 'put',
      data
    })
  },
  
  delete(id) {
    return request({
      url: `/api/categories/${id}`,
      method: 'delete'
    })
  }
}

export const tagAPI = {
  getList() {
    return request({
      url: '/api/tags',
      method: 'get'
    })
  },
  
  create(data) {
    return request({
      url: '/api/tags',
      method: 'post',
      data
    })
  },
  
  delete(id) {
    return request({
      url: `/api/tags/${id}`,
      method: 'delete'
    })
  }
}
