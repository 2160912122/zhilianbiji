<template>
  <el-container style="height: 100vh;">
    <el-aside width="200px" style="background-color: #2e3b4e;">
      <div class="logo">知行织网 - 后台管理系统</div>
      <el-menu
        :default-active="activeMenu"  <!-- 动态绑定当前激活的菜单 -->
        class="el-menu-vertical-demo"
        background-color="#2e3b4e"
        text-color="#fff"
        active-text-color="#ffd04b"
        router  <!-- 开启路由模式 -->
      >
        <!-- 工作台：index对应路由路径 -->
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
        <!-- 退出登录：移除index，避免路由跳转冲突 -->
        <el-menu-item @click="handleLogout">
          <el-icon><SwitchButton /></el-icon>
          <template #title>退出登录</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header style="text-align: right; font-size: 12px">
        <el-dropdown>
          <i class="el-icon-setting" style="margin-right: 15px"></i>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>查看</el-dropdown-item>
              <el-dropdown-item>新增</el-dropdown-item>
              <el-dropdown-item>删除</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <span>管理员</span>
      </el-header>

      <el-main>
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
// 注意：如果已全局注册图标，可删除这行局部导入（避免重复）
// import { Menu, User, Document, SwitchButton } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

// 动态计算当前激活的菜单（解决菜单选中状态不生效的问题）
const activeMenu = computed(() => {
  return route.path || '/dashboard'
})

// 退出登录逻辑优化
const handleLogout = () => {
  try {
    // 清除Token
    localStorage.removeItem('token')
    // 跳转到登录页（强制刷新，避免缓存）
    router.push('/login').then(() => {
      ElMessage.success('退出登录成功！')
      // 可选：强制刷新页面，清空所有状态
      window.location.reload()
    })
  } catch (error) {
    console.error('退出登录失败：', error)
    ElMessage.error('退出登录失败，请重试！')
  }
}

// 页面挂载时校验登录状态（防止未登录直接访问后台）
onMounted(() => {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录！')
    router.push('/login')
  }
})
</script>

<style scoped>
.el-header {
  background-color: #fff;
  color: #333;
  line-height: 60px;
  border-bottom: 1px solid #e6e6e6;
}

.el-aside {
  color: #333;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  font-size: 16px;
  color: #fff;
  border-bottom: 1px solid #404958;
}

.el-menu-vertical-demo {
  border-right: none;
  height: calc(100vh - 60px);  /* 适配logo高度，菜单占满剩余空间 */
}

/* 修复菜单图标垂直居中 */
:deep(.el-menu-item) {
  display: flex;
  align-items: center;
}
</style>