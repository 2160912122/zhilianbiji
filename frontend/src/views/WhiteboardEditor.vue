<template>
  <div class="whiteboard-editor">
    <el-card>
      <template #header>
        <div class="editor-header">
          <div class="header-left">
            <el-button link @click="$router.back()">
              <el-icon><Back /></el-icon>
              返回
            </el-button>
            <el-input
              v-model="whiteboard.title"
              placeholder="请输入白板标题"
              style="width: 300px; margin-left: 20px"
              @input="handleAutoSave"
            />
          </div>
          <div class="header-right">
            <el-button @click="clearCanvas">
              <el-icon><Delete /></el-icon>
              清空
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
      
      <div class="whiteboard-container">
        <div class="toolbar">
          <el-button-group>
            <el-button
              :type="currentTool === 'select' ? 'primary' : ''"
              @click="setTool('select')"
            >
              <el-icon><Pointer /></el-icon>
              选择
            </el-button>
            <el-button
              :type="currentTool === 'pen' ? 'primary' : ''"
              @click="setTool('pen')"
            >
              <el-icon><EditPen /></el-icon>
              画笔
            </el-button>
            <el-button
              :type="currentTool === 'eraser' ? 'primary' : ''"
              @click="setTool('eraser')"
            >
              <el-icon><Delete /></el-icon>
              橡皮擦
            </el-button>
          </el-button-group>
          
          <el-color-picker v-model="strokeColor" @change="handleColorChange" />
          
          <el-slider
            v-model="strokeWidth"
            :min="1"
            :max="50"
            style="width: 150px; margin-left: 20px"
            @change="handleWidthChange"
          />
        </div>
        
        <canvas
          ref="canvasRef"
          class="whiteboard-canvas"
          @mousedown="handleMouseDown"
          @mousemove="handleMouseMove"
          @mouseup="handleMouseUp"
          @mouseleave="handleMouseUp"
        />
      </div>
      
      <div class="editor-footer">
        <span class="save-status">{{ saveStatus }}</span>
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
            <div class="version-content">笔画数: {{ Object.keys(version.data || {}).length || 0 }}</div>
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
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { whiteboardAPI } from '@/api/editor'
import { ElMessage } from 'element-plus'

const props = defineProps({
  isNew: {
    type: Boolean,
    default: false
  }
})

const route = useRoute()
const whiteboardId = route.params.id

const whiteboard = ref({
  id: null,
  title: '',
  room_key: '',
  data: {}
})

const versions = ref([])
const showVersions = ref(false)

const canvasRef = ref(null)
const ctx = ref(null)
const currentTool = ref('select')
const strokeColor = ref('#000000')
const strokeWidth = ref(3)
const isDrawing = ref(false)
const lastX = ref(0)
const lastY = ref(0)

const saveStatus = ref('未保存')
let autoSaveTimer = null

async function loadWhiteboard() {
  if (props.isNew) return
  
  try {
    const data = await whiteboardAPI.get(whiteboardId)
    whiteboard.value = data.whiteboard
    
    if (data.whiteboard.data) {
      loadCanvasData(data.whiteboard.data)
    }
    
    await loadVersions()
  } catch (error) {
    console.error('Load whiteboard error:', error)
  }
}

async function loadVersions() {
  if (!whiteboard.value.id) return
  
  try {
    const data = await whiteboardAPI.getVersions(whiteboard.value.id)
    versions.value = data.versions
  } catch (error) {
    console.error('Load versions error:', error)
  }
}

function initCanvas() {
  const canvas = canvasRef.value
  if (!canvas) return
  
  const container = canvas.parentElement
  canvas.width = container.clientWidth
  canvas.height = 600
  
  ctx.value = canvas.getContext('2d')
  ctx.value.lineCap = 'round'
  ctx.value.lineJoin = 'round'
  ctx.value.strokeStyle = strokeColor.value
  ctx.value.lineWidth = strokeWidth.value
}

function loadCanvasData(data) {
  if (!ctx.value) return
  
  const img = new Image()
  img.onload = () => {
    ctx.value.drawImage(img, 0, 0)
  }
  img.src = data.imageData
}

