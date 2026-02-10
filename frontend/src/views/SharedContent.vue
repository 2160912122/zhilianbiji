<template>
  <div class="shared-content">
    <el-card v-if="loading" style="max-width: 600px; margin: 50px auto;">
      <el-empty description="加载中..." />
    </el-card>
    
    <el-card v-else-if="error" style="max-width: 600px; margin: 50px auto;">
      <el-result :icon="errorIcon" :title="errorTitle" :sub-title="errorMessage">
        <template #extra>
          <el-button type="primary" @click="goHome">返回首页</el-button>
        </template>
      </el-result>
    </el-card>
    
    <div v-else-if="contentType === 'note'" class="shared-note">
      <NoteEditor :note-id="contentId" :is-shared="true" :share-permission="sharePermission" :shared-note="data.note" />
    </div>
    
    <div v-else-if="contentType === 'flowchart'" class="shared-flowchart">
      <FlowchartEditor :flowchart-id="contentId" :is-shared="true" :share-permission="sharePermission" :shared-flowchart="data.flowchart" />
    </div>
    
    <div v-else-if="contentType === 'mindmap'" class="shared-mindmap">
      <MindmapEditor :mindmap-id="contentId" :is-shared="true" :share-permission="sharePermission" :shared-mindmap="data.mindmap" />
    </div>
    
    <el-card v-else style="max-width: 600px; margin: 50px auto;">
      <el-result icon="warning" title="不支持的分享类型" sub-title="该分享链接指向的内容类型不支持">
        <template #extra>
          <el-button type="primary" @click="goHome">返回首页</el-button>
        </template>
      </el-result>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import NoteEditor from './NoteEditor.vue'
import FlowchartEditor from './FlowchartEditor.vue'
import MindmapEditor from './MindmapEditor.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const error = ref(false)
const errorIcon = ref('error')
const errorTitle = ref('')
const errorMessage = ref('')
const contentType = ref('')
const contentId = ref(null)
const sharePermission = ref('view')
const data = ref(null)

onMounted(async () => {
  const token = route.params.token
  
  if (!token) {
    showError('error', '无效的分享链接', '缺少分享令牌')
    return
  }
  
  try {
    const response = await fetch(`/api/share/${token}`)
    const responseData = await response.json()
    
    if (!response.ok) {
      showError('error', '分享链接无效', responseData.message || '无法访问分享的内容')
      return
    }
    
    // 检查响应格式是否正确
    if (!responseData.code || responseData.code !== 200) {
      showError('error', '分享链接无效', responseData.message || '无法访问分享的内容')
      return
    }
    
    data.value = responseData
    contentType.value = responseData.type
    
    if (responseData.type === 'note') {
      contentId.value = responseData.note.id
    } else if (responseData.type === 'flowchart') {
      contentId.value = responseData.flowchart.id
    } else if (responseData.type === 'mindmap') {
      contentId.value = responseData.mindmap.id
    }
    
    sharePermission.value = responseData.permission || 'view'
    loading.value = false
  } catch (err) {
    console.error('加载分享内容失败:', err)
    showError('error', '加载失败', '无法加载分享内容，请稍后重试')
  }
})

function showError(icon, title, message) {
  errorIcon.value = icon
  errorTitle.value = title
  errorMessage.value = message
  error.value = true
  loading.value = false
}

function goHome() {
  router.push('/login')
}
</script>

<style scoped>
.shared-content {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.shared-note,
.shared-flowchart,
.shared-mindmap {
  height: 100vh;
  background-color: #f5f5f5;
}
</style>
