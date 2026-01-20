<template>
  <div class="container">
    <h1>笔记版本详情</h1>
    <div class="actions">
      <router-link :to="`/notes/${noteId}/history`" class="btn btn-secondary">返回历史</router-link>
      <button class="btn btn-primary" @click="rollbackToVersion">回滚到此版本</button>
    </div>
    
    <div class="version-detail" v-if="version">
      <div class="version-header">
        <h2>版本 {{ version.id }}</h2>
        <div class="version-meta">
          <span class="version-date">{{ formatDate(version.updated_at) }}</span>
          <span class="version-author">作者: {{ version.updater.username }}</span>
        </div>
      </div>
      
      <div class="version-content">
        <h3>标题</h3>
        <p>{{ version.title }}</p>
        
        <h3>内容</h3>
        <div class="content-display">
          {{ version.content }}
        </div>
      </div>
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
const versionId = route.params.versionId
const version = ref(null)

onMounted(() => {
  loadVersion()
})

async function loadVersion() {
  try {
    // 由于我们没有单独获取版本详情的API，这里简单地加载所有版本然后找到对应的版本
    const versions = await noteService.getNoteVersions(noteId)
    version.value = versions.find(v => v.id === parseInt(versionId))
  } catch (error) {
    console.error('加载版本详情失败:', error)
    alert('加载版本详情失败')
  }
}

async function rollbackToVersion() {
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

.version-detail {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.version-header {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.version-header h2 {
  margin-top: 0;
  margin-bottom: 10px;
}

.version-meta {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: #666;
}

.version-content h3 {
  margin-top: 20px;
  margin-bottom: 10px;
  font-size: 18px;
}

.version-content p {
  font-size: 16px;
  margin-bottom: 20px;
}

.content-display {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  white-space: pre-wrap;
}
</style>