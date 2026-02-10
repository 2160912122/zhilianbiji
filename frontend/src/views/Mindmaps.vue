<template>
  <div class="mindmaps-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>脑图列表</span>
          <div class="header-buttons">
            <el-button type="primary" @click="$router.push('/mindmaps/new')">
              <el-icon><Plus /></el-icon>
              新建脑图
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="mindmaps" style="width: 100%">
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="is_public" label="公开" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_public ? 'success' : 'info'">
              {{ row.is_public ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="editMindmap(row.id)">编辑</el-button>
            <el-button link type="danger" @click="deleteMindmap(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { mindmapAPI } from '@/api/editor'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const mindmaps = ref([])

async function loadMindmaps() {
  try {
    const result = await mindmapAPI.getList()
    mindmaps.value = result.data || []
  } catch (error) {
    console.error('Load mindmaps error:', error)
    mindmaps.value = []
  }
}

function editMindmap(id) {
  router.push(`/mindmaps/${id}`)
}

async function deleteMindmap(id) {
  try {
    await ElMessageBox.confirm('确定要删除这个脑图吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await mindmapAPI.delete(id)
    ElMessage.success('删除成功')
    loadMindmaps()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete mindmap error:', error)
    }
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadMindmaps()
})
</script>

<style scoped>
.mindmaps-page {
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
