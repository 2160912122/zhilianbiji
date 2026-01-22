import request from '@/utils/request'

// 获取脑图版本列表
export const getVersionList = (mindmapId) => {
  return request({
    url: `/api/mindmaps/${mindmapId}/versions`,
    method: 'GET'
  })
}

// 创建手动版本
export const createVersion = (mindmapId, data) => {
  return request({
    url: `/api/mindmaps/${mindmapId}/versions`,
    method: 'POST',
    data
  })
}

// 获取版本详情
export const getVersionDetail = (mindmapId, versionId) => {
  return request({
    url: `/api/mindmaps/${mindmapId}/versions/${versionId}`,
    method: 'GET'
  })
}

// 恢复版本
export const restoreVersion = (mindmapId, versionId) => {
  return request({
    url: `/api/mindmaps/${mindmapId}/versions/${versionId}/restore`,
    method: 'POST'
  })
}

// 删除版本
export const deleteVersion = (mindmapId, versionId) => {
  return request({
    url: `/api/mindmaps/${mindmapId}/versions/${versionId}`,
    method: 'DELETE'
  })
}