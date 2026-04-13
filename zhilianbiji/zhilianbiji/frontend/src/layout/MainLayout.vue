<template>
  <el-container class="main-layout">
    <!-- 侧边栏 -->
    <el-aside :width="isMobile ? '240px' : '240px'" :class="['sidebar', { 'open': isSidebarOpen }]">
      <div class="logo">
        <div class="logo-icon">
          <el-icon><Document /></el-icon>
        </div>
        <h2>智联笔记</h2>
      </div>
      <el-menu
        :default-active="currentRoute"
        router
        class="menu"
        :collapse-transition="false"
        @select="handleMenuSelect"
      >
        <!-- 所有用户都能看到的基础菜单 -->
        <el-menu-item index="/dashboard" class="menu-item">
          <el-icon class="menu-icon"><HomeFilled /></el-icon>
          <span class="menu-text">仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/notes" class="menu-item">
          <el-icon class="menu-icon"><Document /></el-icon>
          <span class="menu-text">笔记</span>
        </el-menu-item>
        <el-menu-item index="/tables" class="menu-item">
          <el-icon class="menu-icon"><Grid /></el-icon>
          <span class="menu-text">表格</span>
        </el-menu-item>
        <el-menu-item index="/whiteboards" class="menu-item">
          <el-icon class="menu-icon"><EditPen /></el-icon>
          <span class="menu-text">白板</span>
        </el-menu-item>
        <el-menu-item index="/mindmaps" class="menu-item">
          <el-icon class="menu-icon"><Connection /></el-icon>
          <span class="menu-text">脑图</span>
        </el-menu-item>
        <el-menu-item index="/flowcharts" class="menu-item">
          <el-icon class="menu-icon"><Share /></el-icon>
          <span class="menu-text">流程图</span>
        </el-menu-item>
        <el-menu-item index="/knowledge-graphs" class="menu-item">
          <el-icon class="menu-icon"><Link /></el-icon>
          <span class="menu-text">知识图谱</span>
        </el-menu-item>
        <el-menu-item index="/trash" class="menu-item">
          <el-icon class="menu-icon"><Delete /></el-icon>
          <span class="menu-text">回收站</span>
        </el-menu-item>

        <!-- 管理菜单：只对管理员可见 -->
        <el-sub-menu v-if="isAdmin" index="manage" class="sub-menu">
          <template #title>
            <el-icon class="menu-icon"><Setting /></el-icon>
            <span class="menu-text">管理</span>
          </template>

          <!-- 管理员工作台 -->
          <el-menu-item index="/admin" class="menu-item">工作台</el-menu-item>
          <!-- 内容管理 -->
          <el-menu-item index="/admin/note-manage" class="menu-item">内容管理</el-menu-item>
          <!-- 用户管理 -->
          <el-menu-item index="/admin/user-manage" class="menu-item">用户管理</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    
    <!-- 移动端侧边栏遮罩 -->
    <div v-if="isMobile && isSidebarOpen" class="sidebar-mask" @click="toggleSidebar"></div>
    
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <!-- 移动端菜单按钮 -->
          <el-button
            v-if="isMobile"
            class="menu-toggle"
            @click="toggleSidebar"
            size="small"
            icon="Menu"
            circle
          />
          <div class="breadcrumb">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item>{{ pageTitle }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
        </div>
        <div class="header-right">
          <!-- 搜索框 -->
          <div class="search-box">
            <el-input
              v-model="searchQuery"
              placeholder="搜索..."
              clearable
              size="small"
              prefix-icon="Search"
              class="search-input"
              @keyup.enter="handleSearch"
            />
          </div>
          <!-- 未登录时隐藏用户信息，显示登录按钮 -->
          <div v-if="!userStore.user" @click="toLogin" class="login-btn">
            <el-button type="primary" size="small" round>
              <el-icon><UserFilled /></el-icon>
              <span>登录</span>
            </el-button>
          </div>
          <el-dropdown v-else @command="handleCommand" trigger="click" placement="bottom">
            <div class="user-info">
              <div class="user-avatar">
                <el-icon><UserFilled /></el-icon>
              </div>
              <span class="user-name">{{ userStore.user?.username || userStore.user?.email }}</span>
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu class="user-dropdown">
                <el-dropdown-item command="profile" class="dropdown-item">
                  <el-icon><User /></el-icon>
                  <span>个人资料</span>
                </el-dropdown-item>
                <el-dropdown-item command="settings" class="dropdown-item">
                  <el-icon><Setting /></el-icon>
                  <span>设置</span>
                </el-dropdown-item>
                <el-dropdown-item command="logout" class="dropdown-item danger">
                  <el-icon><SwitchButton /></el-icon>
                  <span>退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage, ElMessageBox } from 'element-plus'
