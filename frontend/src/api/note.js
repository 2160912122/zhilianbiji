import request from '@/utils/request'

export const noteAPI = {
  getList(params) {
    return request({
      url: '/notes',
      method: 'get',
      params
    })
  },
  
  create(data) {
    return request({
      url: '/notes',
      method: 'post',
      data
    })
  },
  
  get(id) {
    return request({
      url: `/notes/${id}`,
      method: 'get'
    })
  },
  
  update(id, data) {
    return request({
      url: `/notes/${id}`,
      method: 'put',
      data
    })
  },
  
  delete(id) {
    return request({
      url: `/notes/${id}`,
      method: 'delete'
    })
  },
  
  getVersions(id) {
    return request({
      url: `/notes/${id}/versions`,
      method: 'get'
    })
  },
  
  saveVersion(id) {
    return request({
      url: `/notes/${id}/versions`,
      method: 'post'
    })
  },
  
  rollbackVersion(noteId, versionId) {
    return request({
      url: `/notes/${noteId}/versions/${versionId}/rollback`,
      method: 'post'
    })
  },
  
  share(id, data) {
    return request({
      url: `/notes/${id}/share`,
      method: 'post',
      data
    })
  },
  
  getShares(id) {
    return request({
      url: `/notes/${id}/shares`,
      method: 'get'
    })
  },
  
  deleteShare(token) {
    return request({
      url: `/shares/${token}`,
      method: 'delete'
    })
  }
}
