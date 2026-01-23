<template>
  <!-- 路由出口：渲染匹配的页面组件 -->
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useUserStore } from './store/user'

const userStore = useUserStore()

// 应用启动时初始化用户状态
onMounted(() => {
  // 从localStorage同步用户状态
  userStore.initFromStorage()
  console.log('应用启动，初始化用户状态:', {
    token: userStore.token,
    is_admin: userStore.is_admin
  })
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
}

body {
  margin: 0;
  padding: 0;
  /* 新增：避免页面内容超出视口 */
  overflow-x: hidden;
  background-color: #f5f5f5; /* 新增：全局背景色，提升视觉体验 */
}

/* 全局提示框样式（可选，统一权限提示的样式） */
.alert {
  padding: 12px 20px;
  background-color: #f56c6c;
  color: white;
  border-radius: 4px;
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
}
</style>