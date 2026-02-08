<template>
  <div class="flowchart-editor-page">
    <el-card>
      <template #header>
        <div class="editor-header">
          <div class="header-left">
            <el-button link @click="$router.back()">
              <el-icon><Back /></el-icon>
              返回
            </el-button>
            <el-input
              v-model="flowTitle"
              placeholder="请输入流程图标题"
              style="width: 300px; margin-left: 20px"
              @input="handleTitleChange"
            />
          </div>
          <div class="header-right">
            <AIModuleButton />
            <el-button @click="handleShare">
              <el-icon><Share /></el-icon>
              分享
            </el-button>
            <el-button type="primary" @click="handleSave">
              <el-icon><Check /></el-icon>
              保存
            </el-button>
          </div>
        </div>
      </template>
      
      <FlowEditor
        ref="flowEditor"
        :flow-title="flowTitle"
        :initial-data="graphData"
        :flowchart-id="flowchartId"
        @title-change="handleTitleChange"
        @save="handleSaveFlowchart"
        @share="handleShareFlowchart"
        @export="handleExportFlowchart"
      />
    </el-card>
    
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
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back, Check, Share } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { useAIStore } from '@/store/ai'
import FlowEditor from '@/components/FlowEditor.vue'
import AIModuleButton from '@/components/AIModuleButton.vue'

const props = defineProps({
  isNew: {
    type: Boolean,
    default: false
  }
})

const route = useRoute()
const router = useRouter()
const flowchartId = route.params.id

const flowTitle = ref('未命名流程图')
const graphData = ref({ nodes: {}, edges: {} })
const shareDialogVisible = ref(false)
const sharing = ref(false)
const shareUrl = ref('')

const flowEditor = ref(null)

// 初始化AI store
const aiStore = useAIStore()

