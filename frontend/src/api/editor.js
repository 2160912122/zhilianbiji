import request from '@/utils/request'

export const tableAPI = {
  getList() {
    return request({
      url: '/tables',
      method: 'get'
    })
  },
  
  create(data) {
    return request({
      url: '/tables',
      method: 'post',
      data
    })
  },
  
  get(id) {
    return request({
      url: `/tables/${id}`,
      method: 'get'
    })
  },
  
  update(id, data) {
    return request({
      url: `/tables/${id}`,
      method: 'put',
      data
    })
  },
  
  delete(id) {
    return request({
      url: `/tables/${id}`,
      method: 'delete'
    })
  },
  
  getVersions(id) {
    return request({
      url: `/tables/${id}/versions`,
      method: 'get'
    })
  },
  
  rollbackVersion(id, versionId) {
    return request({
      url: `/tables/${id}/versions/${versionId}`,
      method: 'post'
    })
  }
}

export const whiteboardAPI = {
  getList() {
    return request({
      url: '/whiteboards',
      method: 'get'
    })
  },
  
  create(data) {
    return request({
      url: '/whiteboards',
      method: 'post',
      data
    })
  },
  
  get(id) {
    return request({
      url: `/whiteboards/${id}`,
      method: 'get'
    })
  },
  
  update(id, data) {
    return request({
      url: `/whiteboards/${id}`,
      method: 'put',
      data
    })
  },
  
  delete(id) {
    return request({
      url: `/whiteboards/${id}`,
      method: 'delete'
    })
  },
  
  getVersions(id) {
    return request({
      url: `/whiteboards/${id}/versions`,
      method: 'get'
    })
  },
  
  rollbackVersion(id, versionId) {
    return request({
      url: `/whiteboards/${id}/versions/${versionId}`,
      method: 'post'
    })
  }
}

export const mindmapAPI = {
  getList() {
    return request({
      url: '/mindmaps',
      method: 'get'
    })
  },
  
  create(data) {
    return request({
      url: '/mindmaps',
      method: 'post',
      data
    })
  },
  
  get(id) {
    return request({
      url: `/mindmaps/${id}`,
      method: 'get'
    })
  },
  
  update(id, data) {
    return request({
      url: `/mindmaps/${id}`,
      method: 'put',
      data
    })
  },
  
  delete(id) {
    return request({
      url: `/mindmaps/${id}`,
      method: 'delete'
    })
  },
  
  getVersions(id) {
    return request({
      url: `/mindmaps/${id}/versions`,
      method: 'get'
    })
  },
  
  rollbackVersion(id, versionId) {
    return request({
      url: `/mindmaps/${id}/versions/${versionId}`,
      method: 'post'
    })
  }
}

export const flowchartAPI = {
  getList(params) {
    return request({
      url: '/flowcharts',
      method: 'get',
      params
    })
  },
  
  create(data) {
    return request({
      url: '/flowcharts',
      method: 'post',
      data
    })
  },
  
  get(id) {
    return request({
      url: `/flowcharts/${id}`,
      method: 'get'
    })
  },
  
  update(id, data) {
    return request({
      url: `/flowcharts/${id}`,
      method: 'put',
      data
    })
  },
  
  delete(id) {
    return request({
      url: `/flowcharts/${id}`,
      method: 'delete'
    })
  },
  
  duplicate(id) {
    return request({
      url: `/flowcharts/${id}/duplicate`,
      method: 'post'
    })
  },
  
  share(id, data) {
    return request({
      url: `/flowcharts/${id}/share`,
      method: 'post',
      data
    })
  }
}
