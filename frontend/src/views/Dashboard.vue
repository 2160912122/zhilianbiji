<template>
  <div class="dashboard-container">
    <!-- 顶部导航栏 -->
    <header class="dashboard-header">
      <div class="header-left">
        <h1>流程图管理系统</h1>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleUserCommand">
          <span class="user-info">
            <el-avatar :size="32" :src="userAvatar" />
            <span class="username">{{ user.username }}</span>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <div class="dashboard-content">
      <!-- 侧边栏 - 流程图列表 -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <el-button type="primary" @click="showCreateDialog" style="width: 100%;">
            <el-icon><Plus /></el-icon>新建流程图
          </el-button>
        </div>

        <!-- 搜索区域 -->
        <div class="sidebar-filters">
          <div class="search-box">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索流程图或标签..."
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </div>

        <div class="flowchart-list">
          <div
            v-for="item in filteredFlowcharts"
            :key="item.id"
            class="flowchart-item"
            :class="{ 'active': activeFlowchartId === item.id }"
            @click="selectFlowchart(item.id)"
          >
            <div class="flowchart-info">
              <div class="flowchart-title">{{ item.title }}</div>
              <div class="flowchart-meta">
                <div class="meta-left">
                  <span class="update-time">{{ formatDate(item.updated_at) }}</span>
                  <div class="flowchart-tags">
                  <el-tag
                    v-for="tag in item.tags"
                    :key="tag.id"
                    size="small"
                    type="info"
                    class="flowchart-tag"
                  >
                    {{ tag.name }}
                  </el-tag>
                </div>
                </div>
                <div class="meta-right">
                  <el-tag v-if="item.is_public" type="success" size="small">公开</el-tag>
                </div>
              </div>
            </div>
            <el-dropdown @click.stop @command="handleFlowchartCommand(item.id, $event)">
              <el-icon><More /></el-icon>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="edit">编辑</el-dropdown-item>
                  <el-dropdown-item command="share">分享</el-dropdown-item>
                  <el-dropdown-item command="duplicate">复制</el-dropdown-item>
                  <el-dropdown-item command="delete" style="color: #f56c6c;">删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>

          <!-- 空状态 -->
          <div v-if="filteredFlowcharts.length === 0" class="empty-list">
            <el-empty description="没有找到符合条件的流程图" />
            <div class="empty-hint">
              <p>尝试：</p>
              <ul>
                <li>清除搜索关键词</li>
                <li>取消选择的标签</li>
                <li>创建新的流程图</li>
              </ul>
            </div>
          </div>
        </div>
      </aside>

      <!-- 主内容区 - FlowEditor -->
      <main class="main-content">
        <!-- 流程图编辑器容器 -->
        <div v-if="activeFlowchart" class="flow-editor-container">
          <!-- 使用 FlowEditor 组件 -->
          <FlowEditor
            ref="flowEditor"
            :key="activeFlowchartId"
            :flow-title="activeFlowchart.title"
            :initial-data="graphData"
            :flowchart-id="activeFlowchartId"
            @title-change="handleTitleChange"
            @save="handleSaveFlowchart"
            @share="handleShareFlowchart"
            @export="handleExportFlowchart"
          />
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-editor">
          <el-empty description="选择或创建一个流程图开始编辑" />
          <div class="empty-guide">
            <h3>快速开始：</h3>
            <ul>
              <li>点击左侧「新建流程图」创建新图表</li>
              <li>从左侧选择已有流程图进行编辑</li>
              <li>支持拖拽节点、属性设置、导出分享等功能</li>
            </ul>
          </div>
        </div>
      </main>
    </div>

    <!-- 创建流程图对话框 -->
    <el-dialog v-model="createDialogVisible" title="新建流程图" width="500px">
      <el-form :model="newFlowchartForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input
            v-model="newFlowchartForm.title"
            placeholder="请输入流程图标题"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="标签">
          <div class="tag-input-container">
            <el-select
              v-model="newFlowchartForm.selectedTags"
              multiple
              filterable
              allow-create
              default-first-option
              placeholder="选择或创建标签"
              style="width: 100%;"
            >
              <el-option
                v-for="tag in allTags"
                :key="tag.id"
                :label="tag.name"
                :value="tag.id"
              />
            </el-select>
          </div>
          <div class="tag-hint">
            <small>可以输入新标签创建，多个标签用逗号分隔</small>
          </div>
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="newFlowchartForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入流程图描述（可选）"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            @click="createNewFlowchart"
            :loading="creating"
            :disabled="!newFlowchartForm.title.trim()"
          >
            创建
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 分享对话框 -->
    <el-dialog v-model="shareDialogVisible" title="分享流程图" width="500px">
      <div v-if="shareUrl" class="share-url-container">
        <p>分享链接已生成：</p>
        <el-input v-model="shareUrl" readonly>
          <template #append>
            <el-button @click="copyShareUrl">复制</el-button>
          </template>
        </el-input>
        <p style="margin-top: 10px; color: #666;">该链接有效期为7天</p>
      </div>
      <div v-else>
        <p>确定要分享这个流程图吗？</p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="shareDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmShare" :loading="sharing">确认分享</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  More,
  ArrowDown,
  Search
} from '@element-plus/icons-vue'
import axios from '@/utils/axiosInstance'
import dayjs from 'dayjs'
import FlowEditor from '@/components/FlowEditor.vue'

