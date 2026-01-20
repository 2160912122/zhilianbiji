<template>
  <div id="app">
    <nav v-if="isAuthenticated" class="navbar">
      <div class="container">
        <h1 class="logo">笔记系统</h1>
        <ul class="nav-links">
          <li><router-link to="/">笔记列表</router-link></li>
          <li><router-link to="/categories">分类管理</router-link></li>
          <li><router-link to="/tags">标签管理</router-link></li>
          <li v-if="user.is_admin"><router-link to="/admin">管理员</router-link></li>
          <li><a href="#" @click.prevent="logout">退出登录</a></li>
        </ul>
      </div>
    </nav>
    <main class="container">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useUserStore } from './store/user'
import { useRouter } from 'vue-router'
import axios from 'axios'

const userStore = useUserStore()
const router = useRouter()

const isAuthenticated = computed(() => userStore.isAuthenticated)
const user = computed(() => userStore.user)

// 应用启动时检查登录状态
onMounted(async () => {
  try {
    const response = await axios.get('/api/user')
    if (response.data) {
      userStore.user = response.data
      userStore.isAuthenticated = true
    }
  } catch (error) {
    // 用户未登录或其他错误，保持未认证状态
    userStore.user = null
    userStore.isAuthenticated = false
  }
})

const logout = async () => {
  await userStore.logout()
  router.push('/login')
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f5f5f5;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.navbar {
  background-color: #4a90e2;
  color: white;
  padding: 10px 0;
  margin-bottom: 20px;
}

.navbar .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
}

.nav-links {
  display: flex;
  list-style: none;
  gap: 20px;
}

.nav-links a {
  color: white;
  text-decoration: none;
  font-weight: 500;
}

.nav-links a:hover {
  text-decoration: underline;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-primary {
  background-color: #4a90e2;
  color: white;
}

.btn-primary:hover {
  background-color: #357abd;
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background-color: #c0392b;
}

.btn-success {
  background-color: #2ecc71;
  color: white;
}

.btn-success:hover {
  background-color: #27ae60;
}

form div {
  margin-bottom: 15px;
}

form label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

form input, form textarea, form select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

form textarea {
  resize: vertical;
  min-height: 100px;
}

.flash-message {
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
  font-weight: 500;
}

.flash-success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.flash-error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
</style>