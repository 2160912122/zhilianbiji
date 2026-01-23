<template>
  <el-container class="main-layout">
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <h2>智联笔记</h2>
      </div>
      <el-menu
        :default-active="currentRoute"
        router
        class="menu"
      >
        <!-- 所有用户都能看到的基础菜单 -->
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/notes">
          <el-icon><Document /></el-icon>
          <span>笔记</span>
        </el-menu-item>
        <el-menu-item index="/tables">
          <el-icon><Grid /></el-icon>
          <span>表格</span>
        </el-menu-item>
        <el-menu-item index="/whiteboards">
          <el-icon><EditPen /></el-icon>
          <span>白板</span>
        </el-menu-item>
        <el-menu-item index="/mindmaps">
          <el-icon><Connection /></el-icon>
          <span>脑图</span>
        </el-menu-item>
        <el-menu-item index="/flowcharts">
          <el-icon><Share /></el-icon>
          <span>流程图</span>
        </el-menu-item>

        <!-- 管理菜单：只对管理员可见 -->
        <el-sub-menu v-if="isAdmin" index="manage">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>管理</span>
          </template>
          <el-menu-item index="/categories">分类</el-menu-item>
          <el-menu-item index="/tags">标签</el-menu-item>
          <!-- 管理员工作台 -->
          <el-menu-item index="/admin">工作台</el-menu-item>
          <!-- 用户管理 -->
          <el-menu-item index="/admin/user-manage">用户管理</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <span class="page-title">{{ pageTitle }}</span>
        </div>
        <div class="header-right">
          <!-- 未登录时隐藏用户信息，显示登录按钮 -->
          <div v-if="!userStore.user" @click="toLogin" class="login-btn">
            <el-button type="primary" size="small">登录</el-button>
          </div>
          <el-dropdown v-else @command="handleCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              {{ userStore.user?.username || userStore.user?.email }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage, ElMessageBox } from 'element-plus'
// 导入需要的图标（确保图标已注册，若未注册需在main.js全局注册）
import {
  HomeFilled, Document, Grid, EditPen, Connection, Share,
  Setting, User, ArrowDown, UserFilled
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

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
      '/categories': '分类管理',
      '/tags': '标签管理',
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
      // 额外清空localStorage的isAdmin（防止残留）
      localStorage.removeItem('isAdmin')
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
}

.sidebar {
  background-color: #304156;
  color: #fff;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #434a50;
}

.logo h2 {
  margin: 0;
  font-size: 20px;
  color: #fff;
}

.menu {
  border: none;
  background-color: #304156;
}

.menu :deep(.el-menu-item),
.menu :deep(.el-sub-menu__title) {
  color: #bfcbd9;
}

.menu :deep(.el-menu-item:hover),
.menu :deep(.el-menu-item.is-active) {
  background-color: #263445;
  color: #409eff;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.header-left .page-title {
  font-size: 18px;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.login-btn {
  cursor: pointer;
}

.user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>