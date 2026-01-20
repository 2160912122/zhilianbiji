<template>
  <div class="container">
    <h1>管理员面板</h1>
    <div class="actions">
      <router-link to="/notes" class="btn btn-secondary">返回笔记</router-link>
    </div>
    
    <div class="admin-sections">
      <div class="section">
        <h2>系统统计</h2>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ stats.total_users || 0 }}</div>
            <div class="stat-label">总用户数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.total_notes || 0 }}</div>
            <div class="stat-label">总笔记数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.total_categories || 0 }}</div>
            <div class="stat-label">总分类数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.total_tags || 0 }}</div>
            <div class="stat-label">总标签数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.total_shares || 0 }}</div>
            <div class="stat-label">总分享数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.recent_users || 0 }}</div>
            <div class="stat-label">最近7天新增用户</div>
          </div>
        </div>
      </div>
      
      <div class="section">
        <h2>用户管理</h2>
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>用户名</th>
              <th>角色</th>
              <th>创建时间</th>
              <th>笔记数</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.username }}</td>
              <td>{{ user.is_admin ? '管理员' : '普通用户' }}</td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td>{{ user.note_count || 0 }}</td>
              <td>
                <button 
                  class="btn btn-outline" 
                  @click="toggleAdmin(user.id)"
                >
                  {{ user.is_admin ? '撤销管理员' : '设为管理员' }}
                </button>
                <button class="btn btn-danger" @click="deleteUser(user.id)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="section">
        <h2>笔记管理</h2>
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>标题</th>
              <th>类型</th>
              <th>作者</th>
              <th>更新时间</th>
              <th>内容预览</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="note in notes" :key="note.id">
              <td>{{ note.id }}</td>
              <td>{{ note.title }}</td>
              <td>{{ note.type }}</td>
              <td>{{ note.username }}</td>
              <td>{{ formatDate(note.updated_at) }}</td>
              <td>{{ note.content_preview }}</td>
              <td>
                <button class="btn btn-danger" @click="deleteNote(note.id)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="section">
        <h2>系统工具</h2>
        <div class="system-tools">
          <button class="btn btn-warning" @click="cleanupSystem">清理过期分享链接</button>
          <div class="tool-info" v-if="cleanupResult">
            {{ cleanupResult }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const stats = ref({})
const users = ref([])
const notes = ref([])
const cleanupResult = ref('')

onMounted(() => {
  loadStats()
  loadUsers()
  loadNotes()
})

async function loadStats() {
  try {
    const response = await axios.get('/api/admin/stats')
    stats.value = response.data
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

async function loadUsers() {
  try {
    const response = await axios.get('/api/admin/users')
    users.value = response.data
  } catch (error) {
    console.error('加载用户列表失败:', error)
  }
}

async function loadNotes() {
  try {
    const response = await axios.get('/api/admin/notes')
    notes.value = response.data
  } catch (error) {
    console.error('加载笔记列表失败:', error)
  }
}

async function toggleAdmin(userId) {
  try {
    await axios.post(`/api/admin/users/${userId}/toggle_admin`)
    loadUsers()
  } catch (error) {
    console.error('切换管理员状态失败:', error)
    alert('切换管理员状态失败')
  }
}

async function deleteUser(userId) {
  if (confirm('确定要删除这个用户吗？')) {
    try {
      await axios.delete(`/api/admin/users/${userId}`)
      loadUsers()
      alert('用户删除成功')
    } catch (error) {
      console.error('删除用户失败:', error)
      alert('删除用户失败')
    }
  }
}

async function deleteNote(noteId) {
  if (confirm('确定要删除这个笔记吗？')) {
    try {
      await axios.delete(`/api/admin/notes/${noteId}`)
      loadNotes()
      alert('笔记删除成功')
    } catch (error) {
      console.error('删除笔记失败:', error)
      alert('删除笔记失败')
    }
  }
}

async function cleanupSystem() {
  try {
    const response = await axios.post('/api/admin/cleanup')
    cleanupResult.value = response.data.message
    // 重新加载统计数据
    loadStats()
    setTimeout(() => {
      cleanupResult.value = ''
    }, 3000)
  } catch (error) {
    console.error('系统清理失败:', error)
    alert('系统清理失败')
  }
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleString()
}
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.actions {
  margin-bottom: 20px;
}

.admin-sections {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.section {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.section h2 {
  margin-top: 0;
  margin-bottom: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.system-tools {
  display: flex;
  align-items: center;
  gap: 15px;
}

.tool-info {
  color: green;
  font-weight: bold;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

.table {
  width: 100%;
  border-collapse: collapse;
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

.btn {
  margin-right: 5px;
}

.section h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
}
</style>