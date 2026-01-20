<template>
  <div class="container">
    <h1>分类管理</h1>
    <div class="actions">
      <router-link to="/notes" class="btn btn-secondary">返回笔记</router-link>
    </div>
    
    <div class="category-form">
      <h2>创建新分类</h2>
      <div class="form-group">
        <input 
          type="text" 
          v-model="newCategoryName" 
          class="form-control"
          placeholder="输入分类名称"
        />
      </div>
      <button class="btn btn-primary" @click="createCategory">创建分类</button>
    </div>
    
    <div class="categories-list">
      <h2>现有分类</h2>
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>名称</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="category in categories" :key="category.id">
            <td>{{ category.id }}</td>
            <td>{{ category.name }}</td>
            <td>{{ formatDate(category.created_at) }}</td>
            <td>
              <button class="btn btn-danger" @click="deleteCategory(category.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { categoryService } from '../services/category.js'

const categories = ref([])
const newCategoryName = ref('')

onMounted(() => {
  loadCategories()
})

async function loadCategories() {
  try {
    categories.value = await categoryService.getCategories()
  } catch (error) {
    console.error('加载分类失败:', error)
    alert('加载分类失败')
  }
}

async function createCategory() {
  if (!newCategoryName.value.trim()) {
    alert('分类名称不能为空')
    return
  }
  
  try {
    await categoryService.createCategory({ name: newCategoryName.value.trim() })
    newCategoryName.value = ''
    loadCategories()
    alert('分类创建成功')
  } catch (error) {
    console.error('创建分类失败:', error)
    alert('创建分类失败')
  }
}

async function deleteCategory(categoryId) {
  if (confirm('确定要删除这个分类吗？')) {
    try {
      await categoryService.deleteCategory(categoryId)
      loadCategories()
      alert('分类删除成功')
    } catch (error) {
      console.error('删除分类失败:', error)
      alert('删除分类失败')
    }
  }
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleString()
}
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.actions {
  margin-bottom: 20px;
}

.category-form {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.category-form h2 {
  margin-top: 0;
  margin-bottom: 15px;
}

.form-group {
  margin-bottom: 15px;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.categories-list h2 {
  margin-bottom: 15px;
}

.table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.table th,
.table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.table th {
  background-color: #f5f5f5;
  font-weight: bold;
  color: #333;
}
</style>