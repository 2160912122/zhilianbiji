<template>
  <div class="trash-container">
    <div class="trash-header">
      <div class="header-left">
        <el-icon size="32" class="trash-icon"><Delete /></el-icon>
        <div>
          <h2>回收站</h2>
          <p class="sub-title">{{ trashItems.length }} 个项目已删除</p>
        </div>
      </div>
      <div class="header-right">
        <el-button
          v-if="trashItems.length > 0"
          type="danger"
          @click="handleClearTrash"
          :disabled="loading"
        >
          <el-icon><Delete /></el-icon>
          清空回收站
        </el-button>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <el-spin size="large" />
    </div>

    <div v-else-if="trashItems.length === 0" class="empty-state">
      <el-icon size="80" class="empty-icon"><Document /></el-icon>
      <h3>回收站是空的</h3>
      <p>已删除的项目会显示在这里，你可以随时恢复或永久删除它们</p>
      <el-button type="primary" @click="$router.push('/dashboard')">
        返回首页
      </el-button>
    </div>

    <div v-else class="trash-list">
      <el-card
        v-for="item in trashItems"
        :key="`${item.type}-${item.id}`"
        class="trash-item"
        hover
      >
        <div class="item-content">
          <div class="item-icon" :class="item.type">
            <component :is="getIcon(item.type)" />
          </div>
          <div class="item-info">
            <h3 class="item-title">{{ item.title }}</h3>
            <div class="item-meta">
              <span class="type-badge">{{ getTypeName(item.type) }}</span>
              <span class="delete-time">删除于 {{ formatTime(item.deleted_at) }}</span>
            </div>
          </div>
          <div class="item-actions">
            <el-button size="small" @click="handleRestore(item)">
              <el-icon><ArrowDown /></el-icon>
              恢复
            </el-button>
            <el-button size="small" type="danger" @click="handleDeletePermanently(item)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Delete, Document, Grid, EditPen, Connection, Share, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const trashItems = ref([])
const loading = ref(true)

const iconMap = {
  note: Document,
  flowchart: Share,
  table: Grid,
  whiteboard: EditPen,
  mindmap: Connection
}

const typeNameMap = {
  note: '笔记',
  flowchart: '流程图',
  table: '表格',
  whiteboard: '白板',
  mindmap: '脑图'
}

function getIcon(type) {
  return iconMap[type] || Document
}

function getTypeName(type) {
  return typeNameMap[type] || type
}

function formatTime(timeStr) {
  if (!timeStr) return '未知'
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor(diff / (1000 * 60))
  
  if (days > 0) {
    return `${days} 天前`
  } else if (hours > 0) {
    return `${hours} 小时前`
  } else if (minutes > 0) {
    return `${minutes} 分钟前`
  } else {
    return '刚刚'
  }
}

async function loadTrash() {
  loading.value = true
  try {
    const response = await fetch('/api/trash', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    const data = await response.json()
    if (data.code === 200) {
      trashItems.value = data.data
    }
  } catch (error) {
    console.error('加载回收站失败:', error)
    ElMessage.error('加载回收站失败')
  } finally {
    loading.value = false
  }
}

async function handleRestore(item) {
  try {
    const response = await fetch('/api/trash/restore', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        id: item.id,
        type: item.type
      })
    })
    const data = await response.json()
    if (data.code === 200) {
      ElMessage.success('恢复成功')
      trashItems.value = trashItems.value.filter(i => !(i.type === item.type && i.id === item.id))
    } else {
      ElMessage.error(data.message || '恢复失败')
    }
  } catch (error) {
    console.error('恢复失败:', error)
    ElMessage.error('恢复失败')
  }
}

async function handleDeletePermanently(item) {
  try {
    await ElMessageBox.confirm(
      `确定要永久删除「${item.title}」吗？此操作不可恢复。`,
      '确认删除',
      {
        type: 'warning',
        confirmButtonText: '永久删除',
        cancelButtonText: '取消'
      }
    )
    
    const response = await fetch('/api/trash/delete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        id: item.id,
        type: item.type
      })
    })
    const data = await response.json()
    if (data.code === 200) {
      ElMessage.success('已永久删除')
      trashItems.value = trashItems.value.filter(i => !(i.type === item.type && i.id === item.id))
    } else {
      ElMessage.error(data.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('永久删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

async function handleClearTrash() {
  try {
    await ElMessageBox.confirm(
      '确定要清空回收站吗？所有项目将被永久删除，此操作不可恢复。',
      '确认清空',
      {
        type: 'warning',
        confirmButtonText: '清空回收站',
        cancelButtonText: '取消'
      }
    )
    
    const response = await fetch('/api/trash/clear', {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    const data = await response.json()
    if (data.code === 200) {
      ElMessage.success('回收站已清空')
      trashItems.value = []
    } else {
      ElMessage.error(data.message || '清空失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空回收站失败:', error)
      ElMessage.error('清空失败')
    }
  }
}

onMounted(() => {
  loadTrash()
})
</script>

<style scoped>
.trash-container {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.trash-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e6e6e6;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.trash-icon {
  color: #ff4d4f;
}

.header-left h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.sub-title {
  margin: 5px 0 0;
  color: #999;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 10px;
}

.loading-container {
  display: flex;
  justify-content: center;
  padding: 100px 0;
}

.empty-state {
  text-align: center;
  padding: 80px 0;
}

.empty-icon {
  color: #d9d9d9;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin: 0 0 10px;
  font-size: 18px;
  color: #333;
}

.empty-state p {
  margin: 0 0 30px;
  color: #999;
}

.trash-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.trash-item {
  transition: all 0.3s ease;
}

.trash-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.item-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.item-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.item-icon.note {
  background: #e6f7ff;
  color: #1890ff;
}

.item-icon.flowchart {
  background: #f6ffed;
  color: #52c41a;
}

.item-icon.table {
  background: #fff7e6;
  color: #fa8c16;
}

.item-icon.whiteboard {
  background: #f9f0ff;
  color: #722ed1;
}

.item-icon.mindmap {
  background: #fff1f0;
  color: #ff4d4f;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-title {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.type-badge {
  padding: 2px 8px;
  background: #f5f5f5;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
}

.delete-time {
  font-size: 12px;
  color: #999;
}

.item-actions {
  display: flex;
  gap: 8px;
}
</style>