const router = useRouter()

// 用户信息
const user = ref(JSON.parse(localStorage.getItem('user')) || {})
const userAvatar = computed(() => {
  return user.value.avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
})

// 流程图列表相关
const flowcharts = ref([])
const activeFlowchartId = ref(null)
const activeFlowchart = ref(null)
const graphData = ref({ nodes: {}, edges: {} })

// 标签相关
const allTags = ref([]) // 所有可用标签
const searchKeyword = ref('') // 搜索关键词

// 对话框相关
const createDialogVisible = ref(false)
const shareDialogVisible = ref(false)
const creating = ref(false)
const sharing = ref(false)
const shareUrl = ref('')

// 新流程图表单
const newFlowchartForm = ref({
  title: '新流程图',
  description: '',
  selectedTags: []
})

// 编辑器引用
const flowEditor = ref(null)

// 计算属性：可用的标签（带计数）
const availableTags = computed(() => {
  const tagMap = new Map()

  // 统计每个标签的流程图数量
  flowcharts.value.forEach(flowchart => {
    if (flowchart.tags && flowchart.tags.length > 0) {
      flowchart.tags.forEach(tag => {
        if (tagMap.has(tag.id)) {
          tagMap.get(tag.id).count++
        } else {
          tagMap.set(tag.id, {
            id: tag.id,
            name: tag.name,
            count: 1
          })
        }
      })
    }
  })

  // 转换为数组并按使用次数排序
  return Array.from(tagMap.values()).sort((a, b) => b.count - a.count)
})

// 计算属性：筛选后的流程图列表
const filteredFlowcharts = computed(() => {
  let filtered = flowcharts.value

  // 按关键词搜索（标题、描述、标签）
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.trim().toLowerCase()
    filtered = filtered.filter(item => {
      // 搜索标题和描述
      const matchesTitle = item.title.toLowerCase().includes(keyword)
      const matchesDesc = item.description && item.description.toLowerCase().includes(keyword)
      
      // 搜索标签
      const matchesTags = item.tags && item.tags.some(tag => 
        tag.name.toLowerCase().includes(keyword)
      )
      
      return matchesTitle || matchesDesc || matchesTags
    })
  }

  return filtered
})

// 初始化
onMounted(() => {
  loadFlowcharts()
  loadCurrentUser()
})

// 加载当前用户信息
const loadCurrentUser = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) return

    const response = await axios.get('/api/user', {
      headers: { Authorization: `Bearer ${token}` }
    })
    user.value = response.data.user
  } catch (error) {
    console.error('加载用户信息失败:', error)
  }
}

// 加载流程图列表
const loadFlowcharts = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) return

    const response = await axios.get('/api/flowcharts', {
      headers: { Authorization: `Bearer ${token}` }
    })
    flowcharts.value = response.data

    // 提取所有唯一的标签
    extractAllTags()
  } catch (error) {
    ElMessage.error('加载流程图列表失败')
  }
}

// 提取所有标签
const extractAllTags = () => {
  const tagSet = new Set()
  const tagsMap = new Map()

  flowcharts.value.forEach(flowchart => {
    if (flowchart.tags && flowchart.tags.length > 0) {
      flowchart.tags.forEach(tag => {
        const key = `${tag.id}-${tag.name}`
        if (!tagSet.has(key)) {
          tagSet.add(key)
          tagsMap.set(tag.id, { id: tag.id, name: tag.name })
        }
      })
    }
  })

  allTags.value = Array.from(tagsMap.values())
}

// 显示创建对话框
const showCreateDialog = () => {
  newFlowchartForm.value = {
    title: '新流程图',
    description: '',
    selectedTags: []
  }
  createDialogVisible.value = true
}

