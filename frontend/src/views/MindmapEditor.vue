<template>
  <div class="mindmap-editor">
    <el-card class="mindmap-editor">
      <template #header>
        <div class="editor-header">
          <div class="header-left">
            <el-button link @click="$router.push('/mindmaps')">
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
              <AIModuleButton />
              <el-divider direction="vertical" />
              <el-tooltip content="版本历史" placement="top">
                <el-button @click="showVersions = true">
                  <el-icon><Clock /></el-icon>
                </el-button>
              </el-tooltip>
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
    
    <!-- 版本历史抽屉 -->
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
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { mindmapAPI } from '@/api/editor'
import { ElMessage, ElDialog, ElForm, ElFormItem, ElSelect, ElOption, ElDatePicker, ElButton, ElTable, ElTableColumn, ElTag, ElIcon } from 'element-plus'
import { Share, Delete, Check, DocumentCopy, Back, Clock } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { useAIStore } from '@/store/ai'
import AIModuleButton from '@/components/AIModuleButton.vue'

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

// 生成唯一的默认标题
const generateUniqueTitle = () => {
  const timestamp = new Date().getTime()
  return `新脑图_${timestamp}`
}

const mindmap = ref({
  id: null,
  title: generateUniqueTitle(),
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

// 版本历史功能
const versions = ref([])
const showVersions = ref(false)

// 初始化AI store
const aiStore = useAIStore()

// 监听AI生成的内容
watch(() => aiStore.hasNewContent, (hasNewContent) => {
  if (hasNewContent) {
    try {
      let generatedContent = aiStore.generatedContent
      console.log('AI生成的原始内容:', generatedContent)
      
      // 检查AI生成的内容是否为空
      if (!generatedContent || generatedContent.trim() === '') {
        ElMessage.error('AI服务未返回任何内容，请检查AI服务配置是否正确')
        console.error('AI生成内容为空，可能的原因：')
        console.error('1. AI服务配置不正确（API密钥、基础URL等）')
        console.error('2. 网络连接问题')
        console.error('3. AI模型调用失败')
        return
      }
      
      // 提取Markdown代码块中的JSON内容
      let jsonContent = generatedContent
      const jsonMatch = generatedContent.match(/```json[\s\S]*?```/)
      if (jsonMatch) {
        console.log('找到JSON代码块:', jsonMatch[0])
        jsonContent = jsonMatch[0].replace(/```json\s*/, '').replace(/\s*```/, '')
      } else {
        // 尝试提取普通代码块
        const codeMatch = generatedContent.match(/```[\s\S]*?```/)
        if (codeMatch) {
          console.log('找到普通代码块:', codeMatch[0])
          jsonContent = codeMatch[0].replace(/```\s*/, '').replace(/\s*```/, '')
        } else {
          // 尝试直接查找JSON格式的内容
          console.log('未找到代码块，尝试直接处理内容')
          // 尝试找到JSON的开始和结束
          const jsonStart = generatedContent.indexOf('{')
          const jsonEnd = generatedContent.lastIndexOf('}')
          if (jsonStart !== -1 && jsonEnd !== -1) {
            jsonContent = generatedContent.substring(jsonStart, jsonEnd + 1)
            console.log('提取到的JSON内容:', jsonContent)
          }
        }
      }
      
      // 清理并验证JSON内容
      jsonContent = jsonContent.trim()
      console.log('清理后的JSON内容:', jsonContent)
      
      if (!jsonContent) {
        ElMessage.error('AI未生成有效的脑图数据，请检查AI服务的系统提示词是否正确')
        return
      }
      
      // 解析AI生成的脑图数据（JSON格式）
      try {
        const mindmapData = JSON.parse(jsonContent)
        console.log('解析后的脑图数据:', mindmapData)
        
        if (mindmapData.nodes && Array.isArray(mindmapData.nodes) && mindmapData.edges && Array.isArray(mindmapData.edges)) {
          // 使用AI生成的脑图数据
          nodes.value = mindmapData.nodes
          edges.value = mindmapData.edges
          
          // 更新节点ID计数器
          const maxNodeId = Math.max(...nodes.value.map(node => node.id), 1)
          nodeIdCounter = maxNodeId + 1
          
          // 保存到服务器
          handleSave(true)
          ElMessage.success('AI生成的脑图已成功加载')
        } else {
          ElMessage.error('AI生成的脑图格式不正确')
        }
      } catch (parseError) {
        console.error('JSON解析失败:', parseError)
        console.error('原始JSON内容:', jsonContent)
        
        // 尝试修复JSON格式
        try {
          // 移除可能的注释
          const cleanedJson = jsonContent.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '')
          console.log('清理后的JSON内容:', cleanedJson)
          const mindmapData = JSON.parse(cleanedJson)
          console.log('修复后解析的脑图数据:', mindmapData)
          
          if (mindmapData.nodes && Array.isArray(mindmapData.nodes) && mindmapData.edges && Array.isArray(mindmapData.edges)) {
            nodes.value = mindmapData.nodes
            edges.value = mindmapData.edges
            const maxNodeId = Math.max(...nodes.value.map(node => node.id), 1)
            nodeIdCounter = maxNodeId + 1
            handleSave(true)
            ElMessage.success('AI生成的脑图已成功加载（已修复格式）')
            return
          }
        } catch (cleanError) {
          console.error('修复JSON格式失败:', cleanError)
        }
        
        // 尝试从文本描述中生成脑图数据
        try {
          console.log('尝试从文本描述中生成脑图数据')
          const generatedMindmap = generateMindmapFromDescription(jsonContent)
          
          // 使用生成的脑图数据
          nodes.value = generatedMindmap.nodes
          edges.value = generatedMindmap.edges
          nodeIdCounter = Math.max(...nodes.value.map(node => node.id), 1) + 1
          
          // 保存到服务器
          console.log('保存前的数据:', {
            title: mindmap.value.title || '新脑图',
            data: {
              nodes: JSON.parse(JSON.stringify(nodes.value)),
              edges: JSON.parse(JSON.stringify(edges.value))
            },
            is_public: mindmap.value.is_public
          })
          
          handleSave(true)
          ElMessage.success('AI生成的脑图已成功加载（根据描述生成）')
          return
        } catch (descriptionError) {
          console.error('从描述生成脑图失败:', descriptionError)
        }
        
        // 尝试生成默认的脑图数据
        try {
          console.log('尝试生成默认脑图数据')
          const defaultMindmap = {
            nodes: [
              { id: 1, label: '主题', position: { x: 400, y: 100 } },
              { id: 2, label: '子主题1', position: { x: 200, y: 200 } },
              { id: 3, label: '子主题2', position: { x: 600, y: 200 } }
            ],
            edges: [
              { from: 1, to: 2 },
              { from: 1, to: 3 }
            ]
          }
          
          nodes.value = defaultMindmap.nodes
          edges.value = defaultMindmap.edges
          nodeIdCounter = 4
          handleSave(true)
          ElMessage.success('AI生成的脑图格式有问题，已生成默认脑图结构')
          return
        } catch (defaultError) {
          console.error('生成默认脑图失败:', defaultError)
        }
        
        ElMessage.error('解析AI生成的脑图失败，JSON格式不正确')
      }
    } catch (error) {
      console.error('解析AI脑图数据失败:', error)
      ElMessage.error('解析AI生成的脑图失败')
    } finally {
      // 重置AI store状态
      aiStore.resetGeneratedContent()
    }
  }
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
    let mindmapData
    if (props.isShared && props.sharedMindmap) {
      mindmapData = props.sharedMindmap
    } else if (props.isShared) {
      const sharedResponse = await mindmapAPI.getShared(mindmapId)
      mindmapData = sharedResponse.data
    } else {
      const response = await mindmapAPI.get(mindmapId)
      mindmapData = response.data
    }
    
    mindmap.value = mindmapData
    
    if (mindmapData.data && mindmapData.data.nodes) {
      nodes.value = mindmapData.data.nodes
      edges.value = mindmapData.data.edges || []
      // 确保nodes.value是数组并且不为空
      if (Array.isArray(nodes.value) && nodes.value.length > 0) {
        nodeIdCounter = Math.max(...nodes.value.map(n => n.id)) + 1
      } else {
        nodeIdCounter = 1
      }
    }
    
    // 加载版本历史
    await loadVersions()
  } catch (error) {
    console.error('Load mindmap error:', error)
  }
}

async function loadVersions() {
  if (!mindmap.value.id) return
  
  try {
    const response = await mindmapAPI.getVersions(mindmap.value.id)
    console.log('加载版本历史结果:', response)
    // 正确处理API返回的数据格式
    versions.value = (response.code === 200 && Array.isArray(response.data)) ? response.data : []
  } catch (error) {
    console.error('Load versions error:', error)
    versions.value = []
  }
}

async function rollbackVersion(version) {
  try {
    await mindmapAPI.rollbackVersion(mindmap.value.id, version.id)
    
    // 重新加载脑图数据
    await loadMindmap()
    ElMessage.success('版本回滚成功')
    showVersions.value = false
  } catch (error) {
    console.error('Rollback version error:', error)
    ElMessage.error('版本回滚失败')
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
    
    // 打印完整请求数据
    console.log('【保存脑图-完整请求数据】:', JSON.stringify(data, null, 2))
    
    // 检查数据是否有明显问题
    if (!data.title) {
      console.error('【保存失败】脑图标题不能为空')
      if (!silent) ElMessage.error('脑图标题不能为空')
      return
    }
    
    if (mindmap.value.id) {
      console.log('【更新脑图】ID:', mindmap.value.id)
      await mindmapAPI.update(mindmap.value.id, data)
    } else {
      console.log('【创建新脑图】')
      const result = await mindmapAPI.create(data)
      console.log('【创建成功】响应:', result)
      mindmap.value.id = result.data.id
      mindmap.value.title = result.data.title
    }
    
    // 保存成功后加载版本历史
    if (mindmap.value.id) {
      await loadVersions()
    }
    
    saveStatus.value = '已保存'
    if (!silent) ElMessage.success('保存成功')
  } catch (error) {
    // 打印详细的错误信息
    console.error('【保存失败-详细错误】:', {
      status: error.response?.status,
      data: error.response?.data, // 后端返回的具体错误提示
      requestData: error.config?.data // 实际发送给服务器的数据
    })
    
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

// 从文本描述中生成脑图数据
function generateMindmapFromDescription(description) {
  const nodes = []
  const edges = []
  let nodeId = 1
  
  // 检查描述中是否包含中国特色社会主义相关内容
  if (description.includes('中国特色社会主义')) {
    // 生成中国特色社会主义脑图
    // 中心节点
    const centerNode = {
      id: nodeId++,
      text: '中国特色社会主义',
      x: 400,
      y: 100,
      width: 180,
      height: 40,
      parentId: null
    }
    nodes.push(centerNode)
    
    // 主要分支节点
    const branches = [
      { text: '指导思想', x: 150, y: 200 },
      { text: '基本路线', x: 300, y: 200 },
      { text: '经济', x: 450, y: 200 },
      { text: '政治', x: 600, y: 200 },
      { text: '文化', x: 225, y: 400 },
      { text: '社会', x: 400, y: 400 },
      { text: '生态文明', x: 575, y: 400 }
    ]
    
    const branchNodes = []
    for (let i = 0; i < branches.length; i++) {
      const branchNode = {
        id: nodeId++,
        text: branches[i].text,
        x: branches[i].x,
        y: branches[i].y,
        width: 120,
        height: 40,
        parentId: centerNode.id
      }
      nodes.push(branchNode)
      branchNodes.push(branchNode)
      edges.push({ from: centerNode.id, to: branchNode.id })
    }
    
    // 指导思想子节点
    const guidingIdeas = ['马克思列宁主义', '毛泽东思想', '邓小平理论', '三个代表', '科学发展观', '习近平新时代中国特色社会主义思想']
    for (let i = 0; i < guidingIdeas.length; i++) {
      const ideaNode = {
        id: nodeId++,
        text: guidingIdeas[i],
        x: 100 + (i % 2) * 150,
        y: 300 + Math.floor(i / 2) * 80,
        width: 150,
        height: 40,
        parentId: branchNodes[0].id
      }
      nodes.push(ideaNode)
      edges.push({ from: branchNodes[0].id, to: ideaNode.id })
    }
    
    // 基本路线子节点
    const basicLines = ['以经济建设为中心', '坚持四项基本原则', '坚持改革开放']
    for (let i = 0; i < basicLines.length; i++) {
      const lineNode = {
        id: nodeId++,
        text: basicLines[i],
        x: 250 + i * 150,
        y: 300,
        width: 150,
        height: 40,
        parentId: branchNodes[1].id
      }
      nodes.push(lineNode)
      edges.push({ from: branchNodes[1].id, to: lineNode.id })
    }
    
    // 经济子节点
    const economyNodes = ['社会主义市场经济', '公有制为主体', '多种所有制共同发展', '高质量发展']
    for (let i = 0; i < economyNodes.length; i++) {
      const ecoNode = {
        id: nodeId++,
        text: economyNodes[i],
        x: 400 + (i % 2) * 150,
        y: 300 + Math.floor(i / 2) * 80,
        width: 150,
        height: 40,
        parentId: branchNodes[2].id
      }
      nodes.push(ecoNode)
      edges.push({ from: branchNodes[2].id, to: ecoNode.id })
    }
    
    // 政治子节点
    const politicsNodes = ['党的领导', '人民民主', '法治', '社会主义民主政治']
    for (let i = 0; i < politicsNodes.length; i++) {
      const polNode = {
        id: nodeId++,
        text: politicsNodes[i],
        x: 550 + (i % 2) * 150,
        y: 300 + Math.floor(i / 2) * 80,
        width: 150,
        height: 40,
        parentId: branchNodes[3].id
      }
      nodes.push(polNode)
      edges.push({ from: branchNodes[3].id, to: polNode.id })
    }
    
    // 文化子节点
    const cultureNodes = ['社会主义核心价值观', '中华优秀传统文化', '文化自信', '文化软实力']
    for (let i = 0; i < cultureNodes.length; i++) {
      const culNode = {
        id: nodeId++,
        text: cultureNodes[i],
        x: 150 + (i % 2) * 150,
        y: 500 + Math.floor(i / 2) * 80,
        width: 150,
        height: 40,
        parentId: branchNodes[4].id
      }
      nodes.push(culNode)
      edges.push({ from: branchNodes[4].id, to: culNode.id })
    }
    
    // 社会子节点
    const societyNodes = ['共同富裕', '社会公平正义', '教育医疗住房', '社会保障体系']
    for (let i = 0; i < societyNodes.length; i++) {
      const socNode = {
        id: nodeId++,
        text: societyNodes[i],
        x: 350 + (i % 2) * 150,
        y: 500 + Math.floor(i / 2) * 80,
        width: 150,
        height: 40,
        parentId: branchNodes[5].id
      }
      nodes.push(socNode)
      edges.push({ from: branchNodes[5].id, to: socNode.id })
    }
    
    // 生态文明子节点
    const ecologyNodes = ['绿水青山就是金山银山', '可持续发展', '环境保护', '绿色发展']
    for (let i = 0; i < ecologyNodes.length; i++) {
      const ecoNode = {
        id: nodeId++,
        text: ecologyNodes[i],
        x: 550 + (i % 2) * 150,
        y: 500 + Math.floor(i / 2) * 80,
        width: 150,
        height: 40,
        parentId: branchNodes[6].id
      }
      nodes.push(ecoNode)
      edges.push({ from: branchNodes[6].id, to: ecoNode.id })
    }
    
    return { nodes, edges }
  } else {
    // 默认生成计算机专业课程脑图
    const courseCategories = ['基础课程', '核心课程', '选修课程']
    const basicCourses = ['编程基础', '数据结构', '算法', '计算机组成原理', '操作系统']
    const coreCourses = ['数据库', '计算机网络', '软件工程', '人工智能', '计算机图形学']
    const electiveCourses = ['编译原理', '计算机安全', '机器学习', '深度学习', '自然语言处理', '计算机视觉', '分布式系统', '嵌入式系统', '移动应用开发', '云计算', '大数据处理']
    
    // 生成中心节点
    const centerNode = {
      id: nodeId++,
      text: '计算机专业课程',
      x: 400,
      y: 100,
      width: 150,
      height: 40,
      parentId: null
    }
    nodes.push(centerNode)
    
    // 生成课程类别节点
    const categoryNodes = []
    for (let i = 0; i < courseCategories.length; i++) {
      const categoryNode = {
        id: nodeId++,
        text: courseCategories[i],
        x: 200 + i * 250,
        y: 200,
        width: 120,
        height: 40,
        parentId: centerNode.id
      }
      nodes.push(categoryNode)
      categoryNodes.push(categoryNode)
      edges.push({ from: centerNode.id, to: categoryNode.id })
    }
    
    // 生成基础课程节点
    for (let i = 0; i < basicCourses.length; i++) {
      const courseNode = {
        id: nodeId++,
        text: basicCourses[i],
        x: 150 + (i % 2) * 150,
        y: 300 + Math.floor(i / 2) * 100,
        width: 120,
        height: 40,
        parentId: categoryNodes[0].id
      }
      nodes.push(courseNode)
      edges.push({ from: categoryNodes[0].id, to: courseNode.id })
    }
    
    // 生成核心课程节点
    for (let i = 0; i < coreCourses.length; i++) {
      const courseNode = {
        id: nodeId++,
        text: coreCourses[i],
        x: 400 + (i % 2) * 150,
        y: 300 + Math.floor(i / 2) * 100,
        width: 120,
        height: 40,
        parentId: categoryNodes[1].id
      }
      nodes.push(courseNode)
      edges.push({ from: categoryNodes[1].id, to: courseNode.id })
    }
    
    // 生成选修课程节点
    for (let i = 0; i < electiveCourses.length; i++) {
      const courseNode = {
        id: nodeId++,
        text: electiveCourses[i],
        x: 650 + (i % 2) * 150,
        y: 300 + Math.floor(i / 2) * 100,
        width: 120,
        height: 40,
        parentId: categoryNodes[2].id
      }
      nodes.push(courseNode)
      edges.push({ from: categoryNodes[2].id, to: courseNode.id })
    }
    
    return { nodes, edges }
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
  flex-wrap: wrap;
  padding: 5px;
  background: #f5f7fa;
  border-radius: 4px;
}

.operation-buttons .el-button {
  margin-right: 0;
  border-radius: 0;
  margin: 2px;
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
  margin: 2px;
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
