<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="logo">
        <i class="fa fa-book"></i>
        <span>智联笔记</span>
      </div>
      <div class="menu">
        <div style="position: relative;">
          <button id="new-btn" class="menu-btn" @click="handleNew">
            <i class="fa fa-file-o"></i> 新建
          </button>
        </div>
        
        <button id="open-btn" class="menu-btn" @click="handleOpen">
          <i class="fa fa-folder-open-o"></i> 打开
        </button>
        <button id="save-btn" class="menu-btn" @click="handleSave">
          <i class="fa fa-save"></i> 保存
        </button>
        <button id="export-btn" class="menu-btn" @click="handleExport">
          <i class="fa fa-download"></i> 导出
        </button>
        <button id="share-btn" class="menu-btn" @click="handleShare">
          <i class="fa fa-share-alt"></i> 分享
        </button>
        <button id="toggle-panel-btn" class="menu-btn" @click="handleTogglePanel">
          <i class="fa fa-sliders"></i> 属性
        </button>
        <button id="admin-btn" class="menu-btn" @click="handleAdmin">
          <i class="fa fa-cog"></i> 管理
        </button>
        <!-- 用户信息和退出按钮 -->
        <div style="position: relative; margin-left: 15px;">
          <button id="user-menu-btn" class="menu-btn" style="background-color: rgba(255, 255, 255, 0.2);" @click="toggleUserMenu">
            <i class="fa fa-user"></i>
            <span id="current-username">{{ currentUser?.username || 'admin' }}</span>
          </button>
          <div id="user-dropdown" class="user-dropdown" :class="{ 'visible': userMenuOpen }">
            <div class="dropdown-item" id="logout-btn" @click="handleLogout">
              <i class="fa fa-sign-out" style="color: #ef4444;"></i>退出登录
            </div>
          </div>
        </div>
      </div>
    </header>
    
    <!-- 主容器 -->
    <div class="container">
      <!-- 左侧边栏 -->
      <aside class="sidebar">
        <!-- 搜索区域 -->
        <div class="sidebar-section">
          <div class="search-box">
            <i class="fa fa-search"></i>
            <input type="text" placeholder="搜索笔记..." v-model="searchQuery" @input="handleSearch">
          </div>
        </div>
        
        <!-- 最近笔记 -->
        <div class="sidebar-section">
          <div class="sidebar-header">最近笔记</div>
          <ul class="note-list">
            <li class="note-item" v-for="note in recentNotes" :key="note.id" @click="openNote(note.id)">
              <div class="note-title">{{ note.title }}</div>
              <div class="note-date">{{ formatDate(note.date) }}</div>
            </li>
          </ul>
        </div>
      </aside>
      
      <!-- 主内容区域 -->
      <main class="main-content">
        <slot></slot>
      </main>
    </div>

    <!-- 用户资料模态框 -->
    <div class="modal" v-if="showProfileModal">
      <div class="modal-overlay" @click="showProfileModal = false"></div>
      <div class="modal-content">
        <div class="modal-header">
          <h3>个人资料</h3>
          <button class="modal-close" @click="showProfileModal = false">
            <i class="fa fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="profile-info" v-if="userProfile">
            <div class="profile-field">
              <label>用户名:</label>
              <span>{{ userProfile.username }}</span>
            </div>
            <div class="profile-field">
              <label>邮箱:</label>
              <span>{{ userProfile.email || '未设置' }}</span>
            </div>
            <div class="profile-field">
              <label>角色:</label>
              <span>{{ userProfile.role === 'admin' ? '管理员' : '普通用户' }}</span>
            </div>
            <div class="profile-field">
              <label>注册时间:</label>
              <span>{{ userProfile.created_at }}</span>
            </div>
            <div class="profile-field">
              <label>最后登录:</label>
              <span>{{ userProfile.last_login }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分享文档模态框 -->
    <div class="modal" v-if="showShareModal">
      <div class="modal-overlay" @click="showShareModal = false"></div>
      <div class="modal-content">
        <div class="modal-header">
          <h3>分享文档</h3>
          <button class="modal-close" @click="showShareModal = false">
            <i class="fa fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="share-options">
            <div class="form-group">
              <label for="share-link">分享链接</label>
              <div class="input-group">
                <input type="text" id="share-link" class="form-control" :value="shareLink" readonly>
                <button class="btn btn-primary" @click="copyShareLink">
                  <i class="fa fa-copy"></i>
                  复制
                </button>
              </div>
            </div>
            <div class="form-group">
              <label for="share-expiry">有效期</label>
              <select id="share-expiry" class="form-control">
                <option value="1d">1天</option>
                <option value="7d" selected>7天</option>
                <option value="30d">30天</option>
                <option value="never">永久</option>
              </select>
            </div>
            <div class="form-group">
              <label>
                <input type="checkbox" v-model="allowEdit">
                允许编辑
              </label>
            </div>
            <button class="btn btn-primary" @click="generateShareLink">
              <i class="fa fa-refresh"></i>
              重新生成链接
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, inject, provide } from 'vue'
import { useRouter } from 'vue-router'
import { getCurrentUser, clearUser } from '../utils/auth'
import { authAPI, documentAPI, userAPI } from '../services/api'