// 创建新流程图
const createNewFlowchart = async () => {
  creating.value = true
  try {
    const token = localStorage.getItem('token')

    // 准备标签数据
    const tags = newFlowchartForm.value.selectedTags.map(tagId => {
      // 如果是新创建的标签（字符串形式）
      if (typeof tagId === 'string' && !isNaN(parseInt(tagId))) {
        return { id: parseInt(tagId) }
      } else if (typeof tagId === 'number') {
        return { id: tagId }
      } else {
        // 新标签，只传名称
        return { name: tagId }
      }
    })

    const response = await axios.post('/api/flowcharts', {
      title: newFlowchartForm.value.title,
      description: newFlowchartForm.value.description,
      tags: tags,
      flow_data: { nodes: {}, edges: {} }
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })

    ElMessage.success('创建成功')
    createDialogVisible.value = false

    // 清空当前显示的数据
    activeFlowchartId.value = null
    activeFlowchart.value = null
    graphData.value = { nodes: {}, edges: {} }

    // 重新加载列表
    await loadFlowcharts()

    // 选择新创建的流程图
    await selectFlowchart(response.data.id)
  } catch (error) {
    console.error('创建失败:', error)
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}

// 选择流程图
const selectFlowchart = async (id) => {
  if (activeFlowchartId.value === id && activeFlowchart.value) {
    return
  }

  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`/api/flowcharts/${id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })

    activeFlowchartId.value = id
    activeFlowchart.value = response.data
    graphData.value = { nodes: {}, edges: {} }

    if (activeFlowchart.value.flow_data) {
      graphData.value = JSON.parse(JSON.stringify(activeFlowchart.value.flow_data))
    }

    console.log('流程图加载完成:', id, '数据:', graphData.value)
  } catch (error) {
    console.error('加载流程图失败:', error)
    ElMessage.error('加载流程图失败')
    activeFlowchartId.value = null
    activeFlowchart.value = null
    graphData.value = { nodes: {}, edges: {} }
  }
}

// 处理搜索
const handleSearch = () => {
  // 搜索逻辑已经在 computed 属性中处理
  // 这里可以添加防抖等优化
}

// 处理标题变化
const handleTitleChange = async (newTitle) => {
  if (!activeFlowchart.value) return

  try {
    const token = localStorage.getItem('token')
    await axios.put(`/api/flowcharts/${activeFlowchartId.value}`, {
      title: newTitle
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })

    const flowchart = flowcharts.value.find(f => f.id === activeFlowchartId.value)
    if (flowchart) {
      flowchart.title = newTitle
    }

    ElMessage.success('标题更新成功')
  } catch (error) {
    ElMessage.error('标题更新失败')
  }
}

// 处理保存
const handleSaveFlowchart = async (flowData) => {
  if (!activeFlowchart.value) return

  try {
    const token = localStorage.getItem('token')
    const saveData = {
      flow_data: {
        nodes: flowData.nodes || {},
        edges: flowData.edges || {}
      }
    }

    await axios.put(`/api/flowcharts/${activeFlowchartId.value}`, saveData, {
      headers: { Authorization: `Bearer ${token}` }
    })

    const flowchart = flowcharts.value.find(f => f.id === activeFlowchartId.value)
    if (flowchart) {
      flowchart.updated_at = new Date().toISOString()
    }

    ElMessage.success('保存成功')
    return { success: true, message: '保存成功' }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
    return { success: false, message: '保存失败' }
  }
}

// 处理分享
const handleShareFlowchart = () => {
  shareFlowchart()
}

// 处理导出
const handleExportFlowchart = async (imageData, format = 'svg') => {
  try {
    if (imageData) {
      const link = document.createElement('a')
      link.download = `${activeFlowchart.value.title || 'flowchart'}.${format}`
      link.href = imageData
      link.click()
      ElMessage.success('导出成功')
    } else if (flowEditor.value) {
      const result = await flowEditor.value.exportFlowchart()
      if (result.success) {
        ElMessage.success('导出成功')
      } else {
        ElMessage.error(result.message || '导出失败')
      }
    }
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

// 分享流程图
const shareFlowchart = () => {
  shareDialogVisible.value = true
  shareUrl.value = ''
}

// 确认分享
const confirmShare = async () => {
  if (!activeFlowchartId.value) return

  sharing.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.post(`/api/flowcharts/${activeFlowchartId.value}/share`, {
      days: 7
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })

    shareUrl.value = `${window.location.origin}${response.data.share_url}`
    ElMessage.success('分享链接已生成')

    activeFlowchart.value.is_public = true
    const flowchart = flowcharts.value.find(f => f.id === activeFlowchartId.value)
    if (flowchart) {
      flowchart.is_public = true
    }
  } catch (error) {
    ElMessage.error('分享失败')
  } finally {
    sharing.value = false
  }
}

// 复制分享链接
const copyShareUrl = () => {
  navigator.clipboard.writeText(shareUrl.value)
  ElMessage.success('链接已复制到剪贴板')
}

// 处理流程图命令
const handleFlowchartCommand = async (id, command) => {
  if (command === 'edit') {
    selectFlowchart(id)
  } else if (command === 'share') {
    activeFlowchartId.value = id
    shareFlowchart()
  } else if (command === 'duplicate') {
    try {
      const token = localStorage.getItem('token')
      await axios.post(`/api/flowcharts/${id}/duplicate`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      })

      ElMessage.success('复制成功')
      await loadFlowcharts()
    } catch (error) {
      ElMessage.error('复制失败')
    }
  } else if (command === 'delete') {
    try {
      await ElMessageBox.confirm('确定要删除这个流程图吗？', '提示', {
        type: 'warning'
      })

      const token = localStorage.getItem('token')
      await axios.delete(`/api/flowcharts/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })

      ElMessage.success('删除成功')

      if (activeFlowchartId.value === id) {
        activeFlowchartId.value = null
        activeFlowchart.value = null
        graphData.value = { nodes: {}, edges: {} }
      }

      await loadFlowcharts()
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('删除失败')
      }
    }
  }
}

