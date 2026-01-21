<template>
  <div class="auth-container">
    <div class="auth-header">
      <h1>
        <i class="fa fa-book"></i>
        智联笔记
      </h1>
      <p>智能文档协作平台</p>
    </div>

    <form id="login-form" @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="username">用户名</label>
        <input
          type="text"
          id="username"
          v-model="credentials.username"
          class="form-control"
          placeholder="请输入用户名"
          required
          autocomplete="username"
          @input="validateUsername"
        >
        <div class="error-message" v-if="errors.username">{{ errors.username }}</div>
      </div>

      <div class="form-group">
        <label for="password">密码</label>
        <input
          type="password"
          id="password"
          v-model="credentials.password"
          class="form-control"
          placeholder="请输入密码"
          required
          autocomplete="current-password"
          @input="validatePassword"
        >
        <div class="error-message" v-if="errors.password">{{ errors.password }}</div>
      </div>

      <button type="submit" class="btn" id="login-btn" :disabled="loading || !isFormValid">
        <span id="btn-text" v-if="!loading">登录</span>
        <div class="loading" id="loading" v-else></div>
      </button>
    </form>

    <div class="auth-options">
      <div class="auth-divider">或者</div>
      <button type="button" class="btn btn-secondary" id="demo-btn" @click="handleDemoLogin" :disabled="loading">
        <i class="fa fa-magic"></i>
        体验演示模式
      </button>
    </div>

    <div class="auth-link">
      还没有账号？<router-link to="/register">立即注册</router-link>
    </div>

    <div class="demo-credentials">
      <h4>演示账号</h4>
      <p><strong>用户名：</strong>admin</p>
      <p><strong>密码：</strong>admin123</p>
    </div>

    <div class="toast" :class="{ show: showToast }" :style="toastStyle">
      {{ toastMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '../services/api'
import { saveUser } from '../utils/auth'

const router = useRouter()

// Reactive data
const credentials = reactive({
  username: '',
  password: ''
})

const loading = ref(false)
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('info') // info, success, error
const rememberMe = ref(false)
const errors = reactive({
  username: '',
  password: ''
})

// Computed
const toastStyle = ref({
  backgroundColor: 'rgba(0, 0, 0, 0.9)'
})

const isFormValid = computed(() => {
  return !errors.username && !errors.password && 
         credentials.username.trim() && credentials.password.trim()
})

// Methods
const showToastMessage = (message, type = 'info') => {
  toastMessage.value = message
  toastType.value = type
  
  // Set toast color based on type
  if (type === 'error') {
    toastStyle.value.backgroundColor = '#ef4444'
  } else if (type === 'success') {
    toastStyle.value.backgroundColor = '#10b981'
  } else {
    toastStyle.value.backgroundColor = 'rgba(0, 0, 0, 0.9)'
  }
  
  showToast.value = true
  
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

// 验证函数
const validateUsername = () => {
  if (!credentials.username.trim()) {
    errors.username = '用户名不能为空'
  } else if (credentials.username.length < 3) {
    errors.username = '用户名长度不能少于3个字符'
  } else {
    errors.username = ''
  }
}

const validatePassword = () => {
  if (!credentials.password) {
    errors.password = '密码不能为空'
  } else if (credentials.password.length < 6) {
    errors.password = '密码长度不能少于6个字符'
  } else {
    errors.password = ''
  }
}

const handleLogin = async () => {
  // 表单验证
  validateUsername()
  validatePassword()
  
  if (!isFormValid.value) {
    showToastMessage('请检查表单填写是否正确', 'error')
    return
  }

  loading.value = true

  try {
      const result = await authAPI.login({
        username: credentials.username.trim(),
        password: credentials.password
      })
      
      if (result && result.status === 'success' && result.user) {
        // 保存用户信息
        saveUser(result.user)
        showToastMessage('登录成功，正在跳转...', 'success')
        
        // 跳转到首页或之前的页面
        const redirectPath = router.currentRoute.value.query.redirect || '/'
        setTimeout(() => {
          router.push(redirectPath)
        }, 1500)
    } else {
      showToastMessage(result?.message || '登录失败，请检查用户名和密码', 'error')
    }
  } catch (error) {
    console.error('登录失败:', error)
    showToastMessage('登录失败，请检查网络连接或服务器状态', 'error')
  } finally {
    loading.value = false
  }
}

const handleDemoLogin = () => {
  // 演示账号登录
  credentials.username = 'admin'
  credentials.password = 'admin123'
  rememberMe.value = false
  handleLogin()
}
</script>

<style>
/* 登录页面完整样式 */
#app {
    background-color: #f5f7fa !important;
    min-height: 100vh !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 20px !important;
}

.auth-container {
    background-color: #ffffff !important;
    padding: 2.5rem !important;
    border-radius: 8px !important;
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05) !important;
    width: 100% !important;
    max-width: 480px !important;
    margin: 0 !important;
    animation: slideUp 0.5s ease-out !important;
    margin-top: 20px !important;
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.auth-header {
    text-align: center !important;
    margin-bottom: 2rem !important;
}

.auth-header h1 {
    color: #3b82f6 !important;
    margin: 0 0 0.5rem !important;
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0.5rem !important;
}

.auth-header p {
    color: #64748b !important;
    margin: 0 !important;
    font-size: 0.95rem !important;
}

.form-group {
    margin-bottom: 1.25rem !important;
}

.form-group label {
    display: block !important;
    margin-bottom: 0.5rem !important;
    color: #1e293b !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
}

.form-control {
    width: 100% !important;
    padding: 0.875rem 1rem !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    font-size: 1rem !important;
    background-color: #ffffff !important;
    box-sizing: border-box !important;
}

.form-control:focus {
    border-color: #3b82f6 !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
}

.form-control::placeholder {
    color: #94a3b8 !important;
}

.btn {
    width: 100% !important;
    padding: 0.875rem 1.5rem !important;
    border: none !important;
    border-radius: 8px !important;
    background-color: #3b82f6 !important;
    color: white !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0.5rem !important;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06) !important;
    box-sizing: border-box !important;
}

.btn:hover {
    background-color: #2563eb !important;
    transform: translateY(-1px) !important;
}

.btn:active {
    transform: translateY(0) !important;
}

.btn:disabled {
    opacity: 0.6 !important;
    cursor: not-allowed !important;
    transform: none !important;
    box-shadow: none !important;
}

.btn-secondary {
    background-color: #f8fafc !important;
    color: #1e293b !important;
    border: 1px solid #e2e8f0 !important;
}

.btn-secondary:hover {
    background-color: #ffffff !important;
    border-color: #3b82f6 !important;
}

.auth-link {
    text-align: center !important;
    margin-top: 1.5rem !important;
    font-size: 0.9rem !important;
    color: #64748b !important;
}

.auth-link a {
    color: #3b82f6 !important;
    text-decoration: none !important;
    font-weight: 500 !important;
}

.auth-link a:hover {
    color: #2563eb !important;
    text-decoration: underline !important;
}

.auth-options {
    margin-top: 1.5rem !important;
    padding-top: 1.5rem !important;
    border-top: 1px solid #e2e8f0 !important;
}

.auth-divider {
    display: flex !important;
    align-items: center !important;
    margin: 1.5rem 0 !important;
    color: #94a3b8 !important;
    font-size: 0.875rem !important;
}

.auth-divider::before,
.auth-divider::after {
    content: '' !important;
    flex: 1 !important;
    border-top: 1px solid #e2e8f0 !important;
}

.auth-divider::before {
    margin-right: 1rem !important;
}

.auth-divider::after {
    margin-left: 1rem !important;
}

.demo-credentials {
    background-color: #f8fafc !important;
    padding: 1rem !important;
    border-radius: 8px !important;
    margin-top: 1rem !important;
    font-size: 0.875rem !important;
    color: #64748b !important;
    border: 1px solid #e2e8f0 !important;
}

.demo-credentials h4 {
    margin: 0 0 0.5rem !important;
    color: #1e293b !important;
    font-size: 0.9rem !important;
}

.demo-credentials p {
    margin: 0.25rem 0 !important;
}

.error-message {
    color: #ef4444 !important;
    font-size: 0.8rem !important;
    margin-top: 4px !important;
}

.loading {
    display: inline-block !important;
    width: 16px !important;
    height: 16px !important;
    border: 2px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 50% !important;
    border-top-color: white !important;
    animation: spin 0.8s linear infinite !important;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}
</style>