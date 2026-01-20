import axios from 'axios'

const API_URL = '/api'

const tagService = {
  // 获取所有标签
  async getTags() {
    const response = await axios.get(`${API_URL}/tags`)
    return response.data
  },
  
  // 创建新标签
  async createTag(tagData) {
    const response = await axios.post(`${API_URL}/tags`, tagData)
    return response.data
  },
  
  // 删除标签
  async deleteTag(id) {
    const response = await axios.delete(`${API_URL}/tags/${id}`)
    return response.data
  }
}

export { tagService }