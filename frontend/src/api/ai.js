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
  }
}
