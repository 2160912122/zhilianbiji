<template>
  <div class="knowledge-graphs-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>知识图谱列表</span>
          <div class="header-buttons">
            <el-button type="primary" @click="createGraph">
              <el-icon><Plus /></el-icon>
              新建图谱
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索图谱名称或描述"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      
      <el-table :data="graphs" style="width: 100%">
        <el-table-column prop="name" label="名称" min-width="200" />
        <el-table-column prop="description" label="描述" min-width="300" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="editGraph(row.id)">编辑</el-button>
            <el-button link type="warning" @click="shareGraph(row.id)">分享</el-button>
            <el-button link type="danger" @click="deleteGraph(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <ShareDialog
      v-model:visible="shareDialogVisible"
      :resource-id="currentGraphId"
      resource-type="knowledge_graph"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import ShareDialog from '@/components/ShareDialog.vue'

const router = useRouter()

const graphs = ref([])
const searchQuery = ref('')
const shareDialogVisible = ref(false)
const currentGraphId = ref(null)

let searchTimer = null

async function loadGraphs() {
  try {
    let url = '/api/knowledge-graphs'
    if (searchQuery.value) {
      url += `?search=${encodeURIComponent(searchQuery.value)}`
    }
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      }
    })
    const result = await response.json()
    
    if (result.code === 200 && Array.isArray(result.data)) {
      graphs.value = result.data
    } else {
      graphs.value = []
    }
  } catch (error) {
    console.error('Load graphs error:', error)
    graphs.value = []
  }
}

function handleSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    loadGraphs()
  }, 300)
}

function createGraph() {
  router.push('/knowledge-graphs/new')
}

function editGraph(id) {
  router.push(`/knowledge-graphs/${id}`)
}

function shareGraph(id) {
  currentGraphId.value = id
  shareDialogVisible.value = true
}

async function deleteGraph(id) {
  try {
    await ElMessageBox.confirm('确定要删除这个知识图谱吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const response = await fetch(`/api/knowledge-graphs/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      }
    })
    const result = await response.json()
    
    if (result.code === 200) {
      ElMessage.success('删除成功')
      loadGraphs()
    } else {
      ElMessage.error(result.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete graph error:', error)
    }
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadGraphs()
})
</script>

<style scoped>
.knowledge-graphs-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-buttons {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-bar {
  margin-bottom: 20px;
}

.search-bar .el-input {
  max-width: 500px;
}
</style>