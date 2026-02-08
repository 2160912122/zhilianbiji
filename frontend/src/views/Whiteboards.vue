<template>
  <div class="whiteboards-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>白板列表</span>
          <div class="header-buttons">
            <el-button type="primary" @click="$router.push('/whiteboards/new')">
              <el-icon><Plus /></el-icon>
              新建白板
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="whiteboards" style="width: 100%">
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="room_key" label="房间号" width="150" />
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="editWhiteboard(row.id)">编辑</el-button>
            <el-button link type="danger" @click="deleteWhiteboard(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { whiteboardAPI } from '@/api/editor'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const whiteboards = ref([])

async function loadWhiteboards() {
  try {
    const result = await whiteboardAPI.getList()
    console.log('加载白板列表结果:', result)
    whiteboards.value = (result.code === 200 && Array.isArray(result.data)) ? result.data : []
  } catch (error) {
    console.error('Load whiteboards error:', error)
    whiteboards.value = []
  }
}

function editWhiteboard(id) {
  router.push(`/whiteboards/${id}`)
}

async function deleteWhiteboard(id) {
  try {
    await ElMessageBox.confirm('确定要删除这个白板吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const result = await whiteboardAPI.delete(id)
    console.log('删除白板结果:', result)
    
    if (result.code === 200) {
      ElMessage.success('删除成功')
      loadWhiteboards()
    } else {
      throw new Error(result.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete whiteboard error:', error)
      ElMessage.error('删除失败: ' + (error.message || '服务器错误'))
    }
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadWhiteboards()
})
</script>

<style scoped>
.whiteboards-page {
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
</style>