// 处理用户命令
const handleUserCommand = (command) => {
  if (command === 'logout') {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  } else if (command === 'profile') {
    ElMessage.info('个人中心功能开发中')
  }
}

// 格式化日期
const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 60px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
  z-index: 100;
}

.header-left h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  margin: 0 8px;
  font-weight: 500;
}

.dashboard-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  min-height: 0;
}

.sidebar {
  width: 350px;
  background: #f8f9fa;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  flex-shrink: 0;
  min-height: 0;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.sidebar-filters {
  padding: 0 20px 20px;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.search-box {
  margin-bottom: 16px;
}

.tags-filter {
  background: white;
  border-radius: 6px;
  padding: 12px;
  border: 1px solid #e4e7ed;
}

.tags-filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.filter-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.tags-list {
  max-height: 200px;
  overflow-y: auto;
}

.tag-item {
  margin-bottom: 8px;
}

.tag-item:last-child {
  margin-bottom: 0;
}

.tag-item .el-checkbox {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tag-label {
  flex: 1;
}

.tag-count {
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  padding: 1px 6px;
  border-radius: 10px;
  margin-left: 8px;
}

.flowchart-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  min-height: 0;
}

.flowchart-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.flowchart-item:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.flowchart-item.active {
  border-color: #409EFF;
  background: #ecf5ff;
}

.flowchart-info {
  flex: 1;
  overflow: hidden;
  min-width: 0;
}

.flowchart-title {
  font-weight: 500;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.flowchart-meta {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  font-size: 12px;
  color: #909399;
  gap: 8px;
}

.meta-left {
  flex: 1;
  overflow: hidden;
  min-width: 0;
}

.update-time {
  display: block;
  margin-bottom: 6px;
  white-space: nowrap;
}

.flowchart-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.flowchart-tag {
  cursor: pointer;
  transition: all 0.2s;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.flowchart-tag:hover {
  opacity: 0.8;
  transform: translateY(-1px);
}

.meta-right {
  flex-shrink: 0;
}

.empty-list {
  text-align: center;
  padding: 40px 20px;
}

.empty-hint {
  margin-top: 16px;
  padding: 16px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.empty-hint p {
  margin: 0 0 8px 0;
  font-weight: 500;
  color: #303133;
}

.empty-hint ul {
  margin: 0;
  padding-left: 20px;
  text-align: left;
  color: #606266;
}

.empty-hint li {
  margin-bottom: 4px;
  line-height: 1.4;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  overflow: hidden;
  min-height: 0;
}

.flow-editor-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  min-height: 0;
}

.empty-editor {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: #f8f9fa;
  min-height: 0;
  padding: 40px 20px;
}

.empty-guide {
  margin-top: 30px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  width: 90%;
}

.empty-guide h3 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
}

.empty-guide ul {
  margin: 0;
  padding-left: 20px;
  color: #606266;
}

.empty-guide li {
  margin-bottom: 8px;
  line-height: 1.6;
}

.tag-input-container {
  margin-bottom: 4px;
}

.tag-hint {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}

.share-url-container {
  padding: 8px 0;
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .sidebar {
    width: 320px;
  }

  .dashboard-header {
    padding: 0 16px;
  }
}

@media (max-width: 992px) {
  .sidebar {
    width: 280px;
  }
}

@media (max-width: 768px) {
  .dashboard-content {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    height: 400px;
    border-right: none;
    border-bottom: 1px solid #e4e7ed;
    min-height: 400px;
  }

  .sidebar-header {
    padding: 16px;
  }

  .sidebar-filters {
    padding: 0 16px 16px;
  }

  .flowchart-list {
    padding: 16px;
  }

  .flowchart-item {
    padding: 12px;
  }

  .flowchart-meta {
    flex-direction: column;
    gap: 6px;
  }

  .meta-left {
    width: 100%;
  }

  .meta-right {
    align-self: flex-end;
  }

  .empty-guide {
    width: 95%;
    padding: 16px;
    margin-top: 20px;
  }

  .empty-guide h3 {
    font-size: 14px;
  }

  .empty-guide li {
    font-size: 13px;
    margin-bottom: 6px;
  }
}
</style>