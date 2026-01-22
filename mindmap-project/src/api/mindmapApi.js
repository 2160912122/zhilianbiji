import request from '../utils/request'

// 脑图相关
export const getMindmapList = () => request({ url: '/api/mindmaps', method: 'GET' })
export const createMindmap = (data) => request({ url: '/api/mindmaps', method: 'POST', data })
export const getMindmapById = (id) => request({ url: `/api/mindmaps/${id}`, method: 'GET' })
export const updateMindmap = (id, data) => request({ url: `/api/mindmaps/${id}`, method: 'PUT', data })
export const deleteMindmap = (id) => request({ url: `/api/mindmaps/${id}`, method: 'DELETE' })

// 脑图导出
export const exportJson = (id) => request({ url: `/api/mindmaps/${id}/export/json`, method: 'GET', responseType: 'blob' })
export const exportText = (id) => request({ url: `/api/mindmaps/${id}/export/text`, method: 'GET', responseType: 'blob' })
export const exportImage = (id) => request({ url: `/api/mindmaps/${id}/export/image`, method: 'GET', responseType: 'blob' })
export const exportPdf = (id) => request({ url: `/api/mindmaps/${id}/export/pdf`, method: 'GET', responseType: 'blob' })

// 脑图分享
export const updateShare = (id, data) => request({ url: `/api/mindmaps/${id}/share`, method: 'PUT', data })

// 标签相关
export const getTagList = () => request({ url: '/api/tags', method: 'GET' })
export const createTag = (data) => request({ url: '/api/tags', method: 'POST', data })
export const updateTag = (id, data) => request({ url: `/api/tags/${id}`, method: 'PUT', data })
export const deleteTag = (id) => request({ url: `/api/tags/${id}`, method: 'DELETE' })
export const bindTagToMindmap = (mindmapId, data) => request({ url: `/api/mindmaps/${mindmapId}/tags`, method: 'POST', data })
export const unbindTagFromMindmap = (mindmapId, tagId) => request({ url: `/api/mindmaps/${mindmapId}/tags/${tagId}`, method: 'DELETE' })

// 评论相关
export const getCommentList = (mindmapId) => request({ url: `/api/mindmaps/${mindmapId}/comments`, method: 'GET' })
export const addComment = (mindmapId, data) => request({ url: `/api/mindmaps/${mindmapId}/comments`, method: 'POST', data })
export const updateComment = (mindmapId, commentId, data) => request({ url: `/api/mindmaps/${mindmapId}/comments/${commentId}`, method: 'PUT', data })
export const deleteComment = (mindmapId, commentId) => request({ url: `/api/mindmaps/${mindmapId}/comments/${commentId}`, method: 'DELETE' })

// AI相关
export const aiAnalyze = (data) => request({ url: '/api/ai/analyze', method: 'POST', data })
export const aiEnhance = (data) => request({ url: '/api/ai/enhance', method: 'POST', data })

// 分享脑图访问
export const getShareMindmap = (shareType, id) => request({ url: `/api/share/${shareType}/${id}`, method: 'GET' })
export const updateShareMindmap = (id, data) => request({ url: `/api/share/mindmaps/${id}`, method: 'PUT', data })