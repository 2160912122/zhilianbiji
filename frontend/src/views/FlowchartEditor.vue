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
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back, Check, Share } from '@element-plus/icons-vue'
import request from '@/utils/request'
import FlowEditor from '@/components/FlowEditor.vue'

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

async function loadFlowchart() {
  if (props.isNew) return
  
  try {
    const response = await request.get(`/api/flowcharts/${flowchartId}`)

    flowTitle.value = response.flowchart.title
    graphData.value = { nodes: {}, edges: {} }

    if (response.flowchart.flow_data) {
      graphData.value = JSON.parse(JSON.stringify(response.flowchart.flow_data))
    }
  } catch (error) {
    console.error('加载流程图失败:', error)
    ElMessage.error('加载流程图失败')
  }
}

async function handleTitleChange(newTitle) {
  if (!newTitle) return

  try {
    await request.put(`/api/flowcharts/${flowchartId}`, {
      title: newTitle
    })

    ElMessage.success('标题更新成功')
  } catch (error) {
    console.error('标题更新失败:', error)
    ElMessage.error('标题更新失败')
  }
}

async function handleSaveFlowchart(flowData) {
  try {
    const saveData = {
      title: flowTitle.value,
      flow_data: {
        nodes: flowData.nodes || {},
        edges: flowData.edges || {}
      }
    }

    let response
    if (flowchartId) {
      // 更新现有流程图
      response = await request.put(`/api/flowcharts/${flowchartId}`, saveData)
    } else {
      // 创建新流程图
      response = await request.post('/api/flowcharts', saveData)
      // 保存成功后，跳转到编辑页面
      router.push(`/flowcharts/${response.flowchart.id}`)
    }

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
  loadFlowchart()
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
