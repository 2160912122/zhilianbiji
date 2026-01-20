<template>
  <Layout>
    <div class="admin-container">
      <div class="container">
        <h1 class="page-title">系统管理</h1>

        <!-- Statistics Grid -->
        <div class="stats-grid" id="stats-grid">
          <div class="stat-card">
            <div class="stat-icon"><i class="fa fa-users"></i></div>
            <div class="stat-number" id="user-count">{{ stats.total_users }}</div>
            <div class="stat-label">用户总数</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon"><i class="fa fa-table"></i></div>
            <div class="stat-number" id="table-count">{{ stats.total_tables }}</div>
            <div class="stat-label">表格文档</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon"><i class="fa fa-paint-brush"></i></div>
            <div class="stat-number" id="whiteboard-count">{{ stats.total_whiteboards }}</div>
            <div class="stat-label">白板文档</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon"><i class="fa fa-file-text"></i></div>
            <div class="stat-number" id="total-documents">{{ stats.total_documents }}</div>
            <div class="stat-label">总文档数</div>
          </div>
        </div>

        <!-- User Management -->
        <div class="card">
          <div class="card-header">
            <i class="fa fa-users"></i>
            <span>用户管理</span>
          </div>
          <div class="card-body">
            <div class="users-controls">
              <div class="search-box">
                <i class="fa fa-search"></i>
                <input type="text" v-model="searchQuery" placeholder="搜索用户名...">
              </div>
              <div class="filter-controls">
                <select v-model="roleFilter" class="role-filter">
                  <option value="">全部角色</option>
                  <option value="user">用户</option>
                  <option value="admin">管理员</option>
                </select>
              </div>
            </div>

            <div class="table-container">
              <table class="users-table">
                <thead>
                  <tr>
                    <th>用户名</th>
                    <th>邮箱</th>
                    <th>角色</th>
                    <th>注册时间</th>
                    <th>最后登录</th>
                    <th>状态</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="loadingUsers">
                    <td colspan="7" class="loading-center">
                      <div class="loading"></div>
                      <span>加载中...</span>
                    </td>
                  </tr>
                  <tr v-else-if="filteredUsers.length === 0">
                    <td colspan="7" class="empty-state">
                      <i class="fa fa-users"></i>
                      <p>暂无用户数据</p>
                    </td>
                  </tr>
                  <tr v-for="user in filteredUsers" :key="user.id">
                    <td>
                      <div class="user-info">
                        <i class="fa fa-user-circle" style="color: var(--text-tertiary);"></i>
                        <span>{{ user.username }}</span>
                      </div>
                    </td>
                    <td>{{ user.email }}</td>
                    <td>
                      <span class="role-badge" :class="user.role">
                        {{ user.role === 'admin' ? '管理员' : '用户' }}
                      </span>
                    </td>
                    <td>{{ formatDate(user.registered) }}</td>
                    <td>{{ user.lastLogin ? formatDate(user.lastLogin) : '从未登录' }}</td>
                    <td>
                      <span class="status-badge" :class="user.status">
                        {{ user.status === 'active' ? '正常' : '禁用' }}
                      </span>
                    </td>
                    <td class="actions-cell">
                      <div class="action-buttons">
                        <button class="btn btn-warning btn-sm" @click="editUser(user.id)" title="编辑用户">
                          <i class="fa fa-edit"></i>
                        </button>
                        <button class="btn btn-danger btn-sm" @click="deleteUser(user.id)" title="删除用户">
                          <i class="fa fa-trash"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- System Settings -->
        <div class="card">
          <div class="card-header">
            <i class="fa fa-cog"></i>
            <span>系统设置</span>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleSaveSettings" id="settings-form">
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label" for="default-share-expiry">默认分享有效期：</label>
                  <select id="default-share-expiry" v-model="settings.defaultShareExpiry" class="form-control">
                    <option value="1d">1天</option>
                    <option value="7d" selected>7天</option>
                    <option value="30d">30天</option>
                    <option value="never">永久</option>
                  </select>
                </div>
                <div class="form-group">
                  <label class="form-label" for="auto-save-interval">自动保存间隔（秒）：</label>
                  <input
                    type="number"
                    id="auto-save-interval"
                    v-model="settings.autoSaveInterval"
                    class="form-control"
                    min="10"
                    max="300"
                    step="10"
                  >
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label" for="max-file-size">最大文件大小（MB）：</label>
                  <input
                    type="number"
                    id="max-file-size"
                    v-model="settings.maxFileSize"
                    class="form-control"
                    min="1"
                    max="100"
                  >
                </div>
                <div class="form-group">
                  <label class="form-label" for="session-timeout">会话超时时间（分钟）：</label>
                  <input
                    type="number"
                    id="session-timeout"
                    v-model="settings.sessionTimeout"
                    class="form-control"
                    min="15"
                    max="1440"
                  >
                </div>
              </div>
              <div class="form-group">
                <label class="form-label" for="allowed-file-types">允许的文件类型：</label>
                <input
                  type="text"
                  id="allowed-file-types"
                  v-model="settings.allowedFileTypes"
                  class="form-control"
                  placeholder="用逗号分隔的文件扩展名"
                >
              </div>
              <button type="submit" class="btn btn-primary" id="save-settings" :disabled="savingSettings">
                <span v-if="!savingSettings">
                  <i class="fa fa-save"></i>
                  保存设置
                </span>
                <span v-else>
                  <div class="loading"></div>
                  <span>保存中...</span>
                </span>
              </button>
            </form>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="card">
          <div class="card-header">
            <i class="fa fa-history"></i>
            <span>最近活动</span>
          </div>
          <div class="card-body">
            <div class="table-container">
              <table class="activity-table">
                <thead>
                  <tr>
                    <th>时间</th>
                    <th>用户</th>
                    <th>操作</th>
                    <th>详情</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="loadingActivities">
                    <td colspan="4" class="loading-center">
                      <div class="loading"></div>
                      <span>加载中...</span>
                    </td>
                  </tr>
                  <tr v-else-if="activities.length === 0">
                    <td colspan="4" class="empty-state">
                      <i class="fa fa-info-circle"></i>
                      <p>暂无活动记录</p>
                    </td>
                  </tr>
                  <tr v-for="activity in activities" :key="activity.id">
                    <td>{{ formatDateTime(activity.timestamp) }}</td>
                    <td>{{ activity.user }}</td>
                    <td>
                      <span class="activity-type" :class="activity.type">
                        {{ activity.typeName }}
                      </span>
                    </td>
                    <td>{{ activity.details }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Toast -->
      <div class="toast" :class="{ show: showToast, [toastType]: true }">
        {{ toastMessage }}
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import Layout from '../components/Layout.vue'
import { adminAPI } from '../services/api'

// Reactive data
const loadingStats = ref(true)
const loadingUsers = ref(true)
const loadingActivities = ref(true)
const savingSettings = ref(false)
const searchQuery = ref('')
const roleFilter = ref('')
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('info') // info, success, error

const stats = reactive({
  total_users: 0,
  total_documents: 0,
  total_tables: 0,
  total_whiteboards: 0
})

const users = ref([])

const activities = ref([])

// 系统设置
const settings = reactive({
  defaultShareExpiry: '7d',
  autoSaveInterval: 30,
  maxFileSize: 10,
  sessionTimeout: 60,
  allowedFileTypes: '.csv,.xlsx,.pdf,.jpg,.png'
})

// Computed properties
const filteredUsers = computed(() => {
  let filtered = users.value
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(user => 
      user.username.toLowerCase().includes(query)
    )
  }
  
  // 角色过滤
  if (roleFilter.value) {
    filtered = filtered.filter(user => user.role === roleFilter.value)
  }
  
  return filtered
})