function saveCanvasData() {
  if (!canvasRef.value) return null
  
  return {
    imageData: canvasRef.value.toDataURL('image/png'),
    tool: currentTool.value,
    strokeColor: strokeColor.value,
    strokeWidth: strokeWidth.value
  }
}

function handleAutoSave() {
  saveStatus.value = '正在保存...'
  
  if (autoSaveTimer) clearTimeout(autoSaveTimer)
  autoSaveTimer = setTimeout(() => {
    handleSave(true)
  }, 2000)
}

async function handleSave(silent = false) {
  if (autoSaveTimer) clearTimeout(autoSaveTimer)
  
  try {
    const data = {
      title: whiteboard.value.title || '新白板',
      data: saveCanvasData()
    }
    
    if (whiteboard.value.id) {
      await whiteboardAPI.update(whiteboard.value.id, data)
    } else {
      const result = await whiteboardAPI.create(data)
      whiteboard.value.id = result.whiteboard.id
      whiteboard.value.room_key = result.whiteboard.room_key
      whiteboard.value.title = result.whiteboard.title
    }
    
    await loadVersions()
    
    saveStatus.value = '已保存'
    if (!silent) ElMessage.success('保存成功')
  } catch (error) {
    console.error('Save whiteboard error:', error)
    saveStatus.value = '保存失败'
    if (!silent) ElMessage.error('保存失败')
  }
}

async function rollbackVersion(version) {
  try {
    await whiteboardAPI.rollbackVersion(whiteboard.value.id, version.id)
    whiteboard.value.data = version.data
    loadCanvasData(version.data)
    await loadVersions()
    ElMessage.success('回滚成功')
  } catch (error) {
    console.error('Rollback version error:', error)
    ElMessage.error('回滚失败')
  }
}

function setTool(tool) {
  currentTool.value = tool
}

function handleColorChange() {
  if (ctx.value) {
    ctx.value.strokeStyle = strokeColor.value
  }
}

function handleWidthChange() {
  if (ctx.value) {
    ctx.value.lineWidth = strokeWidth.value
  }
}

function handleMouseDown(e) {
  if (currentTool.value === 'select') return
  
  isDrawing.value = true
  const rect = canvasRef.value.getBoundingClientRect()
  lastX.value = e.clientX - rect.left
  lastY.value = e.clientY - rect.top
}

function handleMouseMove(e) {
  if (!isDrawing.value || currentTool.value === 'select') return
  
  const rect = canvasRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  
  ctx.value.beginPath()
  ctx.value.moveTo(lastX.value, lastY.value)
  ctx.value.lineTo(x, y)
  
  if (currentTool.value === 'eraser') {
    ctx.value.globalCompositeOperation = 'destination-out'
    ctx.value.lineWidth = strokeWidth.value * 3
  } else {
    ctx.value.globalCompositeOperation = 'source-over'
    ctx.value.strokeStyle = strokeColor.value
    ctx.value.lineWidth = strokeWidth.value
  }
  
  ctx.value.stroke()
  
  lastX.value = x
  lastY.value = y
}

function handleMouseUp() {
  if (isDrawing.value) {
    isDrawing.value = false
    handleAutoSave()
  }
}

function clearCanvas() {
  if (!canvasRef.value || !ctx.value) return
  
  ctx.value.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
  handleAutoSave()
}

function exportImage() {
  if (!canvasRef.value) return
  
  const link = document.createElement('a')
  link.download = `${whiteboard.value.title || '白板'}.png`
  link.href = canvasRef.value.toDataURL('image/png')
  link.click()
  ElMessage.success('导出成功')
}

onMounted(() => {
  loadWhiteboard()
  initCanvas()
})

onUnmounted(() => {
  if (autoSaveTimer) clearTimeout(autoSaveTimer)
})
</script>

<style scoped>
.whiteboard-editor {
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

.whiteboard-container {
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  overflow: hidden;
}

.toolbar {
  display: flex;
  align-items: center;
  padding: 10px;
  background: #f5f5f5;
  border-bottom: 1px solid #e6e6e6;
  gap: 10px;
}

.whiteboard-canvas {
  display: block;
  cursor: crosshair;
  background: #fff;
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
