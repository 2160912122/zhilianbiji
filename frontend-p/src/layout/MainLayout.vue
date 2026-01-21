<template>
  <div class="layout-container">
    <!-- 左侧侧边栏 -->
    <div class="sidebar">
      <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical-demo"
        background-color="#1f2937"
        text-color="#fff"
        active-text-color="#fff"
        router
        unique-opened
      >
        <!-- 工作台 -->
        <el-menu-item index="/dashboard">
          <el-icon><Menu /></el-icon>
          <template #title>工作台</template>
        </el-menu-item>
        
        <!-- 用户管理 -->
        <el-menu-item index="/user">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
        
        <!-- 笔记管理 -->
        <el-menu-item index="/note">
          <el-icon><Document /></el-icon>
          <template #title>笔记管理</template>
        </el-menu-item>
        
        <!-- 退出登录 -->
        <el-menu-item @click="handleLogout">
          <el-icon><SwitchButton /></el-icon>
          <template #title>退出登录</template>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- 右侧主内容区 -->
    <div class="main-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Menu, User, Document, SwitchButton } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

// 动态计算当前激活的菜单项
const activeMenu = computed(() => {
  return route.path || '/dashboard'
})

// 退出登录逻辑
const handleLogout = () => {
  localStorage.removeItem('token')
  ElMessage.success('退出登录成功！')
  router.push('/login')
}

// 登录状态校验
onMounted(() => {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录！')
    router.push('/login')
  }
})
</script>

<style scoped>
.layout-container {
  display: flex;
  width: 100vw;
  height: 100vh;
}

.sidebar {
  width: 200px;
  height: 100%;
  background-color: #1f2937;
}

.el-menu-vertical-demo {
  border-right: none;
  height: 100%;
}

:deep(.el-menu-item.is-active) {
  background-color: #3b82f6 !important;
  color: #fff !important;
}

:deep(.el-menu-item:hover) {
  background-color: #374151 !important;
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f9f9f9;
}
</style>