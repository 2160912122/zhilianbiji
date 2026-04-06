<template>
  <div class="dashboard">
    <!-- 页面标题和刷新按钮 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">仪表盘</h1>
          <p class="page-desc">欢迎回来，{{ userStore.user?.username || '用户' }}！这里是您的个人数据概览</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="loadStats" :loading="loading" round class="refresh-btn">
            <el-icon><Refresh /></el-icon>
            <span>刷新数据</span>
          </el-button>
        </div>
      </div>
      <!-- 科技感装饰元素 -->
      <div class="tech-decoration">
        <div class="tech-line"></div>
        <div class="tech-dot"></div>
        <div class="tech-dot"></div>
        <div class="tech-dot"></div>
      </div>
    </div>
    
    <!-- 通用统计卡片 -->
    <el-row :gutter="24">
      <el-col :span="6">
        <el-card class="stat-card" hover>
          <div class="stat-content">
            <div class="stat-icon-container primary">
              <el-icon class="stat-icon"><Document /></el-icon>
              <div class="stat-glow"></div>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.notes || 0 }}</div>
              <div class="stat-label">笔记</div>
              <div class="stat-trend positive">
                <el-icon><CaretTop /></el-icon>
                <span>2.5%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" hover>
          <div class="stat-content">
            <div class="stat-icon-container success">
              <el-icon class="stat-icon"><Grid /></el-icon>
              <div class="stat-glow"></div>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.tables || 0 }}</div>
              <div class="stat-label">表格</div>
              <div class="stat-trend positive">
                <el-icon><CaretTop /></el-icon>
                <span>1.8%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" hover>
          <div class="stat-content">
            <div class="stat-icon-container warning">
              <el-icon class="stat-icon"><EditPen /></el-icon>
              <div class="stat-glow"></div>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.whiteboards || 0 }}</div>
              <div class="stat-label">白板</div>
              <div class="stat-trend positive">
                <el-icon><CaretTop /></el-icon>
                <span>3.2%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" hover>
          <div class="stat-content">
            <div class="stat-icon-container danger">
              <el-icon class="stat-icon"><Connection /></el-icon>
              <div class="stat-glow"></div>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.mindmaps || 0 }}</div>
              <div class="stat-label">脑图</div>
              <div class="stat-trend positive">
                <el-icon><CaretTop /></el-icon>
                <span>4.5%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" hover>
          <div class="stat-content">
            <div class="stat-icon-container info">
              <el-icon class="stat-icon"><Share /></el-icon>
              <div class="stat-glow"></div>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.flowcharts || 0 }}</div>
              <div class="stat-label">流程图</div>
              <div class="stat-trend positive">
                <el-icon><CaretTop /></el-icon>
                <span>2.1%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="18">
        <el-card class="stat-card summary-card" hover>
          <div class="stat-content summary-content">
            <div class="summary-info">
              <div class="summary-title">总资源</div>
              <div class="summary-value">{{ totalResources }}</div>
              <div class="summary-desc">您的所有创作内容</div>
            </div>
            <div class="summary-chart">
              <div class="chart-container">
                <el-progress 
                  :percentage="resourceUsage" 
                  :stroke-width="12" 
                  :color="resourceUsageColor" 
                  status="success"
                  class="progress-bar"
                />
                <div class="chart-text">{{ resourceUsage }}% 利用率</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24" style="margin-top: 24px">
      <el-col :span="12">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">快速创建</span>
              <el-icon class="card-icon"><Plus /></el-icon>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/notes/new')" class="quick-action-btn">
              <div class="btn-icon primary"><el-icon><Document /></el-icon></div>
              <div class="btn-content">
                <div class="btn-title">新建笔记</div>
                <div class="btn-desc">创建富文本笔记</div>
              </div>
            </el-button>
            <el-button type="success" @click="$router.push('/tables/new')" class="quick-action-btn">
              <div class="btn-icon success"><el-icon><Grid /></el-icon></div>
              <div class="btn-content">
                <div class="btn-title">新建表格</div>
                <div class="btn-desc">创建数据表格</div>
              </div>
            </el-button>
            <el-button type="warning" @click="$router.push('/whiteboards/new')" class="quick-action-btn">
              <div class="btn-icon warning"><el-icon><EditPen /></el-icon></div>
              <div class="btn-content">
                <div class="btn-title">新建白板</div>
                <div class="btn-desc">创建协作白板</div>
              </div>
            </el-button>
            <el-button type="danger" @click="$router.push('/mindmaps/new')" class="quick-action-btn">
              <div class="btn-icon danger"><el-icon><Connection /></el-icon></div>
              <div class="btn-content">
                <div class="btn-title">新建脑图</div>
                <div class="btn-desc">创建思维导图</div>
              </div>
            </el-button>
            <el-button type="info" @click="$router.push('/flowcharts/new')" class="quick-action-btn">
              <div class="btn-icon info"><el-icon><Share /></el-icon></div>
              <div class="btn-content">
                <div class="btn-title">新建流程图</div>
                <div class="btn-desc">创建流程图表</div>
              </div>
            </el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="dashboard-card ai-enhanced">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <span class="card-title">最近更新</span>
                <el-tag size="small" type="primary" effect="dark" class="ai-tag">AI 增强</el-tag>
              </div>
              <el-icon class="card-icon"><Clock /></el-icon>
            </div>
          </template>
          <el-empty v-if="recentItems.length === 0" description="暂无内容" />
          <div v-else class="recent-items">
            <div 
              v-for="(item, index) in recentItems" 
              :key="item.id" 
              class="recent-item"
              :class="{ 'ai-highlight': index < 2 }"
              @click="navigateToItem(item)"
            >
              <div class="item-icon" :class="getItemTypeClass(item.type)">
                <el-icon :size="20">
                  <component :is="getItemIcon(item.type)" />
                </el-icon>
                <div v-if="index < 2" class="ai-badge">AI</div>
              </div>
              <div class="item-content">
                <div class="item-title">{{ item.title }}</div>
                <div class="item-meta">
                  <span class="item-type">{{ getTypeLabel(item.type) }}</span>
                  <span class="item-time">{{ formatTime(item.updated_at) }}</span>
                  <span v-if="index < 2" class="ai-suggestion">AI 推荐</span>
                </div>
                <div v-if="index < 2" class="item-ai-summary">
                  {{ getAISummary(item) }}
                </div>
              </div>
              <el-icon class="item-arrow"><ArrowRight /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24" style="margin-top: 24px">
      <el-col :span="24">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">使用统计</span>
              <el-icon class="card-icon"><DataAnalysis /></el-icon>
            </div>
          </template>
          <div class="usage-stats">
            <div class="stat-item">
              <div class="stat-icon"><el-icon><Plus /></el-icon></div>
              <div class="stat-label">本月创建</div>
              <div class="stat-value">{{ monthlyCreated }}</div>
              <div class="stat-change positive">+12.5%</div>
            </div>
            <div class="stat-item">
              <div class="stat-icon"><el-icon><Edit /></el-icon></div>
              <div class="stat-label">本月编辑</div>
              <div class="stat-value">{{ monthlyEdited }}</div>
              <div class="stat-change positive">+8.3%</div>
            </div>
            <div class="stat-item">
              <div class="stat-icon"><el-icon><Share /></el-icon></div>
              <div class="stat-label">分享次数</div>
              <div class="stat-value">{{ shareCount }}</div>
              <div class="stat-change positive">+5.2%</div>
            </div>
            <div class="stat-item">
              <div class="stat-icon"><el-icon><Cpu /></el-icon></div>
              <div class="stat-label">AI 使用</div>
              <div class="stat-value">{{ aiUsage }}</div>
              <div class="stat-change positive">+15.8%</div>
            </div>
          </div>
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
import {
  Refresh, CaretTop, Plus, Clock, DataAnalysis, ArrowRight,
  Document, Grid, EditPen, Connection, Share
} from '@element-plus/icons-vue'

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
const loading = ref(false)

