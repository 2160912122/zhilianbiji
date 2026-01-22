<template>
  <div class="mindmap-home-container">
    <!-- 抽离：顶部导航栏组件 -->
    <HomeHeader 
      :currentUser="currentUser"
      @logout="handleLogout"
      @login="handleLogin"
    />

    <!-- 编辑态：显示工具栏与画布；列表态：显示列表 -->
    <div v-if="isEditing" class="mindmap-editor">
      <div class="editor-top">
        <button class="btn-back-list" @click="exitEditor">← 返回主页</button>
      </div>

      <div class="editor-layout" style="display:flex; gap:12px; padding:12px; height: calc(100vh - 120px);">
          <MindmapSidebar
        :mapList="mindMapList"
        :filterMapList="filterMapList"
        :allTags="allTags"
        v-model:searchKw="searchKw"
        v-model:searchType="searchType"
        :currentId="currentMap.id"
        :formatTime="formatTime"
        @newMap="handleCreateMindMap"
        @openMap="handleOpenMindMap"
        @filterByCategory="handleFilterByCategory"
        @manageTags="(id)=>{ const m = mindMapList.find(x=>x.id===id); if(m && typeof m === 'object'){ Object.assign(currentMap,m); showTagsModal = true } else { showToast('找不到对应的脑图'); } }"
        @delMap="handleDelMindMap"
      />

        <div class="editor-area" style="flex:1;display:flex;flex-direction:column;">
          <HomeToolbar
            @newMap="handleCreateMindMap"
            @saveMap="onSaveMap"
            @exportMap="onExportMap"
            @shareMap="onShareMap"
            @manageAllTags="onManageTags"
            @showVersionHistory="onShowVersionHistory"
            @openAIAssistant="openAIAssistant"
            @openEnhancedAIAssistant="openEnhancedAIAssistant"
            @toggleCommentPanel="() => toggleCommentPanel()"
            @addChild="handleAddChild"
            @addBro="handleAddBro"
            @editNode="handleEditNode"
            @delNode="handleDelNode"
            @moveUp="handleMoveUp"
            @moveDown="handleMoveDown"
            @toggleNode="handleToggleNode"
            @zoomIn="handleZoomIn"
            @zoomOut="handleZoomOut"
            @resetZoom="handleResetZoom"
            @undo="handleUndo"
            @redo="handleRedo"
          />

          <MindmapCanvas ref="canvas" :currentId="currentMap.id" @canvasError="(...args) => handleCanvasError(...args)" />
        </div>
      </div>
    </div>

    <div v-else class="mindmap-list">
      <!-- 抽离：空状态组件 -->
      <HomeEmpty v-if="mindMapList.length === 0" @createMindMap="handleCreateMindMap" />

      <!-- 脑图列表卡片 -->
      <van-cell-group :border="false" class="list-wrap">
        <MindmapItem
          v-for="(item, index) in mindMapList"
          :key="index"
          :map-item="item"
          :index="index"
          @openMindMap="handleOpenMindMap"
          @openShare="handleOpenShare"
          @openTags="handleOpenTags"
          @delMindMap="handleDelMindMap"
        />
      </van-cell-group>
    </div>

    <!-- ===== 原有的所有弹窗组件 完全保留 无需任何修改 ===== -->
    <ShareModal
      v-model:show="showShareModal"
      :mind-map-title="currentMap.title"
      :mind-map-link="currentMap.shareLink"
      :mind-map-id="currentMap.id?.toString() || ''"
      @share="handleMapShare"
    />
    <TagsModal
      v-model:show="showTagsModal"
      :tags="currentMap.tags"
      :category="currentMap.category"
      :max-tag-num="8"
      @confirm="handleTagSave"
    />
    <AIAssistantModal v-model:show="showAIModal" />
    <EnhancedAIModal v-model:show="showEnhancedAIModal" />
    <VersionHistoryModal v-model:show="showVersionHistoryModal" :mindmap-id="currentMap.id" @restore="onVersionRestored" />
    <CommentPanel :modelValue="commentPanelVisible" :currentId="currentMap.id" :currentUser="$root.currentUser" @update:modelValue="val=>commentPanelVisible=val" />
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showConfirmDialog } from 'vant'
import { createMindmap, updateMindmap, deleteMindmap } from '@/api/mindmapApi'
import { getUserInfo, userLogout } from '@/api/authApi'
import request from '@/utils/request'
import MindmapSidebar from './MindmapSidebar.vue'