// 导入需要的图标（确保图标已注册，若未注册需在main.js全局注册）
import {
  HomeFilled, Document, Grid, EditPen, Connection, Share,
<<<<<<< HEAD
  Setting, User, ArrowDown, UserFilled, Search, SwitchButton, Menu
=======
  Setting, User, ArrowDown, UserFilled, Search, SwitchButton, Menu, Delete, Link
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const searchQuery = ref('')

// 响应式状态
const isMobile = ref(false)
const isSidebarOpen = ref(false)

// 检测是否为移动设备
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
  if (!isMobile.value) {
    isSidebarOpen.value = true
  }
}

// 切换侧边栏显示/隐藏
const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

// 处理菜单选择
const handleMenuSelect = () => {
  if (isMobile.value) {
    isSidebarOpen.value = false
  }
}

// 核心：判断是否为管理员（兼容store和localStorage，双重保障）
const isAdmin = computed(() => {
  // 优先从store取，没有则从localStorage取（1=管理员，0=普通用户）
  const storeIsAdmin = userStore.is_admin === 1 || userStore.user?.is_admin === 1
  const localIsAdmin = localStorage.getItem('is_admin') === '1'
  return storeIsAdmin || localIsAdmin
})

// 当前激活的路由
const currentRoute = computed(() => route.path)

// 页面标题映射
const pageTitle = computed(() => {
    const titles = {
      '/dashboard': '仪表盘',
      '/notes': '笔记管理',
      '/tables': '表格管理',
      '/whiteboards': '白板管理',
      '/mindmaps': '脑图管理',
      '/flowcharts': '流程图管理',
      '/knowledge-graphs': '知识图谱',
      '/trash': '回收站',
      '/admin': '工作台'
    }
    return titles[route.path] || '智联笔记'
  })

// 未登录时跳登录页
const toLogin = () => {
  router.push('/login')
}

// 处理搜索
function handleSearch() {
  if (searchQuery.value.trim()) {
    // 这里可以实现搜索逻辑，例如跳转到搜索结果页面
    console.log('搜索:', searchQuery.value)
    // 示例：跳转到搜索结果页面
    router.push(`/search?query=${encodeURIComponent(searchQuery.value)}`)
  }
}

// 处理下拉菜单命令（退出登录、个人资料、设置）
async function handleCommand(command) {
  switch (command) {
    case 'profile':
      // 跳转到个人资料页面
      console.log('个人资料')
      // 示例：跳转到个人资料页面
      router.push('/profile')
      break
    case 'settings':
      // 跳转到设置页面
      console.log('设置')
      // 示例：跳转到设置页面
      router.push('/settings')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        // 调用store的退出方法，清空store和localStorage
        await userStore.logout()
        // 额外清空localStorage的is_admin（防止残留）
        localStorage.removeItem('is_admin')
        ElMessage.success('已退出登录')
        router.push('/login')
      } catch (err) {
        ElMessage.info('已取消退出')
      }
      break
  }
}

// 挂载时初始化用户状态
onMounted(() => {
  userStore.initFromStorage()
  // 初始检测是否为移动设备
  checkMobile()
  // 添加窗口大小变化监听
  window.addEventListener('resize', checkMobile)
})

