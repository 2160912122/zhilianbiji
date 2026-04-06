<template>
  <el-container class="main-layout">
    <el-aside width="240px" class="sidebar">
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
    <el-container>
      <el-header class="header">
        <div class="header-left">
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
        <transition name="fade" mode="out-in">
          <router-view />
        </transition>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage, ElMessageBox } from 'element-plus'
// 导入需要的图标（确保图标已注册，若未注册需在main.js全局注册）
import {
  HomeFilled, Document, Grid, EditPen, Connection, Share,
  Setting, User, ArrowDown, UserFilled, Search, SwitchButton
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const searchQuery = ref('')

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
      '/admin': '工作台'
    }
    return titles[route.path] || '智联笔记'
  })

// 未登录时跳登录页
const toLogin = () => {
  router.push('/login')
}

// 处理下拉菜单命令（退出登录）
async function handleCommand(command) {
  if (command === 'logout') {
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
  }
}

// 挂载时初始化用户状态
onMounted(() => {
  userStore.initFromStorage()
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
  
  .search-box {
    width: 180px;
  }
  
  .main-content {
    padding: 16px;
  }
}
</style>