// 监听AI生成的内容
watch(() => aiStore.hasNewContent, (hasNewContent) => {
  if (hasNewContent) {
    try {
      let generatedContent = aiStore.generatedContent
      
      console.log('AI生成的原始内容:', generatedContent)
      
      // 提取Markdown代码块中的JSON内容
      let jsonContent = generatedContent
      
      // 尝试多种格式提取
      const jsonMatch = generatedContent.match(/```json[\s\S]*?```/)
      if (jsonMatch) {
        console.log('找到JSON代码块')
        jsonContent = jsonMatch[0].replace(/```json\s*/, '').replace(/\s*```/, '')
      } else {
        // 尝试提取普通代码块
        const codeMatch = generatedContent.match(/```[\s\S]*?```/)
        if (codeMatch) {
          console.log('找到普通代码块')
          jsonContent = codeMatch[0].replace(/```\s*/, '').replace(/\s*```/, '')
        } else {
          // 尝试直接提取JSON（如果内容看起来是JSON）
          console.log('尝试直接提取JSON')
          // 检查内容是否以{开头和}结尾
          if (generatedContent.trim().startsWith('{') && generatedContent.trim().endsWith('}')) {
            jsonContent = generatedContent.trim()
          }
        }
      }
      
      // 清理并验证JSON内容
      jsonContent = jsonContent.trim()
      console.log('提取的JSON内容:', jsonContent)
      
      if (!jsonContent) {
        ElMessage.error('AI未生成有效的流程图数据')
        return
      }
      
      // 检查是否是有效的JSON格式
      if (!jsonContent.startsWith('{') || !jsonContent.endsWith('}')) {
        ElMessage.error('AI生成的内容不是有效的JSON格式')
        return
      }
      
      // 解析AI生成的流程图数据（JSON格式）
      try {
        const flowchartData = JSON.parse(jsonContent)
        console.log('AI生成的流程图数据:', flowchartData)
        
        // 处理不同格式的节点数据
        if (flowchartData.nodes) {
          // 修复节点文本乱码问题
          const fixedNodes = {}
          let nodeCount = 0
          let nodeIds = []
          
          // 处理nodes为对象的情况
          if (typeof flowchartData.nodes === 'object' && !Array.isArray(flowchartData.nodes)) {
            nodeIds = Object.keys(flowchartData.nodes)
            for (const nodeId of nodeIds) {
              const node = flowchartData.nodes[nodeId]
              // 为节点生成合理的位置，避免重叠
                const x = 150 + (nodeCount % 2) * 400
                const y = 150 + Math.floor(nodeCount / 2) * 400
              
              fixedNodes[nodeId] = {
                  ...node,
                  id: nodeId,
                  x: node.x || (node.position?.x) || x,
                  y: node.y || (node.position?.y) || y,
                  text: node.text || node.label || '节点',
                  type: node.type || 'rect'
                }
              nodeCount++
            }
          } 
          // 处理nodes为数组的情况
          else if (Array.isArray(flowchartData.nodes)) {
            for (const node of flowchartData.nodes) {
              const nodeId = node.id || `node_${nodeCount}`
              // 为节点生成合理的位置，避免重叠
                const x = 150 + (nodeCount % 2) * 400
                const y = 150 + Math.floor(nodeCount / 2) * 400
              
              fixedNodes[nodeId] = {
                  ...node,
                  id: nodeId,
                  x: node.x || (node.position?.x) || x,
                  y: node.y || (node.position?.y) || y,
                  text: node.text || node.label || '节点',
                  type: node.type || 'rect'
                }
              nodeIds.push(nodeId)
              nodeCount++
            }
          }
          
          // 修复边文本乱码问题
          const fixedEdges = {}
          if (flowchartData.edges) {
            // 处理edges为对象的情况
            if (typeof flowchartData.edges === 'object' && !Array.isArray(flowchartData.edges)) {
              for (const [edgeId, edge] of Object.entries(flowchartData.edges)) {
                fixedEdges[edgeId] = {
                  ...edge,
                  id: edgeId,
                  source: edge.source || edge.from,
                  target: edge.target || edge.to,
                  text: edge.text || '',
                  type: edge.type || 'polyline'
                }
              }
            } 
            // 处理edges为数组的情况
            else if (Array.isArray(flowchartData.edges)) {
              let edgeCount = 0
              for (const edge of flowchartData.edges) {
                const edgeId = edge.id || `edge_${edgeCount}`
                fixedEdges[edgeId] = {
                  ...edge,
                  id: edgeId,
                  source: edge.source || edge.from,
                  target: edge.target || edge.to,
                  text: edge.text || '',
                  type: edge.type || 'polyline'
                }
                edgeCount++
              }
            }
          } else {
            // 如果AI没有生成边，自动生成边连接节点
            console.log('AI没有生成边，自动生成边连接节点')
            for (let i = 0; i < nodeIds.length - 1; i++) {
              const sourceNodeId = nodeIds[i]
              const targetNodeId = nodeIds[i + 1]
              const edgeId = `edge_${sourceNodeId}_${targetNodeId}`
              
              fixedEdges[edgeId] = {
                id: edgeId,
                source: sourceNodeId,
                target: targetNodeId,
                text: '',
                type: 'polyline'
              }
            }
          }
          
          // 使用修复后的流程图数据
          const fixedFlowchartData = {
            nodes: fixedNodes,
            edges: fixedEdges
          }
          
          console.log('准备设置graphData:', fixedFlowchartData)
          console.log('节点数量:', Object.keys(fixedNodes).length)
          console.log('边数量:', Object.keys(fixedEdges).length)
          
          // 确保数据格式正确
          if (Object.keys(fixedNodes).length === 0) {
            console.error('没有生成节点数据')
            ElMessage.error('AI生成的流程图没有节点数据')
            return
          }
          
          graphData.value = fixedFlowchartData
          console.log('graphData设置成功:', graphData.value)
          
          // 为新流程图生成唯一的标题
          if (!flowchartId && (!flowTitle.value || flowTitle.value === '未命名流程图')) {
            flowTitle.value = `AI生成的流程图_${Date.now()}`
          } else if (!flowTitle.value || flowTitle.value === '未命名流程图') {
            flowTitle.value = 'AI生成的流程图'
          }
          
          // 保存到服务器
          handleSaveFlowchart(graphData.value)
          ElMessage.success('AI生成的流程图已成功加载')
        } else {
          ElMessage.error('AI生成的流程图格式不正确')
        }
      } catch (parseError) {
        console.error('JSON解析失败:', parseError)
        console.error('原始JSON内容:', jsonContent)
        
        // 尝试修复JSON格式
        try {
          // 移除可能的注释
          const cleanedJson = jsonContent.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '')
          const flowchartData = JSON.parse(cleanedJson)
          console.log('修复后的流程图数据:', flowchartData)
          
          if (flowchartData.nodes) {
            // 修复节点文本乱码问题
            const fixedNodes = {}
            let nodeCount = 0
            let nodeIds = []
            
            // 处理nodes为对象的情况
            if (typeof flowchartData.nodes === 'object' && !Array.isArray(flowchartData.nodes)) {
              nodeIds = Object.keys(flowchartData.nodes)
              for (const nodeId of nodeIds) {
                const node = flowchartData.nodes[nodeId]
                // 为节点生成合理的位置，避免重叠
                const x = 150 + (nodeCount % 2) * 400
                const y = 150 + Math.floor(nodeCount / 2) * 400
                
                fixedNodes[nodeId] = {
                  ...node,
                  id: nodeId,
                  x: node.x || (node.position?.x) || x,
                  y: node.y || (node.position?.y) || y,
                  text: node.text || node.label || '节点',
                  type: node.type || 'rect'
                }
                nodeCount++
              }
            } 
            // 处理nodes为数组的情况
            else if (Array.isArray(flowchartData.nodes)) {
              for (const node of flowchartData.nodes) {
                const nodeId = node.id || `node_${nodeCount}`
                // 为节点生成合理的位置，避免重叠
                const x = 150 + (nodeCount % 2) * 400
                const y = 150 + Math.floor(nodeCount / 2) * 400
                
                fixedNodes[nodeId] = {
                  ...node,
                  id: nodeId,
                  x: node.x || (node.position?.x) || x,
                  y: node.y || (node.position?.y) || y,
                  text: node.text || node.label || '节点',
                  type: node.type || 'rect'
                }
                nodeIds.push(nodeId)
                nodeCount++
              }
            }
            
            // 修复边文本乱码问题
            const fixedEdges = {}
            if (flowchartData.edges) {
              // 处理edges为对象的情况
              if (typeof flowchartData.edges === 'object' && !Array.isArray(flowchartData.edges)) {
                for (const [edgeId, edge] of Object.entries(flowchartData.edges)) {
                  fixedEdges[edgeId] = {
                    ...edge,
                    id: edgeId,
                    source: edge.source || edge.from,
                    target: edge.target || edge.to,
                    text: edge.text || '',
                    type: edge.type || 'polyline'
                  }
                }
              } 
              // 处理edges为数组的情况
              else if (Array.isArray(flowchartData.edges)) {
                let edgeCount = 0
                for (const edge of flowchartData.edges) {
                  const edgeId = edge.id || `edge_${edgeCount}`
                  fixedEdges[edgeId] = {
                    ...edge,
                    id: edgeId,
                    source: edge.source || edge.from,
                    target: edge.target || edge.to,
                    text: edge.text || '',
                    type: edge.type || 'polyline'
                  }
                  edgeCount++
                }
              }
            } else {
              // 如果AI没有生成边，自动生成边连接节点
              console.log('AI没有生成边，自动生成边连接节点')
              for (let i = 0; i < nodeIds.length - 1; i++) {
                const sourceNodeId = nodeIds[i]
                const targetNodeId = nodeIds[i + 1]
                const edgeId = `edge_${sourceNodeId}_${targetNodeId}`
                
                fixedEdges[edgeId] = {
                  id: edgeId,
                  source: sourceNodeId,
                  target: targetNodeId,
                  text: '',
                  type: 'polyline'
                }
              }
            }
            
            // 使用修复后的流程图数据
            const fixedFlowchartData = {
              nodes: fixedNodes,
              edges: fixedEdges
            }
            
            graphData.value = fixedFlowchartData
            if (!flowTitle.value || flowTitle.value === '未命名流程图') {
              flowTitle.value = 'AI生成的流程图'
            }
            handleSaveFlowchart(graphData.value)
            ElMessage.success('AI生成的流程图已成功加载（已修复格式）')
            return
          }
        } catch (cleanError) {
          console.error('修复JSON格式失败:', cleanError)
        }
        
        ElMessage.error('解析AI生成的流程图失败，JSON格式不正确')
      }
    } catch (error) {
      console.error('解析AI流程图数据失败:', error)
      ElMessage.error('解析AI生成的流程图失败')
    }
    // 重置AI store状态
    aiStore.resetGeneratedContent()
  }
})