// Methods
const showToastMessage = (message, type = 'info') => {
  toastMessage.value = message
  toastType.value = type
  showToast.value = true
  
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

const fetchDashboardData = async () => {
  await Promise.all([
    fetchAdminStats(),
    fetchUsers(),
    fetchActivities()
  ])
}

const fetchAdminStats = async () => {
  loadingStats.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // 生成模拟统计数据
    const baseUsers = 156
    const baseTables = 342
    const baseWhiteboards = 89
    
    stats.total_users = baseUsers + Math.floor(Math.random() * 20)
    stats.total_tables = baseTables + Math.floor(Math.random() * 50)
    stats.total_whiteboards = baseWhiteboards + Math.floor(Math.random() * 15)
    stats.total_documents = stats.total_tables + stats.total_whiteboards + Math.floor(Math.random() * 65)
    
    // 添加数字动画
    animateNumbers()
  } catch (error) {
    console.error('获取统计数据失败:', error)
    showToastMessage('获取统计数据失败', 'error')
  } finally {
    loadingStats.value = false
  }
}

const animateNumbers = () => {
  const numberElements = document.querySelectorAll('.stat-number')
  
  numberElements.forEach(element => {
    const finalValue = parseInt(element.textContent)
    let currentValue = 0
    const increment = Math.ceil(finalValue / 30)
    
    const timer = setInterval(() => {
      currentValue += increment
      if (currentValue >= finalValue) {
        element.textContent = finalValue
        clearInterval(timer)
      } else {
        element.textContent = currentValue
      }
    }, 50)
  })
}