// 模拟数据
const monthlyCreated = ref(12)
const monthlyEdited = ref(35)
const shareCount = ref(8)
const aiUsage = ref(15)

// 计算属性
const totalResources = computed(() => {
  return Object.values(stats.value).reduce((sum, value) => sum + value, 0)
})

const resourceUsage = computed(() => {
  const total = totalResources.value
  return total > 0 ? Math.min(Math.round((total / 100) * 100), 100) : 0
})

const resourceUsageColor = computed(() => {
  const usage = resourceUsage.value
  if (usage < 30) return '#67c23a'
  if (usage < 70) return '#e6a23c'
  return '#f56c6c'
})

// 2. 加载数据
async function loadStats() {
  loading.value = true
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

    // 处理后端返回的数据格式（code, message, data）
const getArrayData = (res) => {
  console.log('处理API响应数据:', res)
  if (res && typeof res === 'object') {
    // 检查是否是标准API响应格式
    if (res.code === 200 && Array.isArray(res.data)) {
      return res.data
    }
    // 检查是否直接返回了数组
    if (Array.isArray(res)) {
      return res
    }
  }
  return []
}

    // 提取数据数组
    const notesData = getArrayData(notesRes)
    const tablesData = getArrayData(tablesRes)
    const whiteboardsData = getArrayData(whiteboardsRes)
    const mindmapsData = getArrayData(mindmapsRes)
    const flowchartsData = getArrayData(flowchartsRes)

    // 赋值个人统计数据
    stats.value = {
      notes: notesData.length,
      tables: tablesData.length,
      whiteboards: whiteboardsData.length,
      mindmaps: mindmapsData.length,
      flowcharts: flowchartsData.length
    }

    console.log('仪表盘数据:', stats.value)

    // 整理最近更新的内容
    recentItems.value = [
      ...notesData.slice(0, 2).map(n => ({ ...n, type: 'note' })),
      ...tablesData.slice(0, 2).map(t => ({ ...t, type: 'table' })),
      ...whiteboardsData.slice(0, 2).map(w => ({ ...w, type: 'whiteboard' })),
      ...mindmapsData.slice(0, 2).map(m => ({ ...m, type: 'mindmap' })),
      ...flowchartsData.slice(0, 2).map(f => ({ ...f, type: 'flowchart' }))
    ]
      .sort((a, b) => new Date(b.updated_at || 0) - new Date(a.updated_at || 0))
      .slice(0, 5)

    console.log('最近更新内容:', recentItems.value)
    // 检查每个项目的type属性
    recentItems.value.forEach((item, index) => {
      console.log(`项目${index}类型:`, item.type, '类型:', typeof item.type)
    })
  } catch (error) {
    console.error('加载数据失败:', error)
    // 权限错误/Token过期会被request.js的响应拦截器处理，自动跳登录页
  } finally {
    loading.value = false
  }
}

