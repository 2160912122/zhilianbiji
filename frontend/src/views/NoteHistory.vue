<template>
  <div class="container">
    <h1>笔记版本历史</h1>
    <div class="actions">
      <router-link :to="`/notes/${noteId}`" class="btn btn-secondary">返回笔记</router-link>
    </div>
    
    <div v-if="versions.length > 0">
      <div 
        v-for="version in versions" 
        :key="version.id" 
        class="version-item"
      >
        <div class="version-header">
          <h3>版本 {{ version.id }}</h3>
          <div class="version-actions">
            <button class="btn btn-outline" @click="viewVersion(version.id)">查看</button>
            <button class="btn btn-primary" @click="rollbackToVersion(version.id)">回滚到此版本</button>
          </div>
        </div>
        <div class="version-meta">
          <span class="version-date">{{ formatDate(version.updated_at) }}</span>
          <span class="version-author">作者: {{ version.updater.username }}</span>
        </div>
        <div class="version-content-preview">{{ getContentPreview(version.content) }}</div>
      </div>
    </div>
    <div v-else>
      <p>没有版本历史记录</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { noteService } from '../services/note.js'

const route = useRoute()
const router = useRouter()
const noteId = route.params.id
const versions = ref([])

onMounted(() => {
  loadVersions()
})

async function loadVersions() {
  try {
    versions.value = await noteService.getNoteVersions(noteId)
  } catch (error) {
    console.error('加载版本历史失败:', error)
    alert('加载版本历史失败')
  }
}

function viewVersion(versionId) {
  router.push(`/notes/${noteId}/versions/${versionId}`)
}

async function rollbackToVersion(versionId) {
  if (confirm('确定要回滚到这个版本吗？当前版本的内容将被覆盖。')) {
    try {
      await noteService.rollbackNoteVersion(noteId, versionId)
      router.push(`/notes/${noteId}`)
    } catch (error) {
      console.error('回滚版本失败:', error)
      alert('回滚版本失败')
    }
  }
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleString()
}

function getContentPreview(content) {
  const maxLength = 100
  return content.length > maxLength ? content.substring(0, maxLength) + '...' : content
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

.version-item {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  background-color: white;
}

.version-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.version-header h3 {
  margin: 0;
}

.version-actions {
  display: flex;
  gap: 10px;
}

.version-meta {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
  font-size: 14px;
  color: #666;
}

.version-content-preview {
  background-color: #f9f9f9;
  padding: 10px;
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.4;
  color: #333;
}
</style>