const fetchUsers = async () => {
  loadingUsers.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 生成模拟用户数据
    const usernames = ['demo', 'testuser', 'admin', 'alice', 'bob', 'charlie', 'diana', 'eve']
    
    users.value = usernames.map((username, index) => {
      const role = index < 6 ? 'user' : 'admin'
      const status = Math.random() > 0.2 ? 'active' : 'inactive'
      
      return {
        id: `user_${index + 1}`,
        username: username,
        email: `${username}@example.com`,
        role: role,
        status: status,
        registered: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString(),
        lastLogin: Math.random() > 0.3 ? new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString() : null,
        document_count: Math.floor(Math.random() * 20)
      }
    })
  } catch (error) {
    console.error('获取用户列表失败:', error)
    showToastMessage('获取用户列表失败', 'error')
  } finally {
    loadingUsers.value = false
  }
}

const fetchActivities = async () => {
  loadingActivities.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 600))
    
    // 生成模拟活动记录
    const activityTypes = [
      { type: 'login', typeName: '登录', user: 'demo', details: '用户登录系统' },
      { type: 'create', typeName: '创建', user: 'alice', details: '创建了新表格文档' },
      { type: 'share', typeName: '分享', user: 'bob', details: '分享了文档给用户' },
      { type: 'edit', typeName: '编辑', user: 'charlie', details: '编辑了表格内容' },
      { type: 'export', typeName: '导出', user: 'diana', details: '导出了CSV文件' }
    ]
    
    activities.value = activityTypes.map((activity, index) => ({
      id: `activity_${index + 1}`,
      ...activity,
      timestamp: new Date(Date.now() - (index + 1) * 3600000).toISOString()
    }))
  } catch (error) {
    console.error('获取活动记录失败:', error)
  } finally {
    loadingActivities.value = false
  }
}

const handleSaveSettings = async (e) => {
  e.preventDefault()
  
  savingSettings.value = true
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 保存设置到localStorage（实际项目中应该调用API）
    localStorage.setItem('system_settings', JSON.stringify(settings))
    
    showToastMessage('设置保存成功', 'success')
  } catch (error) {
    console.error('保存设置失败:', error)
    showToastMessage('保存设置失败', 'error')
  } finally {
    savingSettings.value = false
  }
}

const editUser = (userId) => {
  showToastMessage('用户编辑功能即将推出', 'info')
}

const deleteUser = (userId) => {
  if (confirm('确定要删除这个用户吗？此操作不可撤销。')) {
    showToastMessage('用户删除功能即将推出', 'info')
  }
}

const toggleUserRole = async (user) => {
  if (!confirm(`确定要将用户 "${user.username}" ${user.role === 'admin' ? '设为普通用户' : '设为管理员'} 吗？`)) {
    return
  }
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 更新本地数据
    const index = users.value.findIndex(u => u.id === user.id)
    if (index !== -1) {
      users.value[index].role = user.role === 'admin' ? 'user' : 'admin'
    }
    
    showToastMessage('角色更新成功', 'success')
  } catch (error) {
    console.error('更新用户角色失败:', error)
    showToastMessage('更新用户角色失败', 'error')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '从未登录'
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    if (hours === 0) {
      const minutes = Math.floor(diff / (1000 * 60))
      return minutes <= 1 ? '刚刚' : `${minutes}分钟前`
    }
    return `${hours}小时前`
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString()
  }
}

const formatDateTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString()
}

// Lifecycle hooks
onMounted(() => {
  fetchDashboardData()
  
  // 从localStorage加载设置（实际项目中应该从API获取）
  const savedSettings = localStorage.getItem('system_settings')
  if (savedSettings) {
    const parsedSettings = JSON.parse(savedSettings)
    Object.assign(settings, parsedSettings)
  }
})
</script>

<style scoped>
/* 全局变量 */
:root {
  --primary-color: #10b981;
  --primary-dark: #059669;
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-tertiary: #f1f5f9;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --text-tertiary: #94a3b8;
  --border-color: #e2e8f0;
  --error-color: #ef4444;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --radius: 8px;
  --radius-sm: 4px;
  --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.admin-container {
  width: 100%;
  min-height: calc(100vh - 64px);
  background-color: var(--bg-secondary);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 20px;
}

.page-title {
  margin: 0 0 24px;
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

/* Cards */
.card {
  background: var(--bg-primary);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  margin-bottom: 24px;
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.card-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
  font-weight: 600;
  font-size: 18px;
  background-color: var(--bg-tertiary);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-body {
  padding: 24px;
}

/* Statistics Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--bg-primary);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 24px;
  text-align: center;
  border: 1px solid var(--border-color);
  transition: var(--transition);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.stat-icon {
  font-size: 32px;
  margin-bottom: 12px;
  color: var(--primary-color);
}

.stat-number {
  font-size: 36px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 8px;
  line-height: 1;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
}

/* User Controls */
.users-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.search-box {
  position: relative;
  width: 300px;
}

.search-box i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
}

.search-box input {
  width: 100%;
  padding: 12px 16px 12px 40px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  font-size: 14px;
  transition: var(--transition);
  background-color: var(--bg-primary);
}

.search-box input:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.role-filter {
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  font-size: 14px;
  background-color: var(--bg-primary);
  cursor: pointer;
  transition: var(--transition);
}

.role-filter:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

/* Tables */
.table-container {
  overflow-x: auto;
  border-radius: var(--radius);
  border: 1px solid var(--border-color);
}

.users-table,
.activity-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg-primary);
}

