<template>
  <div class="login-container">
    <div class="login-form card">
      <h2>登录</h2>
      
      <div v-if="userStore.error" class="flash-message flash-error">
        {{ userStore.error }}
      </div>
      
      <form @submit.prevent="handleLogin">
        <div>
          <label for="username">用户名</label>
          <input 
            type="text" 
            id="username" 
            v-model="credentials.username" 
            required
            placeholder="请输入用户名"
          />
        </div>
        
        <div>
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password" 
            v-model="credentials.password" 
            required
            placeholder="请输入密码"
          />
        </div>
        
        <div>
          <button type="submit" class="btn btn-primary" :disabled="userStore.loading">
            {{ userStore.loading ? '登录中...' : '登录' }}
          </button>
        </div>
      </form>
      
      <p class="register-link">
        还没有账号？ <router-link to="/register">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'

const userStore = useUserStore()
const router = useRouter()
const credentials = ref({
  username: '',
  password: ''
})

const handleLogin = async () => {
  try {
    await userStore.login(credentials.value)
    router.push('/')
  } catch (error) {
    // 错误已经在userStore中处理
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}

.login-form {
  width: 100%;
  max-width: 400px;
}

.login-form h2 {
  margin-bottom: 20px;
  text-align: center;
  color: #333;
}

.register-link {
  margin-top: 20px;
  text-align: center;
}
</style>