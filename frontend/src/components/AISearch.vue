<template>
  <div class="ai-search-container">
    <div class="search-header">
      <div class="search-input-wrapper">
        <Search class="search-icon" />
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="输入搜索关键词，支持AI智能回答..."
          @keyup.enter="handleSearch"
        />
        <button class="search-btn" @click="handleSearch">
          <Sparkles />
        </button>
      </div>
    </div>
    
    <div v-if="searching" class="loading-container">
      <el-spinner class="search-loading" />
      <span class="loading-text">正在搜索...</span>
    </div>
    
    <div v-else-if="results" class="search-results">
      <!-- AI回答区域 -->
      <div v-if="results.ai_answer" class="ai-answer-card">
        <div class="card-header">
          <Bot class="ai-icon" />
          <span class="card-title">AI智能回答</span>
        </div>
        <div class="ai-answer-content">
          <div v-html="formatAnswer(results.ai_answer)"></div>
        </div>
      </div>
      
      <!-- 本地搜索结果 -->
      <div v-if="results.local_results.length > 0" class="local-results">
        <div class="results-header">
          <FileSearch class="results-icon" />
          <span class="results-title">文档搜索结果</span>
          <span class="results-count">共 {{ results.local_results.length }} 条</span>
        </div>
        
        <div class="results-list">
          <div
            v-for="item in results.local_results"
            :key="item.id"
            class="result-item"
            @click="handleResultClick(item)"
          >
            <div class="result-icon">
              <component :is="getTypeIcon(item.type)" />
            </div>
            <div class="result-content">
              <h4 class="result-title">{{ item.title }}</h4>
              <p class="result-preview">{{ item.content }}</p>
              <span class="result-meta">
                <Clock class="meta-icon" />
                {{ formatTime(item.updated_at) }}
              </span>
            </div>
            <div class="result-type">
              <span class="type-tag">{{ getTypeName(item.type) }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 空结果 -->
      <div v-if="results.local_results.length === 0 && !results.ai_answer" class="empty-results">
        <SearchX class="empty-icon" />
        <p class="empty-text">未找到相关内容</p>
        <p class="empty-hint">尝试使用其他关键词搜索</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  Search,
  Sparkles,
  Bot,
  FileSearch,
  FileText,
  GitBranch,
  Table,
  PenTool,
  Brain,
  Clock,
  SearchX
} from '@element-plus/icons-vue'

const emit = defineEmits(['result-click'])

const searchQuery = ref('')
const searching = ref(false)
const results = ref(null)

const handleSearch = async () => {
  if (!searchQuery.value.trim()) return
  
  searching.value = true
  results.value = null
  
  try {
    const response = await fetch('/api/search/ai', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ query: searchQuery.value })
    })
    
    const data = await response.json()
    
    if (data.code === 200) {
      results.value = data.data
    } else {
      ElMessage.error(data.message || '搜索失败')
    }
  } catch (error) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败，请稍后重试')
  } finally {
    searching.value = false
  }
}

const handleResultClick = (item) => {
  emit('result-click', item)
}

const getTypeIcon = (type) => {
  const icons = {
    note: FileText,
    flowchart: GitBranch,
    table: Table,
    whiteboard: PenTool,
    mindmap: Brain
  }
  return icons[type] || FileText
}

const getTypeName = (type) => {
  const names = {
    note: '笔记',
    flowchart: '流程图',
    table: '表格',
    whiteboard: '白板',
    mindmap: '脑图'
  }
  return names[type] || '文档'
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)} 天前`
  
  return date.toLocaleDateString('zh-CN')
}

const formatAnswer = (answer) => {
  if (!answer) return ''
  
  // 转换Markdown格式
  let formatted = answer
    .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/### (.+)/g, '<h3>$1</h3>')
    .replace(/## (.+)/g, '<h2>$1</h2>')
    .replace(/### (.+)/g, '<h3>$1</h3>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
  
  return formatted
}
</script>

<style scoped>
.ai-search-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.search-header {
  margin-bottom: 20px;
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 30px;
  padding: 8px 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.search-icon {
  width: 20px;
  height: 20px;
  color: #999;
  margin-right: 10px;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 14px;
  padding: 8px 0;
}

.search-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.2s;
}

.search-btn:hover {
  transform: scale(1.1);
}

.search-btn svg {
  width: 18px;
  height: 18px;
  color: #fff;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
}

.search-loading {
  width: 40px;
  height: 40px;
}

.loading-text {
  margin-top: 16px;
  color: #999;
  font-size: 14px;
}

.search-results {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.ai-answer-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  color: #fff;
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.ai-icon {
  width: 24px;
  height: 24px;
  margin-right: 8px;
}

.card-title {
  font-weight: 600;
  font-size: 16px;
}

.ai-answer-content {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 16px;
  font-size: 14px;
  line-height: 1.8;
}

.ai-answer-content pre {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 6px;
  padding: 12px;
  overflow-x: auto;
  margin: 8px 0;
}

.ai-answer-content code {
  background: rgba(0, 0, 0, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Consolas', monospace;
}

.local-results {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.results-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.results-icon {
  width: 20px;
  height: 20px;
  color: #667eea;
  margin-right: 8px;
}

.results-title {
  font-weight: 600;
  font-size: 16px;
  color: #333;
}

.results-count {
  margin-left: auto;
  font-size: 12px;
  color: #999;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-item {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.result-item:hover {
  background-color: #f8f9fa;
}

.result-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  border-radius: 8px;
  margin-right: 12px;
  flex-shrink: 0;
}

.result-icon svg {
  width: 18px;
  height: 18px;
  color: #667eea;
}

.result-content {
  flex: 1;
  min-width: 0;
}

.result-title {
  font-weight: 500;
  font-size: 14px;
  color: #333;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-preview {
  font-size: 13px;
  color: #999;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-meta {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #bbb;
}

.meta-icon {
  width: 14px;
  height: 14px;
  margin-right: 4px;
}

.result-type {
  margin-left: 12px;
}

.type-tag {
  display: inline-block;
  padding: 4px 10px;
  background: #f0f0f0;
  border-radius: 12px;
  font-size: 12px;
  color: #666;
}

.empty-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
}

.empty-icon {
  width: 48px;
  height: 48px;
  color: #ddd;
  margin-bottom: 12px;
}

.empty-text {
  font-size: 14px;
  color: #999;
  margin-bottom: 4px;
}

.empty-hint {
  font-size: 12px;
  color: #bbb;
}
</style>
