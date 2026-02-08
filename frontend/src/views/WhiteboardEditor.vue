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
            <AIModuleButton />
            <el-button link @click="showVersions = true">
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
        <iframe
          ref="wboIframe"
          class="wbo-iframe"
          :src="wboUrl"
          frameborder="0"
          allowfullscreen
        ></iframe>
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
            <div class="version-content">版本: {{ version.id }}</div>
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
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { whiteboardAPI } from '@/api/editor'
import { ElMessage, ElMessageBox } from 'element-plus'
import AIModuleButton from '@/components/AIModuleButton.vue'
import { useAIStore } from '@/store/ai'

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
const wboIframe = ref(null)

// WBO JWT令牌
const wboToken = ref('')

const saveStatus = ref('未保存')
let autoSaveTimer = null

// 初始化AI store
const aiStore = useAIStore()

// 监听AI生成的内容
watch(() => aiStore.hasNewContent, (hasNewContent) => {
  if (hasNewContent) {
    try {
      // AI生成的白板内容可能是文本描述或JSON数据
      const aiContent = aiStore.generatedContent
      
      // 更新白板标题（如果没有标题）
      if (!whiteboard.value.title) {
        whiteboard.value.title = 'AI生成的白板'
      }
      
      // 显示AI生成的内容作为提示
      ElMessageBox.alert(
        `<div style="max-height: 300px; overflow-y: auto;">
          <h4>AI生成的白板内容</h4>
          <pre style="white-space: pre-wrap; word-break: break-all;">${aiContent}</pre>
          <p style="margin-top: 10px; color: #666;">请在白板中手动创建相关内容</p>
        </div>`,
        'AI内容提示',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '确定',
          type: 'success'
        }
      )
      
      // 尝试自动绘制简单图形（示例：画一个苹果）
      setTimeout(() => {
        drawApple()
      }, 1000)
      
      ElMessage.success('AI生成的白板内容已准备就绪')
    } catch (error) {
      console.error('处理AI白板内容失败:', error)
      ElMessage.error('处理AI生成的白板内容失败')
    }
    // 重置AI store状态
    aiStore.resetGeneratedContent()
  }
})

// 向WBO iframe发送绘制命令
function sendToWBO(command) {
  const iframe = wboIframe.value
  if (iframe && iframe.contentWindow) {
    iframe.contentWindow.postMessage(command, '*')
  }
}

// 绘制一个苹果（示例）
function drawApple() {
  // 苹果主体（圆形）
  sendToWBO({
    type: 'draw',
    tool: 'Pencil',
    action: 'circle',
    data: {
      x: 300,
      y: 300,
      radius: 100,
      color: '#FF4136',
      size: 5
    }
  })
  
  // 苹果梗（线条）
  setTimeout(() => {
    sendToWBO({
      type: 'draw',
      tool: 'Pencil',
      action: 'line',
      data: {
        points: [
          { x: 300, y: 200 },
          { x: 280, y: 180 },
          { x: 290, y: 160 }
        ],
        color: '#3D9970',
        size: 8
      }
    })
  }, 500)
  
  // 苹果叶子（线条）
  setTimeout(() => {
    sendToWBO({
      type: 'draw',
      tool: 'Pencil',
      action: 'line',
      data: {
        points: [
          { x: 280, y: 180 },
          { x: 260, y: 170 },
          { x: 270, y: 190 },
          { x: 280, y: 180 }
        ],
        color: '#3D9970',
        size: 5
      }
    })
  }, 1000)
}

// 计算WBO URL
const wboUrl = computed(() => {
  // 确保roomKey有效，避免生成无效URL
  const roomKey = whiteboard.value.room_key || 'new-whiteboard-' + Date.now()
  let url = `http://localhost:8080/boards/${roomKey}`
  if (wboToken.value) {
    url += `?token=${wboToken.value}`
  }
  return url
})

// 获取WBO JWT令牌
async function getWboToken() {
  try {
    const response = await fetch('/api/whiteboards/wbo-token', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      wboToken.value = data.token
    }
  } catch (error) {
    console.error('Failed to get WBO token:', error)
  }
}

async function loadWhiteboard() {
  if (props.isNew) return
  
  try {
    const response = await whiteboardAPI.get(whiteboardId)
    console.log('加载白板详情结果:', response)
    whiteboard.value = response.code === 200 ? response.data : {}
    
    await loadVersions()
  } catch (error) {
    console.error('Load whiteboard error:', error)
  }
}

async function loadVersions() {
  if (!whiteboard.value.id) return
  
  try {
    const data = await whiteboardAPI.getVersions(whiteboard.value.id)
    console.log('加载版本历史结果:', data)
    // 正确处理API返回的数据格式
    versions.value = (data.code === 200 && Array.isArray(data.data)) ? data.data : []
  } catch (error) {
    console.error('Load versions error:', error)
    versions.value = []
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
      room_key: whiteboard.value.room_key,
      // WBO会自动保存数据，这里只保存标题和基本信息
      data: {
        room_key: whiteboard.value.room_key
      }
    }
    
    if (whiteboard.value.id) {
      const updateResult = await whiteboardAPI.update(whiteboard.value.id, data)
      console.log('更新白板结果:', updateResult)
    } else {
      const createResult = await whiteboardAPI.create(data)
      console.log('创建白板结果:', createResult)
      
      // 正确处理API返回的数据格式
      if (createResult.code === 201 && createResult.data) {
        whiteboard.value.id = createResult.data.id
        whiteboard.value.room_key = createResult.data.room_key
        whiteboard.value.title = createResult.data.title
      } else {
        throw new Error('创建白板失败: ' + (createResult.message || '未知错误'))
      }
    }
    
    await loadVersions()
    
    saveStatus.value = '已保存'
    if (!silent) ElMessage.success('保存成功')
  } catch (error) {
    console.error('Save whiteboard error:', error)
    saveStatus.value = '保存失败'
    if (!silent) ElMessage.error('保存失败: ' + (error.message || '服务器错误'))
  }
}

async function rollbackVersion(version) {
  try {
    await whiteboardAPI.rollbackVersion(whiteboard.value.id, version.id)
    whiteboard.value.data = version.data
    await loadVersions()
    ElMessage.success('回滚成功')
  } catch (error) {
    console.error('Rollback version error:', error)
    ElMessage.error('回滚失败')
  }
}

onMounted(async () => {
  await getWboToken()
  await loadWhiteboard()
  
  // 对于新建白板，生成一个唯一的roomKey
  if (props.isNew && !whiteboard.value.room_key) {
    whiteboard.value.room_key = 'wb-' + Math.random().toString(36).substr(2, 9)
  }
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

.wbo-iframe {
  display: block;
  width: 100%;
  height: 600px;
  border: none;
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
