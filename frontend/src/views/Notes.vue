<template>
  <div class="notes-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>笔记列表</span>
          <div class="header-buttons">
            <el-button type="primary" @click="$router.push('/notes/new')">
              <el-icon><Plus /></el-icon>
              新建笔记
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索笔记标题或内容"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select
          v-model="selectedCategory"
          placeholder="选择分类"
          clearable
          @change="loadNotes"
        >
          <el-option
            v-for="cat in categories"
            :key="cat.id"
            :label="cat.name"
            :value="cat.id"
          />
        </el-select>
        <el-select
          v-model="selectedType"
          placeholder="选择类型"
          clearable
          @change="loadNotes"
        >
          <el-option label="富文本" value="richtext" />
          <el-option label="Markdown" value="markdown" />
        </el-select>
      </div>
      
      <el-table :data="notes" style="width: 100%">
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'richtext' ? 'primary' : 'success'">
              {{ row.type === 'richtext' ? '富文本' : 'Markdown' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category_id" label="分类" width="120">
          <template #default="{ row }">
            {{ getCategoryName(row.category_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="editNote(row.id)">编辑</el-button>
            <el-button link type="danger" @click="deleteNote(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { noteAPI } from '@/api/note'
import { categoryAPI } from '@/api/common'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()

const notes = ref([])
const categories = ref([])
const searchQuery = ref('')
const selectedCategory = ref(null)
const selectedType = ref('')

let searchTimer = null

async function loadNotes() {
  try {
    const params = {}
    if (searchQuery.value) params.search = searchQuery.value
    if (selectedCategory.value) params.category_id = selectedCategory.value
    if (selectedType.value) params.type = selectedType.value
    
    const result = await noteAPI.getList(params)
    notes.value = result.data || []
  } catch (error) {
    console.error('Load notes error:', error)
    notes.value = []
  }
}

async function loadCategories() {
  try {
    const result = await categoryAPI.getList()
    categories.value = result.data || []
  } catch (error) {
    console.error('Load categories error:', error)
    categories.value = []
  }
}

function handleSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    loadNotes()
  }, 300)
}

function editNote(id) {
  router.push(`/notes/${id}`)
}

async function deleteNote(id) {
  try {
    await ElMessageBox.confirm('确定要删除这条笔记吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await noteAPI.delete(id)
    ElMessage.success('删除成功')
    loadNotes()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete note error:', error)
    }
  }
}

function getCategoryName(categoryId) {
  const category = categories.value.find(c => c.id === categoryId)
  return category ? category.name : '未分类'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadNotes()
  loadCategories()
})
</script>

<style scoped>
.notes-page {
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
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-bar .el-input {
  flex: 1;
}
</style>
