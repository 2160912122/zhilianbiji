<template>
  <div class="categories-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>分类管理</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            新建分类
          </el-button>
        </div>
      </template>
      
      <el-table :data="categories" style="width: 100%">
        <el-table-column prop="name" label="分类名称" min-width="200" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="editCategory(row)">编辑</el-button>
            <el-button link type="danger" @click="deleteCategory(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑分类' : '新建分类'"
      width="500px"
    >
      <el-form :model="form" label-width="80px">
        <el-form-item label="分类名称">
          <el-input v-model="form.name" placeholder="请输入分类名称" />
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
import { categoryAPI } from '@/api/common'
import { ElMessage, ElMessageBox } from 'element-plus'

const categories = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const form = ref({
  id: null,
  name: ''
})

async function loadCategories() {
  try {
    categories.value = await categoryAPI.getList()
  } catch (error) {
    console.error('Load categories error:', error)
  }
}

function showCreateDialog() {
  isEdit.value = false
  form.value = { id: null, name: '' }
  dialogVisible.value = true
}

function editCategory(category) {
  isEdit.value = true
  form.value = { id: category.id, name: category.name }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.value.name.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }
  
  try {
    if (isEdit.value) {
      await categoryAPI.update(form.value.id, { name: form.value.name })
      ElMessage.success('更新成功')
    } else {
      await categoryAPI.create({ name: form.value.name })
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadCategories()
  } catch (error) {
    console.error('Submit category error:', error)
    ElMessage.error('操作失败')
  }
}

async function deleteCategory(id) {
  try {
    await ElMessageBox.confirm('确定要删除这个分类吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await categoryAPI.delete(id)
    ElMessage.success('删除成功')
    loadCategories()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete category error:', error)
    }
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.categories-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