// 引入抽离的子组件 + 原有弹窗组件
import HomeHeader from './HomeHeader.vue'
import HomeEmpty from './HomeEmpty.vue'
import MindmapItem from './MindmapItem.vue'
import HomeToolbar from './HomeToolbar.vue'
import MindmapCanvas from './MindmapCanvas.vue'
import ShareModal from './modal/ShareModal.vue'
import TagsModal from './modal/TagsModal.vue'
import VersionHistoryModal from './modal/VersionHistoryModal.vue'
import CommentPanel from './comment/CommentPanel.vue'
import AIAssistantModal from './modal/AIAssistantModal.vue'
import EnhancedAIModal from './modal/EnhancedAIModal.vue'

// ===== 你原有的所有响应式数据 完全保留 无任何修改 =====
const mindMapList = ref([])
const currentMap = reactive({ id: '', title: '', tags: [], shareLink: '', category: '' })
const currentUser = ref({})

// 初始化router
const router = useRouter()
const showShareModal = ref(false)
const showTagsModal = ref(false)
const showAIModal = ref(false)
const showEnhancedAIModal = ref(false)
const isEditing = ref(false)
const canvas = ref(null)

// 格式化时间函数
const formatTime = (time) => {
  if (!time) return ''
  try {
    const date = new Date(time)
    if (isNaN(date.getTime())) return time
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  } catch (error) {
    return time
  }
}

const handleCanvasError = (err, type = 'error') => {
  // 处理画布错误
  console.error('Canvas Error:', err)
  // 根据错误类型显示相应的提示
  if (err.includes('导出成功')) {
    showToast(err, { type: 'success' })
  } else if (err.includes('正在') || err.includes('尝试')) {
    showToast(err, { type: 'info' })
  } else if (err.includes('失败')) {
    showToast(err, { type: 'error' })
  } else {
    showToast(err, { type })
  }
}

// AI助手相关方法
const openAIAssistant = () => {
  showAIModal.value = true
}

const openEnhancedAIAssistant = () => {
  showEnhancedAIModal.value = true
}

