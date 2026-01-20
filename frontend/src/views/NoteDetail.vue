<template>
  <div class="container">
    <div class="actions">
      <router-link to="/notes" class="btn btn-secondary">返回列表</router-link>
      <button class="btn btn-primary" @click="editNote">编辑</button>
      <button class="btn btn-danger" @click="deleteNote">删除</button>
    </div>
    
    <div class="note-detail" v-if="note">
      <h1>{{ note.title }}</h1>
      <div class="note-meta">
        <span class="note-category">{{ getCategoryName(note.category_id) }}</span>
        <span class="note-date">{{ formatDate(note.created_at) }}</span>
        <span class="note-updated">更新于: {{ formatDate(note.updated_at) }}</span>
      </div>
      
      <div class="note-tags">
        <span v-for="tag in note.tags" :key="tag.id" class="tag">
          {{ tag.name }}
        </span>
      </div>
      
      <div class="note-content" v-html="renderContent(note.content)"></div>
      
      <div class="note-actions">
        <button class="btn btn-outline" @click="viewHistory">版本历史</button>
        <button class="btn btn-outline" @click="shareNote">分享笔记</button>
        <button class="btn btn-outline" @click="exportNote('markdown')">导出Markdown</button>
        <button class="btn btn-outline" @click="exportNote('html')">导出HTML</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { noteService } from '../services/note.js'
import { categoryService } from '../services/category.js'
import { marked } from 'marked'

const route = useRoute()
const router = useRouter()
const note = ref(null)
const categories = ref([])

onMounted(() => {
  loadNote()
  loadCategories()
})

async function loadNote() {
  try {
    const noteId = route.params.id
    note.value = await noteService.getNote(noteId)
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

function editNote() {
  router.push(`/notes/${route.params.id}/edit`)
}

async function deleteNote() {
  if (confirm('确定要删除这篇笔记吗？')) {
    try {
      await noteService.deleteNote(route.params.id)
      router.push('/notes')
    } catch (error) {
      console.error('删除笔记失败:', error)
    }
  }
}

function viewHistory() {
  router.push(`/notes/${route.params.id}/history`)
}

function shareNote() {
  router.push(`/notes/${route.params.id}/share`)
}

async function exportNote(format) {
  try {
    const response = await noteService.exportNote(route.params.id, format)
    const blob = new Blob([response.data], { type: response.headers['content-type'] })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${note.value.title}.${format}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('导出笔记失败:', error)
  }
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

function renderContent(content) {
  if (!note.value) return '';
  
  if (note.value.type === 'markdown') {
    // 使用marked库进行完整的Markdown渲染
    return marked(content);
  } else {
    // 富文本类型直接显示内容
    return content;
  }
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

.btn {
  margin-right: 10px;
}

.note-detail {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.note-detail h1 {
  margin-top: 0;
  margin-bottom: 10px;
}

.note-meta {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
  font-size: 14px;
  color: #666;
}

.note-category {
  background-color: #f0f0f0;
  padding: 2px 8px;
  border-radius: 4px;
}

.note-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.tag {
  background-color: #e3f2fd;
  color: #1565c0;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.note-content {
  line-height: 1.6;
  margin-bottom: 30px;
  white-space: pre-wrap;
}

.note-actions {
  display: flex;
  gap: 10px;
  border-top: 1px solid #eee;
  padding-top: 20px;
}

.btn-outline {
  border: 1px solid #ddd;
  background-color: white;
  color: #333;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.btn-outline:hover {
  background-color: #f5f5f5;
}
</style>