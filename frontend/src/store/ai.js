import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAIStore = defineStore('ai', () => {
  // AI生成的内容
  const generatedContent = ref('')
  // 是否有新的AI内容需要插入
  const hasNewContent = ref(false)

  // 设置AI生成的内容
  function setGeneratedContent(content) {
    generatedContent.value = content
    hasNewContent.value = true
  }

  // 重置AI内容状态（表示已处理）
  function resetGeneratedContent() {
    generatedContent.value = ''
    hasNewContent.value = false
  }

  return {
    generatedContent,
    hasNewContent,
    setGeneratedContent,
    resetGeneratedContent
  }
})