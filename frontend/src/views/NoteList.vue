<template>
  <div class="container">
    <h1>我的笔记</h1>
    <div class="actions">
      <router-link to="/notes/create" class="btn btn-primary">创建笔记</router-link>
    </div>
    
    <div class="filter-section">
      <select v-model="selectedCategory" class="form-control">
        <option value="">所有分类</option>
        <option v-for="category in categories" :key="category.id" :value="category.id">
          {{ category.name }}
        </option>
      </select>
      
      <div class="search-container">
        <input 
          type="text" 
          v-model="searchKeyword" 
          placeholder="搜索笔记..." 
          class="form-control search-input"
        />
      </div>
    </div>
    
    <div class="notes-grid">
      <div 
        v-for="note in filteredNotes" 
        :key="note.id" 
        class="note-card"
        @click="viewNote(note.id)"
      >
        <h3>{{ note.title }}</h3>
        <p class="note-preview">{{ note.content }}</p>
        <div class="note-meta">
          <span class="note-category">{{ getCategoryName(note.category_id) }}</span>
          <span class="note-type">{{ note.type === 'markdown' ? 'Markdown' : '富文本' }}</span>
          <span class="note-date">{{ formatDate(note.created_at) }}</span>
        </div>
      </div>
    </div>
    
    <div v-if="filteredNotes.length === 0" class="empty-state">
      <p>没有找到笔记</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { noteService } from '../services/note.js'
import { categoryService } from '../services/category.js'

const router = useRouter()
const notes = ref([])
const categories = ref([])
const selectedCategory = ref('')
const searchKeyword = ref('')

onMounted(() => {
  loadNotes()
  loadCategories()
})

async function loadNotes() {
  try {
    notes.value = await noteService.getNotes()
  } catch (error) {
    console.error('加载笔记失败:', error)
  }
}

async function loadCategories() {
  try {
    categories.value = await categoryService.getCategories()
  } catch (error) {
    console.error('加载分类失败:', error)
  }
}

function viewNote(id) {
  router.push(`/notes/${id}`)
}

function getCategoryName(categoryId) {
  if (!categoryId) return '未分类'
  const category = categories.value.find(cat => cat.id === categoryId)
  return category ? category.name : '未分类'
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleString()
}



const filteredNotes = computed(() => {
  return notes.value.filter(note => {
    const matchesCategory = !selectedCategory.value || note.category_id === selectedCategory.value
    const matchesSearch = !searchKeyword.value || 
      (note.title && note.title.toLowerCase().includes(searchKeyword.value.toLowerCase()))
    return matchesCategory && matchesSearch
  })
})
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  margin-bottom: 20px;
}

.actions {
  margin-bottom: 20px;
}

.filter-section {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.form-control {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  flex: 1;
  max-width: 300px;
}

.search-container {
  display: flex;
  gap: 0;
}

.search-input {
  max-width: 200px;
}

.notes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.note-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: box-shadow 0.3s ease;
  background-color: white;
}

.note-card:hover {
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.note-card h3 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
}

.note-preview {
  color: #666;
  margin-bottom: 10px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.note-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #999;
}

.note-category {
  background-color: #f0f0f0;
  padding: 2px 8px;
  border-radius: 4px;
}

.note-type {
  background-color: #e3f2fd;
  color: #1565c0;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
}

.empty-state {
  text-align: center;
  padding: 50px;
  color: #999;
}
</style>