// 卸载时移除监听
onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.main-layout {
  height: 100vh;
  background-color: var(--background-light);
}

.sidebar {
  background-color: #1f2937;
  color: #fff;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  transition: var(--transition);
}

.logo {
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  border-bottom: 1px solid #374151;
  padding: 0 20px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  border-radius: var(--border-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  box-shadow: var(--shadow-md);
}

.logo h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #f3f4f6;
  background: linear-gradient(135deg, #f3f4f6, #d1d5db);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.menu {
  border: none;
  background-color: #1f2937;
  margin-top: 20px;
}

.menu-item {
  height: 56px;
  margin: 0 12px;
  border-radius: var(--border-radius-md);
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 12px;
}

.menu-icon {
  font-size: 18px;
  transition: var(--transition);
}

.menu-text {
  font-size: 14px;
  font-weight: 500;
  transition: var(--transition);
}

.menu :deep(.el-menu-item),
.menu :deep(.el-sub-menu__title) {
  color: #d1d5db;
  height: 56px;
  line-height: 56px;
  border-radius: var(--border-radius-md);
  margin: 0 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: var(--transition);
}

.menu :deep(.el-menu-item:hover),
.menu :deep(.el-menu-item.is-active) {
  background-color: rgba(64, 158, 255, 0.15);
  color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.menu :deep(.el-menu-item:hover .menu-icon),
.menu :deep(.el-menu-item.is-active .menu-icon) {
  color: var(--primary-color);
  transform: translateX(4px);
}

.sub-menu {
  margin-top: 12px;
}

.header {
  background-color: var(--background-white);
  border-bottom: 1px solid var(--border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 30px;
  height: 70px;
  box-shadow: var(--shadow-sm);
  transition: var(--transition);
}

.breadcrumb {
  display: flex;
  align-items: center;
}

.breadcrumb :deep(.el-breadcrumb__item) {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.search-box {
  position: relative;
  width: 280px;
}

.search-input {
  width: 100%;
  border-radius: var(--border-radius-lg);
  transition: var(--transition);
}

.search-input :deep(.el-input__wrapper) {
  border-radius: var(--border-radius-lg);
  background-color: var(--background-light);
  border: 1px solid transparent;
  transition: var(--transition);
}

.search-input :deep(.el-input__wrapper:hover) {
  border-color: var(--primary-light);
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.search-input :deep(.el-input__wrapper.is-focus) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.login-btn {
  cursor: pointer;
}

.user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: var(--border-radius-lg);
  transition: var(--transition);
}

.user-info:hover {
  background-color: var(--background-light);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  box-shadow: var(--shadow-sm);
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.user-dropdown {
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-lg);
  border: none;
  overflow: hidden;
  min-width: 180px;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  transition: var(--transition);
}

.dropdown-item:hover {
  background-color: var(--primary-light);
  color: var(--primary-color);
}

.dropdown-item.danger:hover {
  background-color: rgba(245, 108, 108, 0.1);
  color: var(--danger-color);
}

.main-content {
  background-color: var(--background-light);
  padding: 30px;
  overflow-y: auto;
  transition: var(--transition);
}

/* 移动端菜单按钮 */
.menu-toggle {
  margin-right: 12px;
  display: none;
}

/* 移动端侧边栏遮罩 */
.sidebar-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
  transition: var(--transition);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .sidebar {
    width: 200px !important;
  }
  
  .logo h2 {
    font-size: 18px;
  }
  
  .search-box {
    width: 200px;
  }
  
  .main-content {
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .menu-toggle {
    display: block;
  }
  
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 1000;
    transform: translateX(-100%);
  }
  
  .sidebar.open {
    transform: translateX(0);
  }
  
  .header {
    padding: 0 20px;
  }
  
  .header-left {
    display: flex;
    align-items: center;
  }
  
  .search-box {
    width: 180px;
  }
  
  .main-content {
    padding: 16px;
  }
  
  .user-name {
    display: none;
  }
  
  .header-right {
    gap: 12px;
  }
}
</style>