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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const isLoggedIn = ref(false)
const error = ref(false)
const errorIcon = ref('error')
const errorTitle = ref('')
const errorMessage = ref('')
const contentType = ref('')
const contentId = ref(null)
const sharePermission = ref('view')
const data = ref(null)

onMounted(async () => {
  const shareToken = route.params.token
  
  if (!shareToken) {
    showError('error', '无效的分享链接', '缺少分享令牌')
    return
  }
  
  const currentToken = localStorage.getItem('token')
  if (!currentToken) {
    localStorage.setItem('shareToken', shareToken)
    router.push('/login')
    return
  }
  
  isLoggedIn.value = true
  
  try {
    const response = await fetch(`/api/share/${shareToken}`)
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
    } else if (responseData.type === 'table_document') {
      contentId.value = responseData.table.id
    } else if (responseData.type === 'whiteboard') {
      contentId.value = responseData.whiteboard.id
    } else if (responseData.type === 'knowledge_graph') {
      contentId.value = responseData.knowledge_graph.id
    }
    
    sharePermission.value = responseData.permission || 'view'
    loading.value = false
    
    openInEditor()
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

function goToLogin() {
  router.push('/login')
}

function goToRegister() {
  router.push('/register')
}

function openInEditor() {
  const routes = {
    note: `/notes/${contentId.value}`,
    flowchart: `/flowcharts/${contentId.value}`,
    mindmap: `/mindmaps/${contentId.value}`,
    table_document: `/tables/${contentId.value}`,
    whiteboard: `/whiteboards/${contentId.value}`,
    knowledge_graph: `/knowledge-graphs/${contentId.value}`
  }
  
  const targetRoute = routes[contentType.value]
  if (targetRoute) {
    router.push(targetRoute)
  } else {
    ElMessage.error('不支持的内容类型')
  }
}
</script>

<style scoped>
.shared-content {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.login-prompt {
  text-align: center;
  padding: 40px;
}

.login-prompt h2 {
  margin-bottom: 16px;
  color: #303133;
}

.login-prompt p {
  color: #606266;
  margin-bottom: 24px;
}

.auth-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.auth-buttons .el-button {
  width: 120px;
}

.shared-content-preview {
  padding: 20px;
}

.preview-content {
  text-align: center;
  padding: 40px;
}

.preview-content h2 {
  margin-bottom: 16px;
  color: #303133;
  font-size: 24px;
}

.preview-content .description {
  color: #606266;
  margin-bottom: 24px;
  font-size: 14px;
}

.meta-info {
  display: flex;
  justify-content: center;
  gap: 12px;
  align-items: center;
  margin-bottom: 32px;
}

.collab-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #67c23a;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  justify-content: center;
}
</style>
