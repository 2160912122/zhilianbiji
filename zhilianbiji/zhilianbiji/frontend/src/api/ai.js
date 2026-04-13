import request from '@/utils/request'

export const aiAPI = {
  /**
   * AI聊天接口
   * @param {Array} messages - 聊天消息数组
   * @returns {Promise} - 返回Promise对象
   */
  chat(messages) {
    return request({
      url: '/api/ai/chat',
      method: 'post',
      data: {
        messages
      }
    })
  },
  
  /**
   * Doubao-Seedream-4.0模型聊天接口
   * @param {Array} messages - 聊天消息数组
   * @returns {Promise} - 返回Promise对象
   */
  chatDoubao(messages) {
    return request({
      url: '/api/ai/chat/doubao',
      method: 'post',
      data: {
        messages
      }
    })
  },
  
  /**
   * 文件上传接口
   * @param {File} file - 要上传的文件
   * @returns {Promise} - 返回Promise对象
   */
  uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file)
    return request({
      url: '/api/ai/upload',
      method: 'post',
      data: formData,
      // 移除手动设置的Content-Type头，让axios自动添加
      headers: {
        'Content-Type': undefined
      }
    })
  },
  
  /**
   * 图像生成接口
   * @param {string} prompt - 图像描述
   * @returns {Promise} - 返回Promise对象
   */
  generateImage(prompt) {
    return request({
      url: '/api/ai/generate-image',
      method: 'post',
      data: {
        prompt
      }
    })
  },
  
  /**
   * 文档分析接口
   * @param {string} file_path - 文件路径
   * @returns {Promise} - 返回Promise对象
   */
  analyzeDocument(file_path) {
    return request({
      url: '/api/ai/analyze-document',
      method: 'post',
      data: {
        file_path
      }
    })
  },
  
  /**
   * 图片分析接口
   * @param {string} file_path - 文件路径
   * @returns {Promise} - 返回Promise对象
   */
  analyzeImage(file_path) {
    return request({
      url: '/api/ai/analyze-image',
      method: 'post',
      data: {
        file_path
      }
    })
  },
  
  /**
   * 视频分析接口
   * @param {string} file_path - 文件路径
   * @returns {Promise} - 返回Promise对象
   */
  analyzeVideo(file_path) {
    return request({
      url: '/api/ai/analyze-video',
      method: 'post',
      data: {
        file_path
      }
    })
  }
}
