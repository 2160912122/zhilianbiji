import request from '@/utils/request'

export const noteAPI = {
  getList(params) {
    return request({
      url: '/api/notes',
      method: 'get',
      params
    })
  },
  
  create(data) {
    return request({
      url: '/api/notes',
      method: 'post',
      data
    })
  },
  
  get(id) {
    return request({
      url: `/api/notes/${id}`,
      method: 'get'
    })
  },
  
  update(id, data) {
    return request({
      url: `/api/notes/${id}`,
      method: 'put',
      data
    })
  },
  
  delete(id) {
    return request({
      url: `/api/notes/${id}`,
      method: 'delete'
    })
  },
  
  getVersions(id) {
    return request({
      url: `/api/notes/${id}/versions`,
      method: 'get'
    })
  },
  
  saveVersion(id) {
    return request({
      url: `/api/notes/${id}/versions`,
      method: 'post'
    })
  },
  
  rollbackVersion(noteId, versionId) {
    return request({
      url: `/api/notes/${noteId}/versions/${versionId}/rollback`,
      method: 'post'
    })
  },
  
  share(id, data) {
    return request({
      url: `/api/notes/${id}/share`,
      method: 'post',
      data
    })
  },
  
  getShares(id) {
    return request({
      url: `/api/notes/${id}/shares`,
      method: 'get'
    })
  },
  
  deleteShare(token) {
    return request({
      url: `/api/shares/${token}`,
      method: 'delete'
    })
  }
}