// ===== 你原有的所有核心业务方法（已增强：优先调用后端创建） =====
const handleCreateMindMap = async () => {
  // 弹窗让用户输入名称与主题，确保名称不重复
  let title = window.prompt('请输入脑图名称（必填）', `新建脑图${mindMapList.value.length + 1}`)
  if (!title || !title.trim()) return
  
  // 检查脑图名称是否重复
  while (title && title.trim()) {
    const isDuplicate = mindMapList.value.some(map => map.title === title.trim())
    if (isDuplicate) {
      title = window.prompt('脑图名称已存在，请输入新的名称', title)
      if (!title || !title.trim()) return
    } else {
      break
    }
  }
  
  const topic = window.prompt('请输入根主题名称（可选，留空则使用名称）', title) || title
  
  // 选择分类
  const categoryOptions = ['工作', '学习', '个人', '其他']
  const categoryPrompt = `请选择脑图分类（输入序号）：\n1. 工作\n2. 学习\n3. 个人\n4. 其他`
  let categoryIndex = parseInt(window.prompt(categoryPrompt, '4')) - 1
  
  // 验证分类输入
  if (isNaN(categoryIndex) || categoryIndex < 0 || categoryIndex >= categoryOptions.length) {
    categoryIndex = 3 // 默认选择其他
  }
  
  const categoryMap = {
    0: 'work',
    1: 'study',
    2: 'personal',
    3: ''
  }
  const category = categoryMap[categoryIndex]

  const defaultData = {
    meta: { name: title, author: '未知用户', version: '1.0' },
    format: 'node_tree',
    data: { id: 'root', topic: topic, direction: 'right', expanded: true, children: [] }
  }
  try {
    const res = await createMindmap({ name: title, data: defaultData, category: category })
    const newMap = res.data
    const mapItem = { id: newMap.id || newMap._id || (new Date().getTime()), title: newMap.name || title, createTime: new Date().toISOString(), tags: newMap.tags || [], category: newMap.category || category, shareLink: newMap.share_link || `${window.location.origin}/share/mindmap/${newMap.id || ''}` }
    mindMapList.value.unshift(mapItem)
    currentMap.id = mapItem.id
    currentMap.title = mapItem.title
    currentMap.tags = newMap.tags || []
    currentMap.category = newMap.category || category
    currentMap.shareLink = mapItem.shareLink
    isEditing.value = true
    nextTick(() => { if (canvas.value && typeof canvas.value.openMap === 'function') canvas.value.openMap(currentMap.id) })
    showToast('脑图创建成功 ✅')
  } catch (err) {
    // 回退到本地临时创建
    const newId = (new Date().getTime())
    mindMapList.value.unshift({ id: newId, title, createTime: new Date().toISOString(), tags: [], category: category, shareLink: `${window.location.origin}/share/mindmap/${newId}` })
    currentMap.id = newId
    currentMap.title = title
    currentMap.tags = []
    currentMap.category = category
    currentMap.shareLink = `${window.location.origin}/share/mindmap/${newId}`
    isEditing.value = true
    nextTick(() => { if (canvas.value && typeof canvas.value.createDefaultMindMap === 'function') canvas.value.createDefaultMindMap() })
    showToast('本地脑图创建成功（后端保存失败），请稍后保存')
  }
}

const handleOpenMindMap = (id) => {
  const item = mindMapList.value.find(m => m.id === id)
  if (item) {
    currentMap.id = item.id
    currentMap.title = item.title
    currentMap.tags = item.tags || []
    currentMap.category = item.category || ''
    currentMap.shareLink = item.shareLink || `${window.location.origin}/share/mindmap/${item.id}`
    
    isEditing.value = true
    // 打开指定脑图到画布
    nextTick(() => {
      if (canvas.value && typeof canvas.value.openMap === 'function') canvas.value.openMap(currentMap.id)
    })
    // 触发提示
    showToast('进入脑图编辑页')
  } else {
    showToast('未找到指定脑图', { type: 'warning' })
  }
}

const exitEditor = () => {
  router.push('/welcome')
}

const invokeCanvas = (method) => {
  const c = canvas.value
  if (c && typeof c[method] === 'function') c[method]()
}

// Canvas operation handlers
const handleAddChild = () => invokeCanvas('addChild')
const handleAddBro = () => invokeCanvas('addBro')
const handleEditNode = () => invokeCanvas('editNode')
const handleDelNode = () => invokeCanvas('delNode')
const handleMoveUp = () => invokeCanvas('moveUp')
const handleMoveDown = () => invokeCanvas('moveDown')
const handleToggleNode = () => invokeCanvas('toggleNode')
const handleZoomIn = () => invokeCanvas('zoomIn')
const handleZoomOut = () => invokeCanvas('zoomOut')
const handleResetZoom = () => invokeCanvas('resetZoom')
const handleUndo = () => invokeCanvas('undo')
const handleRedo = () => invokeCanvas('redo')

const onSaveMap = async () => {
  const c = canvas.value
  if (c && currentMap.id) await c.saveMap(currentMap.id)
}

const onExportMap = async () => {
  const c = canvas.value
  if (c && currentMap.id) await c.exportAsImage(currentMap.id)
}

const onShareMap = () => {
  if (!currentMap.id) {
    showToast('请先打开或创建一个脑图')
    return
  }
  showShareModal.value = true
}

const onManageTags = () => { showTagsModal.value = true }

const showVersionHistoryModal = ref(false)
const onShowVersionHistory = () => {
  if (!currentMap.id) return showToast('请先打开或创建一个脑图')
  showVersionHistoryModal.value = true
}

