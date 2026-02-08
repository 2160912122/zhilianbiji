<template>
  <div class="tables-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>表格列表</span>
          <div class="header-buttons">
            <el-button type="primary" @click="$router.push('/tables/new')">
              <el-icon><Plus /></el-icon>
              新建表格
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="tables" style="width: 100%">
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column label="行列数" width="120">
          <template #default="{ row }">
            {{ (row.rows?.length || 0) }} × {{ (row.columns?.length || 0) }}
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="editTable(row.id)">编辑</el-button>
            <el-button link type="danger" @click="deleteTable(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { tableAPI } from '@/api/editor'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const tables = ref([])

async function loadTables() {
  try {
    const result = await tableAPI.getList()
    tables.value = result.data || []
  } catch (error) {
    console.error('Load tables error:', error)
    tables.value = []
  }
}

function editTable(id) {
  router.push(`/tables/${id}`)
}

async function deleteTable(id) {
  try {
    await ElMessageBox.confirm('确定要删除这个表格吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await tableAPI.delete(id)
    ElMessage.success('删除成功')
    loadTables()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete table error:', error)
    }
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadTables()
})
</script>

<style scoped>
.tables-page {
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
