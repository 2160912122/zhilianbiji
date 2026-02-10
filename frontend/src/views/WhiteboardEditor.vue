<template>
  <div class="whiteboard-editor">
    <el-card>
      <template #header>
        <div class="editor-header">
          <div class="header-left">
            <el-button link @click="$router.push('/whiteboards')">
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

// 生成唯一的默认标题
const generateUniqueTitle = () => {
  const timestamp = new Date().getTime()
  return `新白板_${timestamp}`
}

const whiteboard = ref({
  id: null,
  title: generateUniqueTitle(),
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
      
      // 处理AI生成的内容
      drawFromAI(aiContent)
      
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
  console.log('发送绘制命令:', command)
  if (iframe && iframe.contentWindow) {
    console.log('向iframe发送消息')
    iframe.contentWindow.postMessage(command, '*')
  } else {
    console.log('iframe未就绪或contentWindow不存在')
  }
}



// 颜色映射
const colorMap = {
  '红色': '#FF0000',
  '红': '#FF0000',
  '绿色': '#00FF00',
  '绿': '#00FF00',
  '蓝色': '#0000FF',
  '蓝': '#0000FF',
  '黄色': '#FFFF00',
  '黄': '#FFFF00',
  '橙色': '#FFA500',
  '橙': '#FFA500',
  '紫色': '#800080',
  '紫': '#800080',
  '黑色': '#000000',
  '黑': '#000000',
  '白色': '#FFFFFF',
  '白': '#FFFFFF',
  '棕色': '#8B4513',
  '棕': '#8B4513',
  '灰色': '#808080',
  '灰': '#808080'
};

// 大小映射
const sizeMap = {
  '小': 2,
  '中': 4,
  '大': 6
};

// 位置映射
const positionMap = {
  '上': { x: 300, y: 200 },
  '下': { x: 300, y: 400 },
  '左': { x: 200, y: 300 },
  '右': { x: 400, y: 300 },
  '中心': { x: 300, y: 300 },
  '中间': { x: 300, y: 300 }
};

// 从AI生成的内容中提取绘制步骤
function extractDrawingSteps(aiContent) {
  // 常见的绘制关键词
  const drawKeywords = ['画', '绘制', '画一个', '绘制一个', '画一条', '绘制一条', '画一个圆', '绘制一个圆', '画一个矩形', '绘制一个矩形', '画一条线', '绘制一条线', '写', '标注', '添加文字', '写上', '画出', '画成', '画好', '画完', '画出来']
  
  // 图形类型关键词
  const shapeKeywords = {
    '圆': 'circle',
    '圆形': 'circle',
    '椭圆': 'circle',
    '椭圆形': 'circle',
    '矩形': 'rectangle',
    '正方形': 'rectangle',
    '线': 'line',
    '直线': 'line',
    '竖线': 'line',
    '曲线': 'line',
    '三角形': 'triangle',
    '文字': 'text'
  }
  
  const steps = []
  
  // 按句子分割文本
  const sentences = aiContent.split(/[。！？；;.!?]/)
  
  for (const sentence of sentences) {
    const trimmedSentence = sentence.trim()
    if (!trimmedSentence) continue
    
    console.log('检查句子:', trimmedSentence)
    
    // 检查句子是否包含绘制相关的关键词
    const hasDrawKeyword = drawKeywords.some(keyword => trimmedSentence.includes(keyword))
    console.log('包含绘制关键词:', hasDrawKeyword)
    
    if (hasDrawKeyword) {
      // 识别基本图形类型
      let shapeType = 'line'
      for (const [keyword, type] of Object.entries(shapeKeywords)) {
        if (trimmedSentence.includes(keyword)) {
          shapeType = type
          break
        }
      }
      console.log('识别为图形类型:', shapeType)
      
      // 提取颜色
      let color = '#000000';
      for (const [name, value] of Object.entries(colorMap)) {
        if (trimmedSentence.includes(name)) {
          color = value;
          break;
        }
      }
      
      // 提取大小
      let size = 3;
      for (const [name, value] of Object.entries(sizeMap)) {
        if (trimmedSentence.includes(name)) {
          size = value;
          break;
        }
      }
      
      // 提取位置
      let position = { x: 300, y: 300 };
      for (const [name, value] of Object.entries(positionMap)) {
        if (trimmedSentence.includes(name)) {
          position = value;
          break;
        }
      }
      
      // 提取其他参数
      let radius = 50;
      if (shapeType === 'circle' && trimmedSentence.includes('半径')) {
        const radiusMatch = trimmedSentence.match(/半径(\d+)/);
        if (radiusMatch) {
          radius = parseInt(radiusMatch[1]);
        }
      }
      
      let width = 100;
      let height = 80;
      if (shapeType === 'rectangle') {
        if (trimmedSentence.includes('宽')) {
          const widthMatch = trimmedSentence.match(/宽(\d+)/);
          if (widthMatch) {
            width = parseInt(widthMatch[1]);
          }
        }
        if (trimmedSentence.includes('高')) {
          const heightMatch = trimmedSentence.match(/高(\d+)/);
          if (heightMatch) {
            height = parseInt(heightMatch[1]);
          }
        }
      }
      
      // 提取文字内容
      let text = '文字';
      if (shapeType === 'text') {
        // 尝试从句子中提取文字内容
        const textMatch = trimmedSentence.match(/写(.+)/);
        if (textMatch) {
          text = textMatch[1].trim();
        }
      }
      
      steps.push({
        text: trimmedSentence,
        type: shapeType,
        params: {
          color: color,
          size: size,
          x: position.x,
          y: position.y,
          radius: radius,
          width: width,
          height: height,
          text: text
        }
      })
    }
  }
  
  console.log('提取的步骤:', steps)
  
  return steps
}

// 通用绘制函数
function drawShape(type, params) {
  console.log('绘制图形:', type, params)
  
  switch (type) {
    case 'circle':
      // 绘制圆形
      sendToWBO({
        type: 'draw',
        tool: 'Pencil',
        action: 'circle',
        data: {
          x: params.x || 300,
          y: params.y || 300,
          radius: params.radius || 50,
          color: params.color || '#000000',
          size: params.size || 3
        }
      });
      break;
    case 'rectangle':
      // 绘制矩形
      const width = params.width || 100;
      const height = params.height || 80;
      sendToWBO({
        type: 'draw',
        tool: 'Pencil',
        action: 'line',
        data: {
          points: [
            { x: params.x - width / 2, y: params.y - height / 2 },
            { x: params.x + width / 2, y: params.y - height / 2 },
            { x: params.x + width / 2, y: params.y + height / 2 },
            { x: params.x - width / 2, y: params.y + height / 2 },
            { x: params.x - width / 2, y: params.y - height / 2 }
          ],
          color: params.color || '#000000',
          size: params.size || 3
        }
      });
      break;
    case 'line':
      // 绘制线条
      sendToWBO({
        type: 'draw',
        tool: 'Pencil',
        action: 'line',
        data: {
          points: params.points || [
            { x: params.x - 50, y: params.y },
            { x: params.x + 50, y: params.y }
          ],
          color: params.color || '#000000',
          size: params.size || 3
        }
      });
      break;
    case 'triangle':
      // 绘制三角形
      sendToWBO({
        type: 'draw',
        tool: 'Pencil',
        action: 'line',
        data: {
          points: [
            { x: params.x, y: params.y - 50 },
            { x: params.x + 50, y: params.y + 50 },
            { x: params.x - 50, y: params.y + 50 },
            { x: params.x, y: params.y - 50 }
          ],
          color: params.color || '#000000',
          size: params.size || 3
        }
      });
      break;
    case 'text':
      // 绘制文字
      sendToWBO({
        type: 'draw',
        tool: 'Text',
        action: 'text',
        data: {
          x: params.x || 300,
          y: params.y || 300,
          text: params.text || '文字',
          color: params.color || '#000000',
          size: params.size || 16
        }
      });
      break;
    default:
      console.log('未知图形类型:', type);
  }
}

// 根据AI生成的内容显示绘制步骤（不再自动绘制）
async function drawFromAI(aiContent) {
  console.log('开始处理AI生成的绘制步骤:', aiContent)
  
  // 提取绘制步骤
  const steps = extractDrawingSteps(aiContent)
  console.log('提取的绘制步骤:', steps)
  
  // 显示AI生成的内容和提取的步骤作为提示
  ElMessageBox.alert(
    `<div style="max-height: 400px; overflow-y: auto;">
      <h4>AI生成的绘制步骤</h4>
      <pre style="white-space: pre-wrap; word-break: break-all;">${aiContent}</pre>
      <h4>提取的详细步骤</h4>
      <ul>
        ${steps.map((step, index) => `
          <li style="margin: 5px 0;">
            <strong>步骤 ${index + 1}:</strong> ${step.text}
            ${step.params ? `<br><small style="color: #666;">
              类型: ${step.type}
              ${step.params.color ? `, 颜色: ${step.params.color}` : ''}
              ${step.params.size ? `, 大小: ${step.params.size}` : ''}
              ${step.params.x && step.params.y ? `, 位置: (${step.params.x}, ${step.params.y})` : ''}
            </small>` : ''}
          </li>
        `).join('')}
      </ul>
      <p style="margin-top: 10px; color: #666;">请根据以上步骤手动绘制白板内容。</p>
    </div>`,
    'AI绘制步骤提示',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '确定',
      type: 'info'
    }
  )
  
  ElMessage.success('AI生成的绘制步骤已准备就绪')
}

