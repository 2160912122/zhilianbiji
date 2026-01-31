<template>
  <div class="mindmap-editor">
    <el-card class="mindmap-editor">
      <template #header>
        <div class="editor-header">
          <div class="header-left">
            <el-input
              v-model="mindmap.title"
              placeholder="请输入脑图标题"
              style="width: 300px; margin-left: 20px"
              @input="handleAutoSave"
            />
          </div>
          <div class="header-right">
            <!-- 操作按钮组 -->
            <div class="operation-buttons">
              <el-tooltip v-if="!isShared || sharePermission === 'edit'" content="添加子节点" placement="top">
                <el-button @click="addChildNode">
                  <el-icon><Plus /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip v-if="!isShared || sharePermission === 'edit'" content="删除节点" placement="top">
                <el-button @click="deleteSelectedNode">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip v-if="!isShared || sharePermission === 'edit'" content="节点上移" placement="top">
                <el-button @click="moveNodeUp">
                  <el-icon><Top /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip v-if="!isShared || sharePermission === 'edit'" content="节点下移" placement="top">
                <el-button @click="moveNodeDown">
                  <el-icon><Bottom /></el-icon>
                </el-button>
              </el-tooltip>
              <el-divider direction="vertical" />
              <el-tooltip v-if="!isShared || sharePermission === 'edit'" content="撤销" placement="top">
                <el-button @click="undo">
                  <el-icon><RefreshLeft /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip v-if="!isShared || sharePermission === 'edit'" content="重做" placement="top">
                <el-button @click="redo">
                  <el-icon><RefreshRight /></el-icon>
                </el-button>
              </el-tooltip>
              <el-divider direction="vertical" />
              <el-tooltip content="放大" placement="top">
                <el-button @click="zoomIn">
                  <el-icon><ZoomIn /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="缩小" placement="top">
                <el-button @click="zoomOut">
                  <el-icon><ZoomOut /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="重置缩放" placement="top">
                <el-button @click="resetZoom">
                  <el-icon><Refresh /></el-icon>
                </el-button>
              </el-tooltip>
              <el-divider direction="vertical" />
              <el-tooltip v-if="!isShared" content="分享" placement="top">
                <el-button @click="showShareDialog">
                  <el-icon><Share /></el-icon>
                </el-button>
              </el-tooltip>
              <el-divider direction="vertical" />
              <el-tooltip v-if="!isShared || sharePermission === 'edit'" content="保存" placement="top">
                <el-button type="primary" @click="handleSave">
                  <el-icon><Check /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
          </div>
        </div>
      </template>
      
      <div class="mindmap-container">
        
        <svg
          ref="svgRef"
          class="mindmap-svg"
          @mousedown="handleSvgMouseDown"
        >
          <g ref="zoomGroupRef">
            <line
              v-for="edge in edges"
              :key="`${edge.from}-${edge.to}`"
              :x1="getNodePosition(edge.from).x"
              :y1="getNodePosition(edge.from).y"
              :x2="getNodePosition(edge.to).x"
              :y2="getNodePosition(edge.to).y"
              stroke="#999"
              stroke-width="2"
            />
            <g
              v-for="node in nodes"
              :key="node.id"
              :transform="`translate(${node.x}, ${node.y})`"
              class="node-group"
              @mousedown.stop="!isShared || sharePermission === 'edit' ? handleNodeMouseDown(node, $event) : null"
              @dblclick="!isShared || sharePermission === 'edit' ? startNodeEdit(node) : null"
            >
              <rect
                :width="node.width"
                :height="node.height"
                :fill="selectedNode?.id === node.id ? '#409eff' : (node.bgColor || '#fff')"
                :stroke="selectedNode?.id === node.id ? '#409eff' : '#333'"
                stroke-width="2"
                rx="5"
              />
              <text
                :x="node.width / 2"
                :y="node.height / 2"
                text-anchor="middle"
                dominant-baseline="middle"
                :fill="selectedNode?.id === node.id ? '#fff' : (node.fontColor || '#333')"
                :font-size="node.fontSize || 14"
              >
                {{ node.text }}
              </text>
            </g>
          </g>
        </svg>
        
        <!-- 节点编辑面板 -->
        <div v-if="selectedNode && (!isShared || sharePermission === 'edit')" class="node-edit-panel">
          <h4>编辑节点</h4>
          <el-input
            v-model="editText"
            placeholder="输入节点文本"
            type="textarea"
            :rows="3"
            style="margin-bottom: 10px;"
          />
          <div class="edit-buttons">
            <el-button type="primary" @click="saveNodeEdit">保存</el-button>
            <el-button @click="cancelNodeEdit">取消</el-button>
          </div>
          
          <!-- 文字样式编辑 -->
          <h4 style="margin-top: 20px;">文字样式</h4>
          <el-form :model="nodeStyle" label-width="80px">
            <el-form-item label="字体大小">
              <el-input-number v-model="nodeStyle.fontSize" :min="12" :max="36" :step="1" style="width: 100%;" />
            </el-form-item>
            <el-form-item label="字体颜色">
              <el-color-picker v-model="nodeStyle.fontColor" show-alpha />
            </el-form-item>
            <el-form-item label="背景颜色">
              <el-color-picker v-model="nodeStyle.bgColor" show-alpha />
            </el-form-item>
          </el-form>
          <div class="style-buttons">
            <el-button type="primary" @click="saveNodeStyle">应用样式</el-button>
          </div>
        </div>
      </div>
      
      <div v-if="!isShared" class="editor-footer">
        <span class="save-status">{{ saveStatus }}</span>
        <el-switch
          v-model="mindmap.is_public"
          active-text="公开"
          inactive-text="私有"
          @change="handleAutoSave"
        />
      </div>
    </el-card>
    
    <!-- 分享对话框 -->
    <el-dialog
      v-model="shareDialogVisible"
      title="分享脑图"
      width="600px"
    >
      <div>
        <h4>创建新分享链接</h4>
        <el-form :model="shareForm" label-width="100px" style="margin-bottom: 20px;">
          <el-form-item label="权限">
            <el-select v-model="shareForm.permission" placeholder="请选择权限" style="width: 200px;">
              <el-option label="只读" value="view" />
              <el-option label="可编辑" value="edit" />
            </el-select>
          </el-form-item>
          <el-form-item label="过期时间">
            <el-date-picker
              v-model="shareForm.expire_at"
              type="datetime"
              placeholder="选择过期时间"
              style="width: 200px;"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DD HH:mm:ss"
            />
          </el-form-item>
        </el-form>
        <el-button type="primary" @click="createShareLink">创建分享链接</el-button>
        
        <h4 style="margin-top: 30px;">已创建的分享链接</h4>
        <el-table :data="shareLinks" style="width: 100%;">
          <el-table-column prop="share_url" label="分享链接" min-width="250">
            <template #default="scope">
              <div style="display: flex; align-items: center; gap: 8px;">
                <a :href="getFullShareUrl(scope.row.share_url)" target="_blank" style="flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ getFullShareUrl(scope.row.share_url) }}</a>
                <el-button size="small" @click="copyShareLink(scope.row.share_url)">
                  <el-icon><DocumentCopy /></el-icon>
                </el-button>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="permission" label="权限" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.permission === 'view' ? 'info' : 'success'">
                {{ scope.row.permission === 'view' ? '只读' : '可编辑' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="expire_at" label="过期时间" width="180">
            <template #default="scope">
              {{ scope.row.expire_at || '永不过期' }}
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180" />
          <el-table-column label="操作" width="100">
            <template #default="scope">
              <el-button type="danger" size="small" @click="deleteShareLink(scope.row.token)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { mindmapAPI } from '@/api/editor'
import { ElMessage, ElDialog, ElForm, ElFormItem, ElSelect, ElOption, ElDatePicker, ElButton, ElTable, ElTableColumn, ElTag, ElIcon } from 'element-plus'
import { Share, Delete, Check, DocumentCopy } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'

const props = defineProps({
  isNew: {
    type: Boolean,
    default: false
  },
  mindmapId: {
    type: Number,
    default: null
  },
  isShared: {
    type: Boolean,
    default: false
  },
  sharePermission: {
    type: String,
    default: 'view'
  },
  sharedMindmap: {
    type: Object,
    default: null
  }
})

const route = useRoute()
const router = useRouter()
const mindmapId = props.mindmapId || route.params.id
const userStore = useUserStore()

const mindmap = ref({
  id: null,
  title: '',
  data: {},
  is_public: false
})

const nodes = ref([
  { id: 1, text: '中心主题', x: 400, y: 300, width: 120, height: 40, parentId: null }
])

const edges = ref([])
const selectedNode = ref(null)
const editText = ref('')
const nodeStyle = ref({
  fontSize: 14,
  fontColor: '#333',
  bgColor: '#fff'
})

const svgRef = ref(null)
const zoomGroupRef = ref(null)

const saveStatus = ref('未保存')

// 缩放功能
const zoomLevel = ref(1)

// 撤销重做功能
const history = ref([])
const historyIndex = ref(-1)
const MAX_HISTORY = 50

// 分享功能
const shareDialogVisible = ref(false)
const shareForm = ref({
  permission: 'view',
  expire_at: ''
})
const shareLinks = ref([])

let nodeIdCounter = 2
let isDragging = false
let dragNode = null
let dragOffset = { x: 0, y: 0 }

// 记录历史状态
function saveHistory() {
  // 移除当前索引之后的历史记录
  if (historyIndex.value < history.value.length - 1) {
    history.value = history.value.slice(0, historyIndex.value + 1)
  }
  
  // 保存当前状态
  const currentState = {
    nodes: JSON.parse(JSON.stringify(nodes.value)),
    edges: JSON.parse(JSON.stringify(edges.value))
  }
  
  history.value.push(currentState)
  
  // 限制历史记录数量
  if (history.value.length > MAX_HISTORY) {
    history.value.shift()
  } else {
    historyIndex.value++
  }
}

// 撤销
function undo() {
  if (historyIndex.value > 0) {
    historyIndex.value--
    const prevState = history.value[historyIndex.value]
    nodes.value = JSON.parse(JSON.stringify(prevState.nodes))
    edges.value = JSON.parse(JSON.stringify(prevState.edges))
    handleAutoSave()
  }
}

// 重做
function redo() {
  if (historyIndex.value < history.value.length - 1) {
    historyIndex.value++
    const nextState = history.value[historyIndex.value]
    nodes.value = JSON.parse(JSON.stringify(nextState.nodes))
    edges.value = JSON.parse(JSON.stringify(nextState.edges))
    handleAutoSave()
  }
}

// 节点上移
function moveNodeUp() {
  if (!selectedNode.value) {
    ElMessage.warning('请先选择一个节点')
    return
  }
  
  const node = selectedNode.value
  node.y -= 50
  handleAutoSave()
}

// 节点下移
function moveNodeDown() {
  if (!selectedNode.value) {
    ElMessage.warning('请先选择一个节点')
    return
  }
  
  const node = selectedNode.value
  node.y += 50
  handleAutoSave()
}

// 放大
function zoomIn() {
  if (zoomLevel.value < 2) {
    zoomLevel.value += 0.1
    updateZoom()
  }
}

// 缩小
function zoomOut() {
  if (zoomLevel.value > 0.5) {
    zoomLevel.value -= 0.1
    updateZoom()
  }
}

// 重置缩放
function resetZoom() {
  zoomLevel.value = 1
  updateZoom()
}

// 更新缩放
function updateZoom() {
  if (zoomGroupRef.value) {
    zoomGroupRef.value.setAttribute('transform', `scale(${zoomLevel.value})`)
  }
}

async function loadMindmap() {
  if (props.isNew) return
  
  try {
    let data
    if (props.isShared && props.sharedMindmap) {
      data = { mindmap: props.sharedMindmap }
    } else if (props.isShared) {
      data = await mindmapAPI.getShared(mindmapId)
    } else {
      data = await mindmapAPI.get(mindmapId)
    }
    
    mindmap.value = data.mindmap
    
    if (data.mindmap.data && data.mindmap.data.nodes) {
      nodes.value = data.mindmap.data.nodes
      edges.value = data.mindmap.data.edges || []
      nodeIdCounter = Math.max(...nodes.value.map(n => n.id)) + 1
    }
  } catch (error) {
    console.error('Load mindmap error:', error)
  }
}

function handleAutoSave() {
  // 保存历史状态
  saveHistory()
  
  saveStatus.value = '正在保存...'
  
  setTimeout(() => {
    handleSave(true)
  }, 2000)
}

async function handleSave(silent = false) {
  try {
    // 检查用户是否已经登录
    const token = localStorage.getItem('token')
    if (!token) {
      saveStatus.value = '保存失败'
      if (!silent) ElMessage.error('请先登录')
      router.push('/login')
      return
    }
    
    const data = {
      title: mindmap.value.title || '新脑图',
      data: {
        nodes: JSON.parse(JSON.stringify(nodes.value)),
        edges: JSON.parse(JSON.stringify(edges.value))
      },
      is_public: mindmap.value.is_public
    }
    
    if (mindmap.value.id) {
      await mindmapAPI.update(mindmap.value.id, data)
    } else {
      const result = await mindmapAPI.create(data)
      mindmap.value.id = result.mindmap.id
      mindmap.value.title = result.mindmap.title
    }
    
    saveStatus.value = '已保存'
    if (!silent) ElMessage.success('保存成功')
  } catch (error) {
    console.error('Save mindmap error:', error)
    saveStatus.value = '保存失败'
    if (error.response && error.response.status === 401) {
      // 登录已过期，跳转到登录页面
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (!silent) ElMessage.error('登录已过期，请重新登录')
      router.push('/login')
    } else {
      if (!silent) ElMessage.error('保存失败')
    }
  }
}

function getNodePosition(nodeId) {
  const node = nodes.value.find(n => n.id === nodeId)
  return node ? { x: node.x + node.width / 2, y: node.y + node.height / 2 } : { x: 0, y: 0 }
}

function addChildNode() {
  // 如果没有选择节点，使用中心节点作为父节点
  let parent = selectedNode.value
  if (!parent) {
    // 查找中心节点
    parent = nodes.value.find(node => node.parentId === null)
    if (!parent) {
      // 如果没有中心节点，创建一个
      parent = {
        id: nodeIdCounter++,
        text: '中心主题',
        x: 400,
        y: 100,
        width: 120,
        height: 40,
        parentId: null
      }
      nodes.value.push(parent)
    }
  }
  
  // 查找父节点已有的子节点
  const siblings = nodes.value.filter(node => node.parentId === parent.id)
  
  // 计算新节点的位置：在父节点右侧，垂直分布
  const siblingCount = siblings.length
  const verticalSpacing = 60
  const horizontalOffset = 180
  
  // 计算新节点的Y坐标，使其在已有子节点下方
  let newY = parent.y - (siblingCount * verticalSpacing / 2)
  if (siblingCount > 0) {
    // 如果已有子节点，新节点放在最下面
    const lastSibling = siblings[siblings.length - 1]
    newY = lastSibling.y + verticalSpacing
  }
  
  const newNode = {
    id: nodeIdCounter++,
    text: '新节点',
    x: parent.x + horizontalOffset,
    y: newY,
    width: 100,
    height: 40,
    parentId: parent.id
  }
  
  nodes.value.push(newNode)
  edges.value.push({ from: parent.id, to: newNode.id })
  handleAutoSave()
}

function deleteSelectedNode() {
  if (!selectedNode.value) {
    ElMessage.warning('请先选择一个节点')
    return
  }
  
  const nodeId = selectedNode.value.id
  
  // 递归获取所有子节点ID
  function getAllChildNodeIds(parentId) {
    const childIds = []
    const children = nodes.value.filter(n => n.parentId === parentId)
    
    children.forEach(child => {
      childIds.push(child.id)
      childIds.push(...getAllChildNodeIds(child.id))
    })
    
    return childIds
  }
  
  const allNodeIdsToDelete = [nodeId, ...getAllChildNodeIds(nodeId)]
  
  nodes.value = nodes.value.filter(n => !allNodeIdsToDelete.includes(n.id))
  edges.value = edges.value.filter(e => !allNodeIdsToDelete.includes(e.from) && !allNodeIdsToDelete.includes(e.to))
  
  selectedNode.value = null
  handleAutoSave()
}

function handleNodeMouseDown(node, event) {
  selectedNode.value = node
  isDragging = true
  dragNode = node
  const svgRect = svgRef.value.getBoundingClientRect()
  dragOffset = {
    x: event.clientX - svgRect.left - (node.x * zoomLevel.value),
    y: event.clientY - svgRect.top - (node.y * zoomLevel.value)
  }
}

function startNodeEdit(node) {
  selectedNode.value = node
  editText.value = node.text
}

function saveNodeEdit() {
  if (selectedNode.value) {
    selectedNode.value.text = editText.value
    // 根据文本长度调整节点宽度
    const textLength = editText.value.length
    selectedNode.value.width = Math.max(100, textLength * 10)
    handleAutoSave()
  }
}

function saveNodeStyle() {
  if (selectedNode.value) {
    selectedNode.value.fontSize = nodeStyle.value.fontSize
    selectedNode.value.fontColor = nodeStyle.value.fontColor
    selectedNode.value.bgColor = nodeStyle.value.bgColor
    handleAutoSave()
  }
}

function cancelNodeEdit() {
  if (selectedNode.value) {
    editText.value = selectedNode.value.text
    updateNodeStyleFromSelection()
  }
}

function updateNodeStyleFromSelection() {
  if (selectedNode.value) {
    nodeStyle.value.fontSize = selectedNode.value.fontSize || 14
    nodeStyle.value.fontColor = selectedNode.value.fontColor || '#333'
    nodeStyle.value.bgColor = selectedNode.value.bgColor || '#fff'
  }
}

// 监听选中节点变化，更新编辑框内容
watch(selectedNode, (newNode) => {
  if (newNode) {
    editText.value = newNode.text
    updateNodeStyleFromSelection()
  }
}, { immediate: true })

function handleSvgMouseDown(event) {
  if (event.target.tagName === 'svg') {
    selectedNode.value = null
  }
}

function handleMouseMove(event) {
  if (!isDragging || !dragNode) return
  
  const svgRect = svgRef.value.getBoundingClientRect()
  // 考虑缩放的影响
  dragNode.x = (event.clientX - svgRect.left - dragOffset.x) / zoomLevel.value
  dragNode.y = (event.clientY - svgRect.top - dragOffset.y) / zoomLevel.value
}

function handleMouseUp() {
  if (isDragging) {
    isDragging = false
    dragNode = null
    handleAutoSave()
  }
}

onMounted(() => {
  // 初始化用户状态
  userStore.initFromStorage()
  
  loadMindmap()
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
})

// 分享功能相关方法
async function showShareDialog() {
  if (!mindmap.value.id) {
    ElMessage.error('请先保存脑图')
    return
  }
  
  shareDialogVisible.value = true
  await loadShareLinks()
}

async function createShareLink() {
  if (!mindmap.value.id) {
    ElMessage.error('请先保存脑图')
    return
  }
  
  try {
    const response = await mindmapAPI.share(mindmap.value.id, {
      permission: shareForm.value.permission,
      expire_at: shareForm.value.expire_at
    })
    
    ElMessage.success('分享链接创建成功')
    await loadShareLinks()
    
    // 重置表单
    shareForm.value = {
      permission: 'view',
      expire_at: ''
    }
  } catch (error) {
    console.error('创建分享链接失败:', error)
    ElMessage.error('创建分享链接失败')
  }
}

async function loadShareLinks() {
  if (!mindmap.value.id) return
  
  try {
    const response = await mindmapAPI.getShares(mindmap.value.id)
    shareLinks.value = response
  } catch (error) {
    console.error('加载分享链接失败:', error)
    ElMessage.error('加载分享链接失败')
  }
}

async function deleteShareLink(token) {
  try {
    await mindmapAPI.deleteShare(token)
    ElMessage.success('分享链接已删除')
    await loadShareLinks()
  } catch (error) {
    console.error('删除分享链接失败:', error)
    ElMessage.error('删除分享链接失败')
  }
}

function getFullShareUrl(shareUrl) {
  const baseUrl = window.location.origin
  return baseUrl + shareUrl
}

async function copyShareLink(shareUrl) {
  const fullUrl = getFullShareUrl(shareUrl)
  try {
    await navigator.clipboard.writeText(fullUrl)
    ElMessage.success('分享链接已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败，请手动复制')
  }
}

onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
})
</script>

<style scoped>
.mindmap-editor {
  padding: 20px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.operation-buttons {
  display: flex;
  align-items: center;
  gap: 0;
}

.operation-buttons .el-button {
  margin-right: 0;
  border-radius: 0;
}

.operation-buttons .el-button:first-child {
  border-top-left-radius: 4px;
  border-bottom-left-radius: 4px;
}

.operation-buttons .el-button:last-child {
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
}

.operation-buttons .el-divider {
  margin: 0 5px;
}

.mindmap-container {
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.mindmap-svg {
  display: block;
  width: 100%;
  height: 600px;
  background: #f9f9f9;
}

.node-group {
  cursor: move;
}

.node-group:hover rect {
  stroke: #409eff;
  stroke-width: 3;
}

/* 节点编辑面板样式 */
.node-edit-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 250px;
  padding: 15px;
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.node-edit-panel h4 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.edit-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.style-buttons {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

.editor-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #e6e6e6;
}

.save-status {
  font-size: 12px;
  color: #999;
}
</style>
