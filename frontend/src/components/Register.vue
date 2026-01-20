<template>
  <div class="register-container">
    <div class="register-card">
      <h2>注册</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="username">用户名</label>
          <input 
            id="username" 
            v-model="form.username" 
            type="text" 
            required 
            placeholder="请输入用户名（至少3个字符）"
          />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            id="password" 
            v-model="form.password" 
            type="password" 
            required 
            placeholder="请输入密码（至少6个字符）"
          />
        </div>
        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input 
            id="confirmPassword" 
            v-model="confirmPassword" 
            type="password" 
            required 
            placeholder="请再次输入密码"
          />
        </div>
        <div v-if="localError" class="error-message">{{ localError }}</div>
        <div v-if="error" class="error-message">{{ error }}</div>
        <button 
          type="submit" 
          class="register-button" 
          :disabled="loading"
        >
          {{ loading ? '注册中...' : '注册' }}
        </button>
        <div class="login-link">
          已有账号？<router-link to="/login">立即登录</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    
    const form = ref({
      username: '',
      password: ''
    })
    
    const confirmPassword = ref('')
    const loading = ref(false)
    const error = ref(null)
    
    const localError = computed(() => {
      if (form.value.username.length < 3) {
        return '用户名长度至少3个字符'
      }
      if (form.value.password.length < 6) {
        return '密码长度至少6个字符'
      }
      if (form.value.password !== confirmPassword.value) {
        return '两次输入的密码不一致'
      }
      return null
    })
    
    const handleRegister = async () => {
      if (localError.value) {
        return
      }
      
      loading.value = true
      error.value = null
      
      try {
        await userStore.register({
          username: form.value.username,
          password: form.value.password
        })
        
        // 注册成功后跳转到登录页
        router.push('/login')
      } catch (err) {
        error.value = err.response?.data?.message || '注册失败，请稍后重试'
      } finally {
        loading.value = false
      }
    }
    
    return {
      form,
      confirmPassword,
      loading,
      error,
      localError,
      handleRegister
    }
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.register-card {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

h2 {
  margin-bottom: 1.5rem;
  text-align: center;
  color: #333;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
}

input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

input:focus {
  outline: none;
  border-color: #409eff;
}

.error-message {
  color: #f56c6c;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.register-button {
  width: 100%;
  padding: 0.8rem;
  background-color: #67c23a;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.register-button:hover {
  background-color: #85ce61;
}

.register-button:disabled {
  background-color: #c2e7b0;
  cursor: not-allowed;
}

.login-link {
  margin-top: 1rem;
  text-align: center;
  font-size: 0.9rem;
  color: #666;
}

.login-link a {
  color: #409eff;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>