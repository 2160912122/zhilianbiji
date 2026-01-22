<template>
  <div class="tags-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>标签管理</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            新建标签
          </el-button>
        </div>
      </template>
      
      <el-table :data="tags" style="width: 100%">
        <el-table-column prop="name" label="标签名称" min-width="200">
          <template #default="{ row }">
            <el-tag>{{ row.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="danger" @click="deleteTag(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-dialog
      v-model="dialogVisible"
      title="新建标签"
      width="500px"
    >
      <el-form :model="form" label-width="80px">
        <el-form-item label="标签名称">
          <el-input v-model="form.name" placeholder="请输入标签名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { tagAPI } from '@/api/common'
import { ElMessage, ElMessageBox } from 'element-plus'

const tags = ref([])
const dialogVisible = ref(false)
const form = ref({
  name: ''
})

async function loadTags() {
  try {
    tags.value = await tagAPI.getList()
  } catch (error) {
    console.error('Load tags error:', error)
  }
}

function showCreateDialog() {
  form.value = { name: '' }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.value.name.trim()) {
    ElMessage.warning('请输入标签名称')
    return
  }
  
  try {
    await tagAPI.create({ name: form.value.name })
    ElMessage.success('创建成功')
    dialogVisible.value = false
    loadTags()
  } catch (error) {
    console.error('Submit tag error:', error)
    ElMessage.error('创建失败')
  }
}

async function deleteTag(id) {
  try {
    await ElMessageBox.confirm('确定要删除这个标签吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await tagAPI.delete(id)
    ElMessage.success('删除成功')
    loadTags()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete tag error:', error)
    }
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadTags()
})
</script>

<style scoped>
.tags-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
