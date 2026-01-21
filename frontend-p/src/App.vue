<script setup>
import { RouterView } from 'vue-router'
import { ref, provide, onMounted } from 'vue'
import { authAPI } from './services/api'
import { saveUser, clearUser } from './utils/auth'

// 提供共享状态，用于控制创建文档模态框
const showCreateModal = ref(false)

const openCreateModal = () => {
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
}

// 检查用户登录状态
const checkLoginStatus = async () => {
  try {
    const result = await authAPI.checkLogin()
    if (result && result.logged_in && result.username) {
      // 用户已登录，更新localStorage中的用户信息
      saveUser({
        id: result.id || '',
        username: result.username,
        role: result.role || 'user'
      })
    } else {
      // 用户未登录，清除localStorage中的用户信息
      clearUser()
    }
  } catch (error) {
    console.error('检查登录状态失败:', error)
    // 检查失败时，清除localStorage中的用户信息
    clearUser()
  }
}

// 应用初始化时检查登录状态
onMounted(() => {
  checkLoginStatus()
})

// 提供给子组件使用
provide('showCreateModal', showCreateModal)
provide('openCreateModal', openCreateModal)
provide('closeCreateModal', closeCreateModal)
</script>

<template>
  <div class="app-container">
    <RouterView />
  </div>
</template>

<style>
/* 全局样式 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
  line-height: 1.6;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 认证页面特殊处理 */
.auth-container {
  margin: auto;
  display: block;
}

/* 公共按钮样式 */
button {
  cursor: pointer;
  font-family: inherit;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

/* 公共输入框样式 */
input, textarea, select {
  font-family: inherit;
  font-size: 1rem;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
