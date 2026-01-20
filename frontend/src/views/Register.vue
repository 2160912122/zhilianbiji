<template>
  <div class="register-container">
    <div class="register-form card">
      <h2>注册</h2>
      
      <div v-if="userStore.error" class="flash-message flash-error">
        {{ userStore.error }}
      </div>
      
      <form @submit.prevent="handleRegister">
        <div>
          <label for="username">用户名</label>
          <input 
            type="text" 
            id="username" 
            v-model="credentials.username" 
            required
            placeholder="请输入用户名（3-50个字符）"
          />
        </div>
        
        <div>
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password" 
            v-model="credentials.password" 
            required
            placeholder="请输入密码（至少6个字符）"
          />
        </div>
        
        <div>
          <button type="submit" class="btn btn-primary" :disabled="userStore.loading">
            {{ userStore.loading ? '注册中...' : '注册' }}
          </button>
        </div>
      </form>
      
      <p class="login-link">
        已有账号？ <router-link to="/login">立即登录</router-link>
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

const handleRegister = async () => {
  try {
    await userStore.register(credentials.value)
    router.push('/login')
  } catch (error) {
    // 错误已经在userStore中处理
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}

.register-form {
  width: 100%;
  max-width: 400px;
}

.register-form h2 {
  margin-bottom: 20px;
  text-align: center;
  color: #333;
}

.login-link {
  margin-top: 20px;
  text-align: center;
}
</style>