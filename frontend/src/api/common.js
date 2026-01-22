import request from '@/utils/request'

export const categoryAPI = {
  getList() {
    return request({
      url: '/categories',
      method: 'get'
    })
  },
  
  create(data) {
    return request({
      url: '/categories',
      method: 'post',
      data
    })
  },
  
  update(id, data) {
    return request({
      url: `/categories/${id}`,
      method: 'put',
      data
    })
  },
  
  delete(id) {
    return request({
      url: `/categories/${id}`,
      method: 'delete'
    })
  }
}

export const tagAPI = {
  getList() {
    return request({
      url: '/tags',
      method: 'get'
    })
  },
  
  create(data) {
    return request({
      url: '/tags',
      method: 'post',
      data
    })
  },
  
  delete(id) {
    return request({
      url: `/tags/${id}`,
      method: 'delete'
    })
  }
}
