<template>
  <div class="search-results">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">搜索结果</span>
          <el-icon class="card-icon"><Search /></el-icon>
        </div>
      </template>
      <div class="search-info">
        <p>搜索关键词: <span class="search-query">{{ searchQuery }}</span></p>
        <p>找到 <span class="search-count">{{ searchResults.length }}</span> 个结果</p>
      </div>
      <el-empty v-if="searchResults.length === 0" description="没有找到相关结果" />
      <div v-else class="search-results-list">
        <div 
          v-for="(item, index) in searchResults" 
          :key="item.id || index" 
          class="search-result-item"
          @click="navigateToItem(item)"
        >
          <div class="item-icon" :class="getItemTypeClass(item.type)">
            <el-icon :size="20">
              <component :is="getItemIcon(item.type)" />
            </el-icon>
          </div>
          <div class="item-content">
            <div class="item-title">{{ item.title }}</div>
            <div class="item-meta">
              <span class="item-type">{{ getTypeLabel(item.type) }}</span>
              <span class="item-time">{{ formatTime(item.updated_at) }}</span>
            </div>
            <div class="item-preview">{{ item.content?.substring(0, 100) }}...</div>
          </div>
          <el-icon class="item-arrow"><ArrowRight /></el-icon>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
<<<<<<< HEAD
import { ref, onMounted, computed } from 'vue'
=======
import { ref, onMounted, computed, watch } from 'vue'
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
import { useRoute, useRouter } from 'vue-router'
import { Search, ArrowRight, Document, Grid, EditPen, Connection, Share } from '@element-plus/icons-vue'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()

const searchQuery = computed(() => route.query.query || '')
const searchResults = ref([])

// 加载搜索结果
async function loadSearchResults() {
  if (!searchQuery.value) return
  
<<<<<<< HEAD
  try {
    // 调用搜索API获取真实数据
    const response = await request.get(`/api/search?query=${encodeURIComponent(searchQuery.value)}`)
=======
  console.log('开始搜索:', searchQuery.value)
  try {
    // 调用搜索API获取真实数据
    const url = `/api/search?query=${encodeURIComponent(searchQuery.value)}`
    console.log('请求URL:', url)
    const response = await request.get(url)
    console.log('搜索结果:', response)
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
    searchResults.value = response.data
  } catch (error) {
    console.error('加载搜索结果失败:', error)
  }
}

// 导航到项目详情
function navigateToItem(item) {
  const links = {
    note: `/notes/${item.id}`,
    table: `/tables/${item.id}`,
    whiteboard: `/whiteboards/${item.id}`,
    mindmap: `/mindmaps/${item.id}`,
    flowchart: `/flowcharts/${item.id}`
  }
  router.push(links[item.type] || '#')
}

// 获取项目类型的样式类
function getItemTypeClass(type) {
  const classes = {
    note: 'primary',
    table: 'success',
    whiteboard: 'warning',
    mindmap: 'danger',
    flowchart: 'info'
  }
  return classes[type] || 'info'
}

// 获取项目类型的图标
function getItemIcon(type) {
  const icons = {
    note: Document,
    table: Grid,
    whiteboard: EditPen,
    mindmap: Connection,
    flowchart: Share
  }
  return icons[type] || Document
}

// 获取项目类型的标签
function getTypeLabel(type) {
  const labels = {
    note: '笔记',
    table: '表格',
    whiteboard: '白板',
    mindmap: '脑图',
    flowchart: '流程图'
  }
  return labels[type] || type
}

// 格式化时间
function formatTime(timeString) {
  if (!timeString) return '未知时间'
  const date = new Date(timeString)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}

<<<<<<< HEAD
=======
// 监听搜索关键词变化，重新加载搜索结果
watch(searchQuery, (newVal) => {
  console.log('搜索关键词变化:', newVal)
  searchResults.value = []
  loadSearchResults()
})

>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
// 页面挂载时加载搜索结果
onMounted(() => {
  loadSearchResults()
})
</script>

<style scoped>
.search-results {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 64px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.5);
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #303133);
  background: linear-gradient(135deg, #303133, #606266);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.card-icon {
  font-size: 20px;
  color: var(--text-light, #909399);
  transition: all 0.3s ease;
}

.search-info {
  padding: 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.search-query {
  font-weight: 600;
  color: var(--primary-color, #409eff);
}

.search-count {
  font-weight: 600;
  color: var(--success-color, #67c23a);
}

.search-results-list {
  padding: 0 20px 20px;
}

.search-result-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  border-radius: var(--border-radius-lg, 12px);
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(5px);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  border: 1px solid rgba(0, 0, 0, 0.1);
  margin-bottom: 16px;
}

.search-result-item:hover {
  background-color: rgba(64, 158, 255, 0.05);
  transform: translateX(8px);
  box-shadow: 0 8px 20px rgba(64, 158, 255, 0.2);
  border-color: #409eff;
}

.item-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  position: relative;
  flex-shrink: 0;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.item-icon.primary {
  background: linear-gradient(135deg, #409eff, #66b1ff);
  color: white;
}

.item-icon.success {
  background: linear-gradient(135deg, #67c23a, #85ce61);
  color: white;
}

.item-icon.warning {
  background: linear-gradient(135deg, #e6a23c, #ebb563);
  color: white;
}

.item-icon.danger {
  background: linear-gradient(135deg, #f56c6c, #f78989);
  color: white;
}

.item-icon.info {
  background: linear-gradient(135deg, #909399, #a6a9ad);
  color: white;
}

.item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.item-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #303133);
  line-height: 1.4;
  background: linear-gradient(135deg, #303133, #606266);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--text-light, #909399);
}

.item-type {
  background-color: rgba(0, 0, 0, 0.1);
  padding: 2px 10px;
  border-radius: 12px;
  font-weight: 500;
}

.item-preview {
  font-size: 14px;
  color: var(--text-secondary, #606266);
  line-height: 1.4;
  margin-top: 4px;
}

.item-arrow {
  font-size: 20px;
  color: var(--text-light, #909399);
  transition: all 0.3s ease;
  flex-shrink: 0;
  margin-top: 4px;
}

.search-result-item:hover .item-arrow {
  color: #409eff;
  transform: translateX(8px);
}
</style>