.users-table th,
.users-table td,
.activity-table th,
.activity-table td {
  padding: 16px 20px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.users-table th,
.activity-table th {
  background-color: var(--bg-tertiary);
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
  position: sticky;
  top: 0;
  z-index: 10;
}

.users-table tr:hover,
.activity-table tr:hover {
  background-color: var(--bg-secondary);
}

.users-table tr:last-child td,
.activity-table tr:last-child td {
  border-bottom: none;
}

/* User Info */
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Badges */
.role-badge,
.status-badge,
.activity-type {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.role-badge.admin {
  background-color: #fef3c7;
  color: #92400e;
}

.role-badge.user {
  background-color: #dbeafe;
  color: #1e40af;
}

.status-badge.active {
  background-color: #d1fae5;
  color: #065f46;
}

.status-badge.inactive {
  background-color: #fee2e2;
  color: #991b1b;
}

.activity-type.login {
  background-color: #dbeafe;
  color: #1e40af;
}

.activity-type.create {
  background-color: #d1fae5;
  color: #065f46;
}

.activity-type.share {
  background-color: #fef3c7;
  color: #92400e;
}

.activity-type.edit {
  background-color: #e0e7ff;
  color: #3730a3;
}

.activity-type.export {
  background-color: #f3e8ff;
  color: #7c3aed;
}

/* Buttons */
.btn {
  padding: 10px 18px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background: var(--bg-primary);
  cursor: pointer;
  transition: var(--transition);
  font-size: 14px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: var(--text-primary);
}

.btn:hover {
  background-color: var(--bg-tertiary);
  border-color: var(--text-tertiary);
  transform: translateY(-1px);
}

.btn:active {
  transform: translateY(0);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.btn-primary:hover {
  background-color: var(--primary-dark);
  border-color: var(--primary-dark);
}

.btn-danger {
  background-color: var(--error-color);
  color: white;
  border-color: var(--error-color);
}

.btn-danger:hover {
  background-color: #dc2626;
  border-color: #dc2626;
}

.btn-warning {
  background-color: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.btn-warning:hover {
  background-color: #d97706;
  border-color: #d97706;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

/* Forms */
.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-primary);
  font-size: 14px;
}

.form-control {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  font-size: 14px;
  transition: var(--transition);
  background-color: var(--bg-primary);
}

.form-control:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.form-row {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.form-row .form-group {
  flex: 1;
  margin-bottom: 0;
}

/* Loading */
.loading {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-center {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: var(--text-tertiary);
}

.loading-center .loading {
  margin-right: 12px;
  border-color: var(--text-tertiary);
  border-top-color: var(--primary-color);
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-tertiary);
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-state p {
  margin: 0;
  font-size: 16px;
}

/* Toast */
.toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: var(--radius);
  color: white;
  font-size: 14px;
  z-index: 1000;
  opacity: 0;
  transition: var(--transition);
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(10px);
  max-width: 90vw;
  text-align: center;
}

.toast.show {
  opacity: 1;
}

.toast.success {
  background-color: var(--success-color);
}

.toast.error {
  background-color: var(--error-color);
}

.toast.info {
  background-color: rgba(0, 0, 0, 0.9);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    padding: 20px 16px;
  }

  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
  }

  .stat-card {
    padding: 20px 16px;
  }

  .card-body {
    padding: 20px 16px;
  }

  .users-table th,
  .users-table td,
  .activity-table th,
  .activity-table td {
    padding: 12px 16px;
  }

  .form-row {
    flex-direction: column;
    gap: 0;
  }

  .users-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .search-box {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 24px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-number {
    font-size: 28px;
  }

  .users-table-container,
  .activity-table-container {
    font-size: 0.875rem;
  }

  .users-table th,
  .users-table td,
  .activity-table th,
  .activity-table td {
    padding: 0.75rem 0.5rem;
  }

  .btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.75rem;
  }
}
</style>