// 绘制圆形
function drawCircle(index) {
  const x = 200 + (index % 3) * 300
  const y = 200 + Math.floor(index / 3) * 200
  const radius = 50 + (index % 3) * 20
  
  sendToWBO({
    type: 'draw',
    tool: 'Pencil',
    action: 'circle',
    data: {
      x: x,
      y: y,
      radius: radius,
      color: getRandomColor(),
      size: 3
    }
  })
}

// 绘制矩形
function drawRectangle(index) {
  const x = 200 + (index % 3) * 300
  const y = 200 + Math.floor(index / 3) * 200
  const width = 100 + (index % 3) * 50
  const height = 80 + (index % 3) * 30
  
  sendToWBO({
    type: 'draw',
    tool: 'Pencil',
    action: 'rectangle',
    data: {
      x: x - width / 2,
      y: y - height / 2,
      width: width,
      height: height,
      color: getRandomColor(),
      size: 3
    }
  })
}

// 绘制线条
function drawLine(index) {
  const startX = 200 + (index % 3) * 300
  const startY = 200 + Math.floor(index / 3) * 200
  const endX = startX + 100 + (index % 3) * 50
  const endY = startY + 50 + (index % 3) * 30
  
  sendToWBO({
    type: 'draw',
    tool: 'Pencil',
    action: 'line',
    data: {
      points: [
        { x: startX, y: startY },
        { x: endX, y: endY }
      ],
      color: getRandomColor(),
      size: 3
    }
  })
}

