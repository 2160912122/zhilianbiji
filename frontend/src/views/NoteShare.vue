<template>
  <div class="container">
    <h1>分享笔记</h1>
    <div class="actions">
      <router-link :to="`/notes/${noteId}`" class="btn btn-secondary">返回笔记</router-link>
    </div>
    
    <div class="share-form">
      <div class="form-group">
        <label for="permission">权限</label>
        <select v-model="shareData.permission" id="permission" class="form-control">
          <option value="view">只读</option>
          <option value="edit">可编辑</option>
        </select>
      </div>
      
      <div class="form-group">
        <label for="expireAt">过期时间</label>
        <select v-model="shareData.expireAt" id="expireAt" class="form-control">
          <option value="">永不过期</option>
          <option value="1m">1分钟</option>
          <option value="1d">1天</option>
          <option value="7d">7天</option>
          <option value="30d">30天</option>
        </select>
      </div>
      
      <div class="form-actions">
        <button class="btn btn-primary" @click="createShareLink">创建分享链接</button>
      </div>
    </div>
    
    <div v-if="shareLink" class="share-result">
      <h2>分享链接已创建</h2>
      <div class="share-link">
        <input type="text" v-model="shareLink" readonly class="form-control" />
        <button class="btn btn-secondary" @click="copyLink">复制链接</button>
      </div>
      <p class="share-info">此链接有效期至: {{ shareExpireDate || '永久' }}</p>
    </div>
    
    <div class="existing-shares" v-if="existingShares.length > 0">
      <h2>已存在的分享</h2>
      <table class="table">
        <thead>
          <tr>
            <th>链接</th>
            <th>权限</th>
            <th>创建时间</th>
            <th>过期时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="share in existingShares" :key="share.token">
            <td class="share-link-cell">
              <input type="text" :value="share.share_url" readonly class="form-control" />
            </td>
            <td>{{ share.permission === 'view' ? '只读' : '可编辑' }}</td>
            <td>{{ formatDate(share.created_at) }}</td>
            <td>{{ share.expire_at ? formatDate(share.expire_at) : '永久' }}</td>
            <td>
              <button class="btn btn-danger" @click="deleteShare(share.token)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { noteService } from '../services/note.js'

const route = useRoute()
const noteId = route.params.id
const shareData = ref({
  permission: 'view',
  expireAt: ''
})
const shareLink = ref('')
const shareExpireDate = ref('')
const existingShares = ref([])
const loading = ref(false)
const error = ref(null)

// 计算分享URL - 现在我们直接使用API返回的share_url
function getShareUrl(shareKey) {
  return window.location.origin + `/share/${shareKey}`
}

// 格式化日期
function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  // 确保将UTC时间转换为本地时间显示
  return date.toLocaleString()
}

// 加载现有分享
async function loadExistingShares() {
  loading.value = true
  error.value = null

  try {
    const shares = await noteService.getShares(noteId)
    existingShares.value = shares
  } catch (err) {
    error.value = '获取分享链接失败：' + (err.response?.data?.error || err.message)
    console.error('获取分享链接失败:', err)
  } finally {
    loading.value = false
  }
}

// 创建分享链接
async function createShareLink() {
  loading.value = true
  error.value = null

  try {
    // 计算实际的过期日期
    let expireAt = null
    if (shareData.value.expireAt) {
      const expireDate = new Date()
      if (shareData.value.expireAt === '1m') {
        expireDate.setMinutes(expireDate.getMinutes() + 1)
      } else if (shareData.value.expireAt === '1d') {
        expireDate.setDate(expireDate.getDate() + 1)
      } else if (shareData.value.expireAt === '7d') {
        expireDate.setDate(expireDate.getDate() + 7)
      } else if (shareData.value.expireAt === '30d') {
        expireDate.setDate(expireDate.getDate() + 30)
      }
      // 使用UTC时间以避免时区问题
      expireAt = new Date(expireDate.getTime() - expireDate.getTimezoneOffset() * 60000).toISOString().slice(0, -1)
      // 保存UTC时间字符串，然后使用formatDate函数转换为本地时间显示
      shareExpireDate.value = formatDate(expireAt)
    } else {
      shareExpireDate.value = ''
    }

    const response = await noteService.createShare(noteId, shareData.value.permission, expireAt)
    shareLink.value = response.share_url
    
    // 重新加载现有分享
    await loadExistingShares()
  } catch (err) {
    error.value = '创建分享链接失败：' + (err.response?.data?.error || err.message)
    console.error('创建分享链接失败:', err)
    alert('创建分享链接失败')
  } finally {
    loading.value = false
  }
}

// 复制链接到剪贴板
async function copyLink() {
  try {
    await navigator.clipboard.writeText(shareLink.value)
    alert('链接已复制到剪贴板')
  } catch (err) {
    console.error('复制链接失败:', err)
    alert('复制链接失败')
  }
}

// 删除分享
async function deleteShare(token) {
  try {
    await noteService.deleteShare(token)
    await loadExistingShares()
    alert('分享已删除')
  } catch (err) {
    error.value = '删除分享失败：' + (err.response?.data?.error || err.message)
    console.error('删除分享失败:', err)
    alert('删除分享失败')
  }
}

onMounted(() => {
  loadExistingShares()
})
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

.share-form {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.form-actions {
  margin-top: 30px;
}

.share-result {
  background-color: #e8f5e8;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
}

.share-result h2 {
  margin-top: 0;
  color: #2e7d32;
}

.share-link {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.share-info {
  color: #43a047;
  font-size: 14px;
}

.existing-shares h2 {
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

.share-link-cell {
  max-width: 300px;
}
</style>