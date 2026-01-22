<template>
  <div class="mindmap-editor">
    <el-card>
      <template #header>
        <div class="editor-header">
          <div class="header-left">
            <el-button link @click="$router.back()">
              <el-icon><Back /></el-icon>
              返回
            </el-button>
            <el-input
              v-model="mindmap.title"
              placeholder="请输入脑图标题"
              style="width: 300px; margin-left: 20px"
              @input="handleAutoSave"
            />
          </div>
          <div class="header-right">
            <el-button @click="addChildNode">
              <el-icon><Plus /></el-icon>
              添加子节点
            </el-button>
            <el-button @click="deleteSelectedNode">
              <el-icon><Delete /></el-icon>
              删除节点
            </el-button>
            <el-button @click="exportImage">
              <el-icon><Download /></el-icon>
              导出图片
            </el-button>
            <el-button @click="showVersions = true">
              <el-icon><Clock /></el-icon>
              版本历史
            </el-button>
            <el-button type="primary" @click="handleSave">
              <el-icon><Check /></el-icon>
              保存
            </el-button>
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
              @mousedown.stop="handleNodeMouseDown(node, $event)"
            >
              <rect
                :width="node.width"
                :height="node.height"
                :fill="selectedNode?.id === node.id ? '#409eff' : '#fff'"
                :stroke="selectedNode?.id === node.id ? '#409eff' : '#333'"
                stroke-width="2"
                rx="5"
              />
              <text
                :x="node.width / 2"
                :y="node.height / 2"
                text-anchor="middle"
                dominant-baseline="middle"
                :fill="selectedNode?.id === node.id ? '#fff' : '#333'"
                font-size="14"
              >
                {{ node.text }}
              </text>
            </g>
          </g>
        </svg>
      </div>
      
      <div class="editor-footer">
        <span class="save-status">{{ saveStatus }}</span>
        <el-switch
          v-model="mindmap.is_public"
          active-text="公开"
          inactive-text="私有"
          @change="handleAutoSave"
        />
      </div>
    </el-card>
    
    <el-drawer v-model="showVersions" title="版本历史" size="40%">
      <el-timeline>
        <el-timeline-item
          v-for="version in versions"
          :key="version.id"
          :timestamp="version.updated_at"
          placement="top"
        >
          <div class="version-item">
            <div class="version-content">节点数: {{ version.data?.nodes?.length || 0 }}</div>
            <div class="version-actions">
              <el-button link type="warning" @click="rollbackVersion(version)">
                回滚
              </el-button>
            </div>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { mindmapAPI } from '@/api/editor'
import { ElMessage } from 'element-plus'

const props = defineProps({
  isNew: {
    type: Boolean,
    default: false
  }
})

const route = useRoute()
const mindmapId = route.params.id

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
const versions = ref([])
const showVersions = ref(false)

const svgRef = ref(null)
const zoomGroupRef = ref(null)

const saveStatus = ref('未保存')

let nodeIdCounter = 2
let isDragging = false
let dragNode = null
let dragOffset = { x: 0, y: 0 }

async function loadMindmap() {
  if (props.isNew) return
  
  try {
    const data = await mindmapAPI.get(mindmapId)
    mindmap.value = data.mindmap
    
    if (data.mindmap.data && data.mindmap.data.nodes) {
      nodes.value = data.mindmap.data.nodes
      edges.value = data.mindmap.data.edges || []
      nodeIdCounter = Math.max(...nodes.value.map(n => n.id)) + 1
    }
    
    await loadVersions()
  } catch (error) {
    console.error('Load mindmap error:', error)
  }
}

async function loadVersions() {
  if (!mindmap.value.id) return
  
  try {
    const data = await mindmapAPI.getVersions(mindmap.value.id)
    versions.value = data.versions
  } catch (error) {
    console.error('Load versions error:', error)
  }
}

function handleAutoSave() {
  saveStatus.value = '正在保存...'
  
  setTimeout(() => {
    handleSave(true)
  }, 2000)
}

async function handleSave(silent = false) {
  try {
    const data = {
      title: mindmap.value.title || '新脑图',
      data: {
        nodes: nodes.value,
        edges: edges.value
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
    
    await loadVersions()
    
    saveStatus.value = '已保存'
    if (!silent) ElMessage.success('保存成功')
  } catch (error) {
    console.error('Save mindmap error:', error)
    saveStatus.value = '保存失败'
    if (!silent) ElMessage.error('保存失败')
  }
}

async function rollbackVersion(version) {
  try {
    await mindmapAPI.rollbackVersion(mindmap.value.id, version.id)
    mindmap.value.data = version.data
    nodes.value = version.data.nodes || []
    edges.value = version.data.edges || []
    await loadVersions()
    ElMessage.success('回滚成功')
  } catch (error) {
    console.error('Rollback version error:', error)
    ElMessage.error('回滚失败')
  }
}

function getNodePosition(nodeId) {
  const node = nodes.value.find(n => n.id === nodeId)
  return node ? { x: node.x + node.width / 2, y: node.y + node.height / 2 } : { x: 0, y: 0 }
}

function addChildNode() {
  if (!selectedNode.value) {
    ElMessage.warning('请先选择一个节点')
    return
  }
  
  const parent = selectedNode.value
  const newNode = {
    id: nodeIdCounter++,
    text: '新节点',
    x: parent.x + 150,
    y: parent.y,
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
  
  if (selectedNode.value.parentId === null) {
    ElMessage.warning('不能删除中心节点')
    return
  }
  
  const nodeId = selectedNode.value.id
  
  nodes.value = nodes.value.filter(n => n.id !== nodeId)
  edges.value = edges.value.filter(e => e.from !== nodeId && e.to !== nodeId)
  
  selectedNode.value = null
  handleAutoSave()
}

function handleNodeMouseDown(node, event) {
  selectedNode.value = node
  isDragging = true
  dragNode = node
  dragOffset = {
    x: event.clientX - node.x,
    y: event.clientY - node.y
  }
}

function handleSvgMouseDown(event) {
  if (event.target.tagName === 'svg') {
    selectedNode.value = null
  }
}

function handleMouseMove(event) {
  if (!isDragging || !dragNode) return
  
  const svgRect = svgRef.value.getBoundingClientRect()
  dragNode.x = event.clientX - svgRect.left - dragOffset.x
  dragNode.y = event.clientY - svgRect.top - dragOffset.y
}

function handleMouseUp() {
  if (isDragging) {
    isDragging = false
    dragNode = null
    handleAutoSave()
  }
}

function exportImage() {
  const svgData = new XMLSerializer().serializeToString(svgRef.value)
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  const img = new Image()
  
  canvas.width = svgRef.value.clientWidth
  canvas.height = svgRef.value.clientHeight
  
  img.onload = () => {
    ctx.fillStyle = '#fff'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.drawImage(img, 0, 0)
    
    const link = document.createElement('a')
    link.download = `${mindmap.value.title || '脑图'}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
    ElMessage.success('导出成功')
  }
  
  img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)))
}

onMounted(() => {
  loadMindmap()
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
})

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

.mindmap-container {
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  overflow: hidden;
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