const onVersionRestored = (version) => {
  showToast('版本已恢复，正在刷新…')
  nextTick(() => { if (canvas.value && typeof canvas.value.openMap === 'function') canvas.value.openMap(currentMap.id) })
}

const commentPanelVisible = ref(false)
const toggleCommentPanel = () => { commentPanelVisible.value = !commentPanelVisible.value }

const handleOpenShare = (item) => {
  Object.assign(currentMap, item)
  showShareModal.value = true
}

const handleOpenTags = (item) => {
  Object.assign(currentMap, item)
  showTagsModal.value = true
}

const handleTagSave = async (newTags, newCategory) => {
  try {
    // 更新本地状态
    const target = mindMapList.value.find(item => item.id === currentMap.id)
    if (target) {
      target.tags = newTags
      target.category = newCategory
    }
    
    // 同时更新currentMap的tags和category，确保当前编辑的脑图能立即显示新标签和分类
    currentMap.tags = newTags
    currentMap.category = newCategory
    
    // 更新后端数据
    if (currentMap.id) {
      await updateMindmap(currentMap.id, { tags: newTags, category: newCategory })
    }
    showToast('标签和分类保存成功')
  } catch (err) {
    console.error('保存标签和分类失败', err)
    showToast('保存标签和分类失败，请重试')
  }
}

// 搜索与侧边栏数据
const searchKw = ref('')
const searchType = ref('all')
const currentCategory = ref('all')

const handleFilterByCategory = (category) => { currentCategory.value = category }

const filterMapList = computed(() => {
  const kw = (searchKw.value || '').trim().toLowerCase()
  let filtered = mindMapList.value
  
  // 分类过滤
  if (currentCategory.value !== 'all') {
    filtered = filtered.filter(m => m.category === currentCategory.value)
  }
  
  // 关键词搜索
  if (kw) {
    filtered = filtered.filter(m => {
      const nameMatch = (m.title||m.name||'').toLowerCase().includes(kw)
      const tagMatch = (m.tags||[]).some(t => {
        const tagValue = typeof t === 'string' ? t : (t?.name || '')
        return tagValue.toLowerCase().includes(kw)
      })
      const categoryMatch = (m.category||'').toLowerCase().includes(kw)
      switch (searchType.value) {
        case 'name':
          return nameMatch
        case 'tag':
          return tagMatch
        case 'category':
          return categoryMatch
        default:
          return nameMatch || tagMatch || categoryMatch
      }
    })
  }
  
  return filtered
})

const allTags = computed(() => {
  const set = new Map()
  mindMapList.value.forEach(m => (m.tags||[]).forEach(t => {
    const tagName = typeof t === 'string' ? t : (t.name || '')
    if (tagName) {
      set.set(tagName, { id: tagName, name: tagName, color: '#409eff' })
    }
  }))
  return Array.from(set.values())
})

const handleDelMindMap = async (id) => {
  try {
    await showConfirmDialog({ title: '确认删除', message: '删除后脑图数据将无法恢复，确定删除吗？', confirmButtonText: '删除', confirmButtonColor: '#f53f3f' })
    
    // 从本地列表中删除脑图
    const idx = mindMapList.value.findIndex(m => m.id === id)
    if (idx === -1) {
      showToast('脑图不存在或已被删除', { type: 'warning' })
      return
    }
    
    // 先从本地列表中删除，提升用户体验
    mindMapList.value.splice(idx, 1)
    
    // 调用后端API删除脑图
    try {
      await deleteMindmap(id)
      showToast('脑图删除成功')
    } catch (err) {
      console.error('删除脑图失败:', err)
      // 分析错误类型并给出相应提示
      let errorMsg = '删除成功（本地）'
      if (err.response && err.response.status === 404) {
        errorMsg = '删除成功（脑图在服务器上不存在）'
      } else if (err.response && err.response.status === 500) {
        errorMsg = '删除成功（本地），服务器端可能存在关联数据'
      }
      showToast(errorMsg)
    }
    
    // 如果删除的是当前正在编辑的脑图，尝试选择下一个可用脑图并打开；若无则创建空白画布，但不要跳回列表页面
    if (currentMap.id === id) {
      const nextItem = mindMapList.value[idx] || mindMapList.value[0]
      if (nextItem) {
        currentMap.id = nextItem.id
        currentMap.title = nextItem.title
        currentMap.tags = nextItem.tags || []
        currentMap.category = nextItem.category || ''
        nextTick(() => { 
          if (canvas.value && typeof canvas.value.openMap === 'function') {
            canvas.value.openMap(currentMap.id).catch(() => {
              // 如果打开失败，创建默认脑图
              if (canvas.value && typeof canvas.value.createDefaultMindMap === 'function') {
                canvas.value.createDefaultMindMap()
              }
            })
          }
        })
      } else {
        // 没有其他脑图，保留编辑态并展示空白画布
        currentMap.id = ''
        currentMap.title = ''
        currentMap.tags = []
        currentMap.category = ''
        nextTick(() => { 
          if (canvas.value && typeof canvas.value.createDefaultMindMap === 'function') {
            canvas.value.createDefaultMindMap()
          }
        })
      }
    }
  } catch { /* 取消删除无操作 */ }
}