// 辅助函数
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

function navigateToItem(item) {
  router.push(getLink(item))
}

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

function getAISummary(item) {
  // 模拟AI摘要，实际项目中可以调用AI API生成
  const summaries = {
    note: '这是一篇关于项目计划的笔记，包含了详细的任务分配和时间线。',
    table: '这是一个包含销售数据的表格，记录了最近一个季度的业绩情况。',
    whiteboard: '这是一个团队协作白板，包含了项目 brainstorming 的结果。',
    mindmap: '这是一个关于产品功能的思维导图，展示了核心功能模块和关系。',
    flowchart: '这是一个业务流程图表，描述了客户服务的处理流程。'
  }
  return summaries[item.type] || '这是一个重要的文档，值得您的关注。'
}

// 页面挂载时加载数据
onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
  background-color: var(--background-color, #f0f2f5);
  min-height: 100vh;
}

/* 页面标题和刷新按钮区域样式 */
.page-header {
  margin-bottom: 24px;
  padding: 40px;
  background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
  border-radius: var(--border-radius-lg, 12px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  color: white;
  position: relative;
  overflow: hidden;
}

.page-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(64, 158, 255, 0.1), rgba(102, 126, 234, 0.1));
  z-index: 1;
}

.header-content {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.header-left {
  flex: 1;
  min-width: 300px;
}

.page-title {
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 12px 0;
  color: white;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-desc {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 18px;
  font-weight: 400;
  line-height: 1.4;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.refresh-btn {
  background: linear-gradient(135deg, #409eff, #66b1ff);
  border: none;
  box-shadow: 0 4px 15px rgba(64, 158, 255, 0.4);
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.6);
}

/* 科技感装饰元素 */
.tech-decoration {
  position: absolute;
  bottom: 20px;
  left: 40px;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.tech-line {
  width: 100px;
  height: 2px;
  background: linear-gradient(90deg, #409eff, transparent);
}

.tech-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #409eff;
  box-shadow: 0 0 10px #409eff;
  animation: pulse 2s infinite;
}

.tech-dot:nth-child(2) {
  animation-delay: 0.3s;
}

.tech-dot:nth-child(3) {
  animation-delay: 0.6s;
}

.tech-dot:nth-child(4) {
  animation-delay: 0.9s;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}

/* 统计卡片样式 */
.stat-card {
  cursor: pointer;
  transition: all 0.3s ease;
  height: 180px;
  border-radius: var(--border-radius-lg, 12px);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.stat-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  border-color: #409eff;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 24px;
  width: 100%;
  height: 140px;
  padding: 24px;
  box-sizing: border-box;
  position: relative;
  overflow: hidden;
}

.stat-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #409eff, #667eea);
}

.stat-icon-container {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 1;
}

.stat-icon-container.primary {
  background: linear-gradient(135deg, #409eff, #66b1ff);
  color: white;
}

.stat-icon-container.success {
  background: linear-gradient(135deg, #67c23a, #85ce61);
  color: white;
}

.stat-icon-container.warning {
  background: linear-gradient(135deg, #e6a23c, #ebb563);
  color: white;
}

.stat-icon-container.danger {
  background: linear-gradient(135deg, #f56c6c, #f78989);
  color: white;
}

.stat-icon-container.info {
  background: linear-gradient(135deg, #909399, #a6a9ad);
  color: white;
}

.stat-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.4) 0%, transparent 70%);
  z-index: -1;
}

.stat-icon {
  font-size: 32px;
  transition: all 0.3s ease;
}

.stat-card:hover .stat-icon {
  transform: scale(1.1);
}

.stat-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
  z-index: 1;
}

.stat-value {
  font-size: 40px;
  font-weight: 700;
  color: var(--text-primary, #303133);
  margin: 0;
  line-height: 1;
  background: linear-gradient(135deg, #303133, #606266);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 16px;
  color: var(--text-secondary, #606266);
  margin: 0;
  font-weight: 500;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 600;
  animation: fadeIn 0.5s ease-in-out;
}

.stat-trend.positive {
  color: var(--success-color, #67c23a);
}

.stat-trend.negative {
  color: var(--danger-color, #f56c6c);
}

/* 汇总卡片 */
.summary-card {
  height: 180px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
}

.summary-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 40px;
}

.summary-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-title {
  font-size: 16px;
  color: var(--text-secondary, #606266);
  font-weight: 600;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.summary-value {
  font-size: 56px;
  font-weight: 700;
  color: var(--text-primary, #303133);
  margin: 0;
  line-height: 1;
  background: linear-gradient(135deg, #409eff, #667eea);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.summary-desc {
  font-size: 14px;
  color: var(--text-light, #909399);
  margin: 0;
}

.summary-chart {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-container {
  position: relative;
  width: 140px;
  height: 140px;
}

.progress-bar {
  --el-progress-color: linear-gradient(135deg, #409eff, #667eea);
}

.chart-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary, #303133);
  text-align: center;
  background: linear-gradient(135deg, #409eff, #667eea);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 仪表盘卡片 */
.dashboard-card {
  border-radius: var(--border-radius-lg, 12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.dashboard-card:hover {
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  border-color: #409eff;
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

.card-header .header-left {
  display: flex;
  align-items: center;
  gap: 12px;
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

.ai-tag {
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 12px;
  background: linear-gradient(135deg, #409eff, #667eea);
  color: white;
}

.card-icon {
  font-size: 20px;
  color: var(--text-light, #909399);
  transition: all 0.3s ease;
}

.dashboard-card:hover .card-icon {
  color: #409eff;
  transform: rotate(15deg);
}

.ai-enhanced {
  border-left: 4px solid #409eff;
  box-shadow: 0 4px 15px rgba(64, 158, 255, 0.2);
}

/* 快速操作按钮 */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px;
}

.quick-action-btn {
  width: 100%;
  justify-content: flex-start;
  gap: 16px;
  align-items: center;
  padding: 20px 24px;
  height: 90px;
  border-radius: var(--border-radius-lg, 12px);
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(5px);
}

.quick-action-btn:hover {
  transform: translateX(8px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  border-color: #409eff;
  background: rgba(64, 158, 255, 0.05);
}

.btn-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  position: relative;
  overflow: hidden;
}

.btn-icon::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  transition: all 0.6s ease;
}

.btn-icon:hover::before {
  left: 100%;
}

.btn-icon.primary {
  background: linear-gradient(135deg, #409eff, #66b1ff);
  color: white;
}

.btn-icon.success {
  background: linear-gradient(135deg, #67c23a, #85ce61);
  color: white;
}

.btn-icon.warning {
  background: linear-gradient(135deg, #e6a23c, #ebb563);
  color: white;
}

.btn-icon.danger {
  background: linear-gradient(135deg, #f56c6c, #f78989);
  color: white;
}

.btn-icon.info {
  background: linear-gradient(135deg, #909399, #a6a9ad);
  color: white;
}

.btn-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-start;
}

.btn-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #303133);
}

.btn-desc {
  font-size: 14px;
  color: var(--text-secondary, #606266);
}

/* 最近更新 */
.recent-items {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recent-item {
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
}

.recent-item:hover {
  background-color: rgba(64, 158, 255, 0.05);
  transform: translateX(8px);
  box-shadow: 0 8px 20px rgba(64, 158, 255, 0.2);
  border-color: #409eff;
}

.recent-item.ai-highlight {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.1), rgba(102, 126, 234, 0.1));
  border: 1px solid #409eff;
  box-shadow: 0 4px 15px rgba(64, 158, 255, 0.3);
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

.ai-badge {
  position: absolute;
  top: -10px;
  right: -10px;
  background: linear-gradient(135deg, #409eff, #667eea);
  color: white;
  font-size: 10px;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(64, 158, 255, 0.4);
  animation: pulse 2s infinite;
}

.ai-suggestion {
  background: linear-gradient(135deg, #409eff, #667eea);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 600;
}

.item-ai-summary {
  margin-top: 12px;
  font-size: 14px;
  color: var(--text-secondary, #606266);
  line-height: 1.4;
  padding: 12px;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: var(--border-radius-md, 8px);
  border-left: 4px solid #409eff;
  animation: fadeIn 0.5s ease-in-out;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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

.item-arrow {
  font-size: 20px;
  color: var(--text-light, #909399);
  transition: all 0.3s ease;
  flex-shrink: 0;
  margin-top: 4px;
}

.recent-item:hover .item-arrow {
  color: #409eff;
  transform: translateX(8px);
}

/* 使用统计 */
.usage-stats {
  padding: 24px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(5px);
  border-radius: var(--border-radius-lg, 12px);
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.stat-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #409eff, #667eea);
}

.stat-item:hover {
  transform: translateY(-8px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  border-color: #409eff;
}

.stat-item .stat-icon {
  font-size: 32px;
  margin-bottom: 12px;
  color: #409eff;
  transition: all 0.3s ease;
}

.stat-item:hover .stat-icon {
  transform: scale(1.2) rotate(15deg);
}

.stat-item .stat-label {
  font-size: 16px;
  color: var(--text-secondary, #606266);
  margin-bottom: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.stat-item .stat-value {
  font-size: 36px;
  font-weight: 700;
  color: var(--text-primary, #303133);
  margin-bottom: 8px;
  line-height: 1;
  background: linear-gradient(135deg, #409eff, #667eea);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-item .stat-change {
  font-size: 14px;
  font-weight: 600;
  animation: fadeIn 0.5s ease-in-out;
}

.stat-item .stat-change.positive {
  color: var(--success-color, #67c23a);
}

.stat-item .stat-change.negative {
  color: var(--danger-color, #f56c6c);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .summary-content {
    gap: 20px;
  }
  
  .usage-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .tech-decoration {
    display: none;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 30px;
  }
  
  .page-title {
    font-size: 28px;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .stat-card {
    height: 160px;
  }
  
  .stat-content {
    padding: 20px;
    gap: 16px;
  }
  
  .stat-icon-container {
    width: 60px;
    height: 60px;
  }
  
  .stat-value {
    font-size: 32px;
  }
  
  .summary-card {
    height: auto;
  }
  
  .summary-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
  }
  
  .quick-action-btn {
    height: 80px;
    padding: 16px 20px;
  }
  
  .usage-stats {
    grid-template-columns: 1fr;
  }
  
  .tech-decoration {
    display: none;
  }
}
</style>