async function loadFlowchart() {
  if (props.isNew) return
  
  try {
    const response = await request.get(`/api/flowcharts/${flowchartId}`)

    flowTitle.value = response.data.title
    graphData.value = { nodes: {}, edges: {} }

    if (response.data.flow_data) {
      // 确保flow_data是正确的格式
      const flowData = response.data.flow_data
      if (flowData.nodes && flowData.edges) {
        // 格式正确，直接使用
        graphData.value = JSON.parse(JSON.stringify(flowData))
      } else if (flowData.nodes || flowData.edges) {
        // 部分格式正确，补全缺失部分
        graphData.value = {
          nodes: flowData.nodes || {},
          edges: flowData.edges || {}
        }
      } else {
        // 格式不正确，使用空数据
        graphData.value = { nodes: {}, edges: {} }
      }
    }
    console.log('加载的流程图数据:', graphData.value)
  } catch (error) {
    console.error('加载流程图失败:', error)
    ElMessage.error('加载流程图失败')
  }
}

function handleTitleChange(newTitle) {
  if (!newTitle) return
  
  // 更新本地标题
  flowTitle.value = newTitle
  
  // 自动保存，与其他编辑器保持一致的用户体验
  handleSave()
}

async function handleSaveFlowchart(flowData) {
  try {
    // 确保flowData格式正确
    const normalizedFlowData = {
      nodes: flowData.nodes || {},
      edges: flowData.edges || {}
    }
    
    const saveData = {
      title: flowTitle.value,
      flow_data: normalizedFlowData
    }

    console.log('保存的流程图数据:', saveData)

    let response
    if (flowchartId) {
      // 更新现有流程图
      console.log('更新现有流程图:', flowchartId)
      response = await request.put(`/api/flowcharts/${flowchartId}`, saveData)
    } else {
      // 创建新流程图
      console.log('创建新流程图:', saveData)
      response = await request.post('/api/flowcharts', saveData)
      console.log('创建成功，响应:', response)
      // 保存成功后，跳转到编辑页面
      if (response.data && response.data.id) {
        console.log('跳转到编辑页面:', `/flowcharts/${response.data.id}`)
        router.push(`/flowcharts/${response.data.id}`)
      } else {
        console.error('创建流程图失败，响应中没有id:', response)
        ElMessage.error('创建流程图失败，响应格式不正确')
        return { success: false, message: '创建流程图失败' }
      }
    }

    console.log('保存成功:', response)
    ElMessage.success('保存成功')
    return { success: true, message: '保存成功' }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
    return { success: false, message: '保存失败' }
  }
}