// 从App.vue注入的方法
const openCreateModal = inject('openCreateModal', () => {})


const router = useRouter()

// Reactive data
const currentUser = ref(null)
const loading = ref(false)
const userMenuOpen = ref(false)
const searchQuery = ref('')
const recentNotes = ref([])
const showProfileModal = ref(false)
const userProfile = ref(null)
// 分享相关状态
const showShareModal = ref(false)
const shareLink = ref('')
const allowEdit = ref(false)
// 属性面板切换状态
const showPropertiesPanel = ref(false)

// Provide the properties panel state to child components
provide('showPropertiesPanel', showPropertiesPanel)

// Methods
const fetchCurrentUser = () => {
  const user = getCurrentUser()
  if (user) {
    currentUser.value = user
  }
}

const fetchUserProfile = async () => {
  try {
    const profileData = await userAPI.getProfile()
    if (profileData.status === 'success' && profileData.user) {
      userProfile.value = profileData.user
    }
  } catch (error) {
    console.error('获取用户资料失败:', error)
    alert('获取用户资料失败，请稍后重试')
  }
}

const toggleUserMenu = () => {
  userMenuOpen.value = !userMenuOpen.value
}

const closeUserMenu = () => {
  userMenuOpen.value = false
}

const handleLogout = async () => {
  if (confirm('确定要退出登录吗？')) {
    loading.value = true
    try {
      await authAPI.logout()
      clearUser()
      currentUser.value = null
      router.push('/login')
    } catch (error) {
      console.error('退出登录失败:', error)
      // 即使API调用失败，也清除本地用户信息
      clearUser()
      currentUser.value = null
      router.push('/login')
    } finally {
      loading.value = false
    }
  }
}

const handleNew = () => {
  // 触发新建文档模态框
  openCreateModal()
}

const handleOpen = () => {
  // 打开文档逻辑
  console.log('打开文档')
  // 导航到首页的文档列表
  router.push('/')
}

const handleSave = () => {
  // 保存文档逻辑
  console.log('保存文档')
  // 发送保存请求到后端
  // 这里需要根据当前打开的文档来保存，暂时先实现基本功能
  alert('文档保存功能将在文档编辑页面实现')
}

const handleExport = () => {
  // 导出文档逻辑
  console.log('导出文档')
  // 检查当前是否在文档页面
  if (router.currentRoute.value.path.startsWith('/document/')) {
    // 发送事件给DocumentView组件处理导出
    window.dispatchEvent(new CustomEvent('export-document'))
  } else {
    alert('请先打开一个文档进行导出')
  }
}

const handleShare = () => {
  // 分享文档逻辑
  console.log('分享文档')
  // 检查当前是否在文档页面
  if (router.currentRoute.value.path.startsWith('/document/')) {
    // 显示分享模态框
    showShareModal.value = true
    // 生成示例分享链接
    shareLink.value = `${window.location.origin}/shared/${Math.random().toString(36).substr(2, 9)}`
  } else {
    alert('请先打开一个文档进行分享')
  }
}

const handleAdmin = () => {
  // 管理员页面逻辑
  console.log('管理文档')
  router.push('/admin')
}

const handleTogglePanel = () => {
  // 切换属性面板显示状态
  showPropertiesPanel.value = !showPropertiesPanel.value
  console.log('切换属性面板:', showPropertiesPanel.value)
}

const handleProfile = async () => {
  await fetchUserProfile()
  showProfileModal.value = true
}



// 分享功能方法
const copyShareLink = () => {
  navigator.clipboard.writeText(shareLink.value).then(() => {
    alert('链接已复制到剪贴板')
  }).catch(err => {
    console.error('复制失败:', err)
    alert('复制失败，请手动复制')
  })
}

const generateShareLink = () => {
  // 生成新的分享链接
  shareLink.value = `${window.location.origin}/shared/${Math.random().toString(36).substr(2, 9)}`
  alert('新链接已生成')
}

const handleSearch = () => {
  // 搜索笔记逻辑
  console.log('搜索笔记:', searchQuery.value)
}