// 登录
const handleLogin = () => {
  // 跳转到登录页面
  router.push('/login')
}

// 退出登录
const handleLogout = async () => {
  try {
    await userLogout()
    showToast('退出登录成功')
    // 跳转到登录页面
    router.push('/login')
  } catch (err) {
    showToast('退出登录失败')
    console.error('退出登录失败:', err)
  }
}

const handleMapShare = (shareData) => {
  console.log('脑图分享触发', shareData)
}



// 获取当前用户信息
const fetchUserInfo = async () => {
  try {
    const userInfo = await getUserInfo()
    currentUser.value = userInfo.data
  } catch (err) {
    console.error('获取用户信息失败:', err)
    // 检查是否是401错误（未登录）
    if (err.response && err.response.status === 401) {
      // 清除登录状态并跳转到登录页
      localStorage.removeItem('isLogin')
      localStorage.removeItem('isAdmin')
      router.push('/login')
    } else {
      // 非401错误，保持登录状态，使用默认用户信息
      const isLogin = localStorage.getItem('isLogin') === 'true'
      if (isLogin) {
        currentUser.value = {
          username: '用户'
        }
      }
    }
  }
}

// 初始化时加载脑图列表和用户信息
// 新的 init 函数（替换原有函数）
const init = async () => {
  try {
    await fetchUserInfo()
    const mindmaps = await request.get('/api/mindmaps')
    // 确保每个脑图对象都包含category属性
    mindMapList.value = (mindmaps.data || []).map(map => ({
      ...map,
      category: map.category || '',
      tags: map.tags || []
    }))
    // 从欢迎页面跳转过来时，默认创建一个新的脑图
    handleCreateMindMap()
  } catch (err) {
    console.error('加载脑图列表失败:', err)
  }
}

// 组件挂载时初始化
onMounted(() => {
  init()
})
</script>

<script>
export default { name: 'MindmapHome' }
</script>

<style lang="scss" scoped>
.mindmap-home-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

/* 编辑态样式 */
.mindmap-editor {
  height: calc(100vh - 48px);
  background-color: #fff;
  overflow: hidden;
}

.editor-top {
  padding: 12px;
  border-bottom: 1px solid #ebedf0;
  background-color: #fafafa;
  height: 52px;
  box-sizing: border-box;
}

.editor-layout {
  display: flex;
  gap: 12px;
  padding: 12px;
  height: calc(100vh - 100px);
  overflow: hidden;
  box-sizing: border-box;
}

.editor-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.btn-back-list {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background-color: #1989fa;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(25, 137, 250, 0.2);
}

.btn-back-list:hover {
  background-color: #3296fa;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(25, 137, 250, 0.3);
}

.btn-back-list:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(25, 137, 250, 0.2);
}

/* 列表态样式 */
.mindmap-list {
  min-height: calc(100vh - 48px);
  padding: 20px;
}

.list-wrap {
  max-width: 900px;
  margin: 0 auto;
}
</style>