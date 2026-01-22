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
        <el-sub-menu index="manage">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>管理</span>
          </template>
          <el-menu-item index="/categories">分类</el-menu-item>
          <el-menu-item index="/tags">标签</el-menu-item>
          <el-menu-item v-if="userStore.user?.is_admin" index="/admin">后台管理</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <span class="page-title">{{ pageTitle }}</span>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              {{ userStore.user?.username }}
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
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const currentRoute = computed(() => route.path)
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
    '/admin': '后台管理'
  }
  return titles[route.path] || '智联笔记'
})

async function handleCommand(command) {
  if (command === 'logout') {
    await userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }
}
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
