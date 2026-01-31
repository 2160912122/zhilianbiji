import request from '@/utils/request'

export const tableAPI = {
  getList() {
    return request({
      url: '/api/tables',
      method: 'get'
    })
  },
  
  create(data) {
    return request({
      url: '/api/tables',
      method: 'post',
      data
    })
  },
  
  get(id) {
    return request({
      url: `/api/tables/${id}`,
      method: 'get'
    })
  },
  
  update(id, data) {
    return request({
      url: `/api/tables/${id}`,
      method: 'put',
      data
    })
  },
  
  delete(id) {
    return request({
      url: `/api/tables/${id}`,
      method: 'delete'
    })
  },
  
  getVersions(id) {
    return request({
      url: `/api/tables/${id}/versions`,
      method: 'get'
    })
  },
  
  rollbackVersion(id, versionId) {
    return request({
      url: `/api/tables/${id}/versions/${versionId}`,
      method: 'post'
    })
  }
}

export const whiteboardAPI = {
  getList() {
    return request({
      url: '/api/whiteboards',
      method: 'get'
    })
  },
  
  create(data) {
    return request({
      url: '/api/whiteboards',
      method: 'post',
      data
    })
  },
  
  get(id) {
    return request({
      url: `/api/whiteboards/${id}`,
      method: 'get'
    })
  },
  
  update(id, data) {
    return request({
      url: `/api/whiteboards/${id}`,
      method: 'put',
      data
    })
  },
  
  delete(id) {
    return request({
      url: `/api/whiteboards/${id}`,
      method: 'delete'
    })
  },
  
  getVersions(id) {
    return request({
      url: `/api/whiteboards/${id}/versions`,
      method: 'get'
    })
  },
  
  rollbackVersion(id, versionId) {
    return request({
      url: `/api/whiteboards/${id}/versions/${versionId}`,
      method: 'post'
    })
  }
}

export const mindmapAPI = {
  getList() {
    return request({
      url: '/api/mindmaps',
      method: 'get'
    })
  },
  
  create(data) {
    return request({
      url: '/api/mindmaps',
      method: 'post',
      data
    })
  },
  
  get(id) {
    return request({
      url: `/api/mindmaps/${id}`,
      method: 'get'
    })
  },
  
  update(id, data) {
    return request({
      url: `/api/mindmaps/${id}`,
      method: 'put',
      data
    })
  },
  
  delete(id) {
    return request({
      url: `/api/mindmaps/${id}`,
      method: 'delete'
    })
  },
  
  getVersions(id) {
    return request({
      url: `/api/mindmaps/${id}/versions`,
      method: 'get'
    })
  },
  
  rollbackVersion(id, versionId) {
    return request({
      url: `/api/mindmaps/${id}/versions/${versionId}`,
      method: 'post'
    })
  },
  
  share(id, data) {
    return request({
      url: `/api/mindmaps/${id}/share`,
      method: 'post',
      data
    })
  },
  
  getShares(id) {
    return request({
      url: `/api/mindmaps/${id}/shares`,
      method: 'get'
    })
  },
  
  deleteShare(token) {
    return request({
      url: `/api/shares/${token}`,
      method: 'delete'
    })
  },
  
  getShared(id) {
    return request({
      url: `/api/mindmaps/${id}/shared`,
      method: 'get'
    })
  }
}

export const flowchartAPI = {
  getList(params) {
    return request({
      url: '/api/flowcharts',
      method: 'get',
      params
    })
  },
  
  create(data) {
    return request({
      url: '/api/flowcharts',
      method: 'post',
      data
    })
  },
  
  get(id) {
    return request({
      url: `/api/flowcharts/${id}`,
      method: 'get'
    })
  },
  
  update(id, data) {
    return request({
      url: `/api/flowcharts/${id}`,
      method: 'put',
      data
    })
  },
  
  delete(id) {
    return request({
      url: `/api/flowcharts/${id}`,
      method: 'delete'
    })
  },
  
  duplicate(id) {
    return request({
      url: `/api/flowcharts/${id}/duplicate`,
      method: 'post'
    })
  },
  
  share(id, data) {
    return request({
      url: `/api/flowcharts/${id}/share`,
      method: 'post',
      data
    })
  }
}
