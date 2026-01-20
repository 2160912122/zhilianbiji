import axios from 'axios'

const API_URL = '/api'

const noteService = {
  // 获取笔记列表
  async getNotes() {
    const response = await axios.get(`${API_URL}/notes`)
    return response.data
  },
  
  // 获取单个笔记详情
  async getNote(id) {
    const response = await axios.get(`${API_URL}/notes/${id}`)
    return response.data
  },
  
  // 创建笔记
  async createNote(noteData) {
    const response = await axios.post(`${API_URL}/notes`, noteData)
    return response.data
  },
  
  // 更新笔记
  async updateNote(id, noteData) {
    const response = await axios.put(`${API_URL}/notes/${id}`, noteData)
    return response.data
  },
  
  // 删除笔记
  async deleteNote(id) {
    const response = await axios.delete(`${API_URL}/notes/${id}`)
    return response.data
  },
  
  // 获取笔记版本历史
  async getNoteVersions(id) {
    const response = await axios.get(`${API_URL}/notes/${id}/versions`)
    return response.data
  },
  
  // 回滚笔记版本
  async rollbackNoteVersion(noteId, versionId) {
    const response = await axios.post(`${API_URL}/notes/${noteId}/versions/${versionId}/rollback`)
    return response.data
  },
  
  // 导出笔记
  async exportNote(id, format) {
    const response = await axios.get(`${API_URL}/notes/${id}/export`, {
      params: { format },
      responseType: 'blob'
    })
    return response
  },
  
  // 创建分享链接
  async createShare(noteId, permission, expireAt) {
    const response = await axios.post(`${API_URL}/share`, {
      note_id: noteId,
      permission,
      expire_at: expireAt
    })
    return response.data
  },

  // 获取笔记的所有分享链接
  async getShares(noteId) {
    const response = await axios.get(`${API_URL}/notes/${noteId}/shares`)
    return response.data
  },

  // 删除分享链接
  async deleteShare(token) {
    const response = await axios.delete(`${API_URL}/shares/${token}`)
    return response.data
  },
  
  // AI生成笔记
  async aiGenerateNote(topic) {
    const response = await axios.post(`${API_URL}/ai/generate_note`, {
      topic
    })
    return response.data
  },
  
  // AI总结笔记
  async aiSummarize(content) {
    const response = await axios.post(`${API_URL}/ai/summarize`, {
      content
    })
    return response.data
  },
  
  // AI推荐标签
  async aiSuggestTags(content) {
    const response = await axios.post(`${API_URL}/ai/suggest_tags`, {
      content
    })
    return response.data
  }
}

export { noteService }