const openNote = (noteId) => {
  // 打开笔记逻辑
  console.log('打开笔记:', noteId)
  router.push(`/document/${noteId}`)
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

// 点击外部关闭下拉菜单
const handleClickOutside = (event) => {
  const userDropdown = document.getElementById('user-dropdown')
  const userBtn = document.querySelector('.user-btn')
  if (userDropdown && !userDropdown.contains(event.target) && userBtn && !userBtn.contains(event.target)) {
    closeUserMenu()
  }
}

// Lifecycle hooks
onMounted(async () => {
  fetchCurrentUser()
  document.addEventListener('click', handleClickOutside)
  
  try {
    // 从API获取真实的文档列表
    const docsResult = await documentAPI.getDocuments()
    if (docsResult && docsResult.length > 0) {
      // 使用真实文档数据填充最近笔记
      recentNotes.value = docsResult.map(doc => ({
        id: doc.id,
        title: doc.name,
        date: doc.modified
      }))
    } else {
      // 如果没有文档，使用模拟数据
      recentNotes.value = [
        { id: 'e3c55583-7608-47ea-9a0c-8f7b77ed6090', title: '测试表格文档', date: new Date().toISOString() },
        { id: 'fd2075c8-6f3a-4d03-923d-034e28db8fd1', title: '测试白板文档', date: new Date().toISOString() }
      ]
    }
  } catch (error) {
    console.error('获取文档列表失败:', error)
    // 出错时使用模拟数据
    recentNotes.value = [
      { id: 'e3c55583-7608-47ea-9a0c-8f7b77ed6090', title: '测试表格文档', date: new Date().toISOString() },
      { id: 'fd2075c8-6f3a-4d03-923d-034e28db8fd1', title: '测试白板文档', date: new Date().toISOString() }
    ]
  }
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* 全局变量 */
:root {
  --primary-color: #10b981;
  --primary-light: #d1fae5;
  --primary-dark: #059669;
  --bg-primary: #fff;
  --bg-secondary: #f8fafc;
  --bg-tertiary: #f1f5f9;
  --text-primary: #334155;
  --text-secondary: #64748b;
  --text-tertiary: #94a3b8;
  --border-color: #e2e8f0;
  --shadow: 0 1px 3px rgba(0,0,0,0.1);
  --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
  --radius: 6px;
}

/* 应用容器 */
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

/* 顶部导航栏 */
.header {
  background-color: var(--primary-color);
  padding: 0 20px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: var(--shadow-md);
  z-index: 100;
  position: relative;
}

.logo {
  display: flex;
  align-items: center;
  color: white;
  font-weight: 600;
  font-size: 20px;
}

.logo i {
  margin-right: 10px;
  font-size: 24px;
}

.menu {
  display: flex;
  align-items: center;
  gap: 12px;
}

.menu-btn {
  background-color: rgba(255, 255, 255, 0.15);
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: var(--radius);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
  font-size: 14px;
  font-weight: 500;
}

.menu-btn:hover {
  background-color: rgba(255, 255, 255, 0.25);
  transform: translateY(-1px);
}

/* 用户菜单 */
.user-menu {
  position: relative;
}

.user-btn {
  display: flex;
  align-items: center;
  gap: 6px;
}

.user-btn .fa-angle-down {
  transition: transform 0.2s ease;
}

.user-btn .fa-angle-down.open {
  transform: rotate(180deg);
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: white;
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
  width: 140px;
  z-index: 1000;
  border: 1px solid var(--border-color);
  display: none;
  overflow: hidden;
  margin-top: 8px;
  animation: slideDown 0.2s ease-out;
}

.user-dropdown.visible {
  display: block;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-item {
  padding: 12px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: background-color 0.2s;
  font-size: 14px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background-color: var(--bg-tertiary);
}

/* 主容器 */
.container {
  display: flex;
  height: calc(100vh - 60px);
  overflow: hidden;
}

/* 左侧边栏 */
.sidebar {
  width: 260px;
  background-color: white;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 通用模态框样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-content {
  position: relative;
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: var(--shadow-md);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.modal-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--text-tertiary);
}

.modal-close:hover {
  color: var(--text-secondary);
}

.modal-body {
  padding: 24px;
}

/* 表单样式 */
.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-primary);
}

.form-control {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  font-size: 14px;
  transition: var(--transition);
}

.form-control:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.input-group {
  display: flex;
  gap: 8px;
}

.input-group .form-control {
  flex: 1;
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

/* 按钮样式 */
.btn {
  padding: 10px 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: var(--transition);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn:hover {
  background-color: var(--bg-tertiary);
  border-color: var(--text-tertiary);
  transform: translateY(-1px);
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

.input-group .btn {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}

/* 分享选项样式 */
.share-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.share-options .form-group:last-child {
  margin-bottom: 0;
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.profile-field {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
}

.profile-field label {
  font-weight: 500;
  color: var(--text-primary);
  min-width: 80px;
}

.profile-field span {
  color: var(--text-secondary);
  flex: 1;
  text-align: right;
}

.sidebar-section {
  padding: 16px 0;
  border-bottom: 1px solid var(--border-color);
}

.sidebar-header {
  padding: 0 16px 12px;
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 14px;
  letter-spacing: 0.5px;
}

/* 搜索框 */
.search-box {
  display: flex;
  align-items: center;
  padding: 0 16px;
  position: relative;
}

.search-box i {
  position: absolute;
  left: 28px;
  color: var(--text-tertiary);
  font-size: 14px;
}

.search-box input {
  width: 100%;
  padding: 8px 16px 8px 40px;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  font-size: 14px;
  transition: all 0.2s;
}

.search-box input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px var(--primary-light);
}

/* 笔记列表 */
.note-list {
  list-style: none;
  padding: 0;
  margin: 0;
  overflow-y: auto;
  flex: 1;
}

.note-item {
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid var(--border-color);
}

.note-item:last-child {
  border-bottom: none;
}

.note-item:hover {
  background-color: var(--bg-tertiary);
}

.note-title {
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.note-date {
  font-size: 12px;
  color: var(--text-tertiary);
}

/* 主内容区域 */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: var(--bg-secondary);
}
</style>