async function handleSave() {
  if (flowEditor.value) {
    await flowEditor.value.save()
  }
}

function handleShare() {
  shareDialogVisible.value = true
  shareUrl.value = ''
}

function handleShareFlowchart(id) {
  handleShare()
}

async function confirmShare() {
  if (!flowchartId) return

  sharing.value = true
  try {
    const response = await request.post(`/api/flowcharts/${flowchartId}/share`, {
      days: 7
    })

    shareUrl.value = `${window.location.origin}${response.share_url}`
    ElMessage.success('分享链接已生成')
  } catch (error) {
    console.error('分享失败:', error)
    ElMessage.error('分享失败')
  } finally {
    sharing.value = false
  }
}

function copyShareUrl() {
  navigator.clipboard.writeText(shareUrl.value)
  ElMessage.success('链接已复制到剪贴板')
}

async function handleExportFlowchart(imageData, format = 'svg') {
  try {
    if (imageData) {
      const link = document.createElement('a')
      link.download = `${flowTitle.value || 'flowchart'}.${format}`
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

onMounted(() => {
  console.log('FlowchartEditor组件挂载，isNew:', props.isNew, 'flowchartId:', flowchartId)
  if (!props.isNew && flowchartId) {
    console.log('加载流程图数据...')
    loadFlowchart()
  } else {
    console.log('新流程图，跳过加载')
  }
})
</script>

<style scoped>
.flowchart-editor-page {
  padding: 20px;
  height: calc(100vh - 80px);
}

.flowchart-editor-page :deep(.el-card) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.flowchart-editor-page :deep(.el-card__body) {
  flex: 1;
  overflow: hidden;
  padding: 0;
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

.share-url-container p {
  margin: 10px 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
