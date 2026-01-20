import axios from 'axios'

const API_URL = '/api'

const categoryService = {
  // 获取所有分类
  async getCategories() {
    const response = await axios.get(`${API_URL}/categories`)
    return response.data
  },
  
  // 创建新分类
  async createCategory(categoryData) {
    const response = await axios.post(`${API_URL}/categories`, categoryData)
    return response.data
  },
  
  // 删除分类
  async deleteCategory(id) {
    const response = await axios.delete(`${API_URL}/categories/${id}`)
    return response.data
  }
}

export { categoryService }