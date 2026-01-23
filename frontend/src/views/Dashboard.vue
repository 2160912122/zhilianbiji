<template>
  <div class="dashboard">
    <!-- 通用统计卡片 -->
    <el-row :gutter="20">
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#409eff"><Document /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.notes || 0 }}</div>
              <div class="stat-label">我的笔记总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#67c23a"><Grid /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.tables || 0 }}</div>
              <div class="stat-label">我的表格总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#e6a23c"><EditPen /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.whiteboards || 0 }}</div>
              <div class="stat-label">我的白板总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#f56c6c"><Connection /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.mindmaps || 0 }}</div>
              <div class="stat-label">我的脑图总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#909399"><Share /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.flowcharts || 0 }}</div>
              <div class="stat-label">我的流程图总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快速创建</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/notes/new')" class="quick-action-btn">
              <el-icon><Document /></el-icon>
              新建笔记
            </el-button>
            <el-button type="success" @click="$router.push('/tables/new')" class="quick-action-btn">
              <el-icon><Grid /></el-icon>
              新建表格
            </el-button>
            <el-button type="warning" @click="$router.push('/whiteboards/new')" class="quick-action-btn">
              <el-icon><EditPen /></el-icon>
              新建白板
            </el-button>
            <el-button type="danger" @click="$router.push('/mindmaps/new')" class="quick-action-btn">
              <el-icon><Connection /></el-icon>
              新建脑图
            </el-button>
            <el-button type="info" @click="$router.push('/flowcharts/new')" class="quick-action-btn">
              <el-icon><Share /></el-icon>
              新建流程图
            </el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近更新</span>
            </div>
          </template>
          <el-empty v-if="recentItems.length === 0" description="暂无内容" />
          <el-timeline v-else>
            <el-timeline-item
              v-for="item in recentItems"
              :key="item.id"
              :timestamp="item.updated_at"
              placement="top"
            >
              <el-link :href="getLink(item)" type="primary">{{ item.title }}</el-link>
              <el-tag size="small" style="margin-left: 10px">{{ getTypeLabel(item.type) }}</el-tag>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
// 替换为统一的请求工具（不再直接用各API文件，避免重复封装）
import request from '@/utils/request'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

// 页面渲染后，异步加载用户信息（不阻塞页面显示）
onMounted(async () => {
  if (localStorage.getItem('token') && !userStore.user) {
    try {
      await userStore.fetchCurrentUser()
      // 加载成功后，更新页面数据（比如笔记总数、表格总数等）
      console.log('用户信息加载成功：', userStore.user)
    } catch (e) {
      console.warn('用户信息加载失败：', e)
      // 加载失败 → 清除token并跳登录
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
  }
})

// 1. 定义数据变量
const stats = ref({
  notes: 0,
  tables: 0,
  whiteboards: 0,
  mindmaps: 0,
  flowcharts: 0
})
const recentItems = ref([])

// 2. 加载数据
async function loadStats() {
  try {
    // 加载当前用户的个人数据
    // 替换原有的多API调用，统一用request请求
    const [notesRes, tablesRes, whiteboardsRes, mindmapsRes, flowchartsRes] = await Promise.all([
      request.get('/api/notes'),
      request.get('/api/tables'),
      request.get('/api/whiteboards'),
      request.get('/api/mindmaps'),
      request.get('/api/flowcharts')
    ])

    // 赋值个人统计数据
    stats.value = {
      notes: Array.isArray(notesRes) ? notesRes.length : 0,
      tables: Array.isArray(tablesRes) ? tablesRes.length : 0,
      whiteboards: Array.isArray(whiteboardsRes) ? whiteboardsRes.length : 0,
      mindmaps: Array.isArray(mindmapsRes) ? mindmapsRes.length : 0,
      flowcharts: Array.isArray(flowchartsRes) ? flowchartsRes.length : 0
    }

    // 整理最近更新的内容
    recentItems.value = [
      ...(Array.isArray(notesRes) ? notesRes.slice(0, 2) : []).map(n => ({ ...n, type: 'note' })),
      ...(Array.isArray(tablesRes) ? tablesRes.slice(0, 2) : []).map(t => ({ ...t, type: 'table' })),
      ...(Array.isArray(whiteboardsRes) ? whiteboardsRes.slice(0, 2) : []).map(w => ({ ...w, type: 'whiteboard' })),
      ...(Array.isArray(mindmapsRes) ? mindmapsRes.slice(0, 2) : []).map(m => ({ ...m, type: 'mindmap' })),
      ...(Array.isArray(flowchartsRes) ? flowchartsRes.slice(0, 2) : []).map(f => ({ ...f, type: 'flowchart' }))
    ]
      .sort((a, b) => new Date(b.updated_at || 0) - new Date(a.updated_at || 0))
      .slice(0, 5)
  } catch (error) {
    console.error('加载数据失败:', error)
    // 权限错误/Token过期会被request.js的响应拦截器处理，自动跳登录页
  }
}

// 4. 辅助函数（保持原有逻辑）
function getLink(item) {
  const links = {
    note: `/notes/${item.id}`,
    table: `/tables/${item.id}`,
    whiteboard: `/whiteboards/${item.id}`,
    mindmap: `/mindmaps/${item.id}`,
    flowchart: `/flowcharts/${item.id}`
  }
  return links[item.type] || '#'
}

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

// 5. 页面挂载时加载数据
onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

/* 原有样式保留并优化 */
.stat-card {
  cursor: pointer;
  transition: transform 0.2s;
}
.stat-card:hover {
  transform: translateY(-5px);
}
.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}
.stat-icon {
  font-size: 48px;
}
.stat-info {
  flex: 1;
}
.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #333;
}
.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 5px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.quick-action-btn {
  width: 100%;
  justify-content: flex-start;
  gap: 10px;
}
</style>