// 绘制文字
function drawText(index, text) {
  const x = 200 + (index % 3) * 300
  const y = 200 + Math.floor(index / 3) * 200
  
  sendToWBO({
    type: 'draw',
    tool: 'Text',
    action: 'text',
    data: {
      x: x,
      y: y,
      text: text.substring(0, 20), // 限制文字长度
      color: '#000000',
      size: 16
    }
  })
}

// 绘制默认图形
function drawDefaultShape(index) {
  drawCircle(index)
}

// 获取随机颜色
function getRandomColor() {
  const colors = ['#FF4136', '#0074D9', '#2ECC40', '#FFDC00', '#FF851B', '#B10DC9', '#001F3F', '#39CCCC', '#01FF70', '#FF4136']
  return colors[Math.floor(Math.random() * colors.length)]
}

// 绘制示例内容
function drawExampleContent() {
  // 绘制一个简单的流程图
  const startX = 200
  const startY = 150
  const stepWidth = 120
  const stepHeight = 60
  const stepGap = 100
  
  // 开始
  sendToWBO({
    type: 'draw',
    tool: 'Pencil',
    action: 'rectangle',
    data: {
      x: startX - stepWidth / 2,
      y: startY - stepHeight / 2,
      width: stepWidth,
      height: stepHeight,
      color: '#0074D9',
      size: 3
    }
  })
  
  // 开始文字
  setTimeout(() => {
    sendToWBO({
      type: 'draw',
      tool: 'Text',
      action: 'text',
      data: {
        x: startX,
        y: startY,
        text: '开始',
        color: '#000000',
        size: 16
      }
    })
  }, 300)
  
  // 步骤1
  setTimeout(() => {
    sendToWBO({
      type: 'draw',
      tool: 'Pencil',
      action: 'rectangle',
      data: {
        x: startX - stepWidth / 2,
        y: startY + stepGap - stepHeight / 2,
        width: stepWidth,
        height: stepHeight,
        color: '#2ECC40',
        size: 3
      }
    })
  }, 600)
  
  // 步骤1文字
  setTimeout(() => {
    sendToWBO({
      type: 'draw',
      tool: 'Text',
      action: 'text',
      data: {
        x: startX,
        y: startY + stepGap,
        text: '步骤1',
        color: '#000000',
        size: 16
      }
    })
  }, 900)
  
  // 连接线1
  setTimeout(() => {
    sendToWBO({
      type: 'draw',
      tool: 'Pencil',
      action: 'line',
      data: {
        points: [
          { x: startX, y: startY + stepHeight / 2 },
          { x: startX, y: startY + stepGap - stepHeight / 2 }
        ],
        color: '#000000',
        size: 2
      }
    })
  }, 1200)
  
  // 步骤2
  setTimeout(() => {
    sendToWBO({
      type: 'draw',
      tool: 'Pencil',
      action: 'rectangle',
      data: {
        x: startX - stepWidth / 2,
        y: startY + stepGap * 2 - stepHeight / 2,
        width: stepWidth,
        height: stepHeight,
        color: '#FFDC00',
        size: 3
      }
    })
  }, 1500)
  
  // 步骤2文字
  setTimeout(() => {
    sendToWBO({
      type: 'draw',
      tool: 'Text',
      action: 'text',
      data: {
        x: startX,
        y: startY + stepGap * 2,
        text: '步骤2',
        color: '#000000',
        size: 16
      }
    })
  }, 1800)
  
  // 连接线2
  setTimeout(() => {
    sendToWBO({
      type: 'draw',
      tool: 'Pencil',
      action: 'line',
      data: {
        points: [
          { x: startX, y: startY + stepGap + stepHeight / 2 },
          { x: startX, y: startY + stepGap * 2 - stepHeight / 2 }
        ],
        color: '#000000',
        size: 2
      }
    })
  }, 2100)
  
  // 结束
  setTimeout(() => {
    sendToWBO({
      type: 'draw',
      tool: 'Pencil',
      action: 'rectangle',
      data: {
        x: startX - stepWidth / 2,
        y: startY + stepGap * 3 - stepHeight / 2,
        width: stepWidth,
        height: stepHeight,
        color: '#FF4136',
        size: 3
      }
    })
  }, 2400)
  
  // 结束文字
  setTimeout(() => {
    sendToWBO({
      type: 'draw',
      tool: 'Text',
      action: 'text',
      data: {
        x: startX,
        y: startY + stepGap * 3,
        text: '结束',
        color: '#000000',
        size: 16
      }
    })
  }, 2700)
  
  // 连接线3
  setTimeout(() => {
    sendToWBO({
      type: 'draw',
      tool: 'Pencil',
      action: 'line',
      data: {
        points: [
          { x: startX, y: startY + stepGap * 2 + stepHeight / 2 },
          { x: startX, y: startY + stepGap * 3 - stepHeight / 2 }
        ],
        color: '#000000',
        size: 2
      }
    })
  }, 3000)
}

// 计算WBO URL
const wboUrl = computed(() => {
  // 确保roomKey有效，避免生成无效URL
  const roomKey = whiteboard.value.room_key || 'new-whiteboard-' + Date.now()
  // 使用whitebophir服务
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
