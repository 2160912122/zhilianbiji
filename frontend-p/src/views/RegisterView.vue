<template>
  <div class="auth-container">
    <div class="auth-header">
      <h1>
        <i class="fa fa-book"></i>
        智联笔记
      </h1>
      <p>创建您的账号</p>
    </div>

    <form id="register-form" @submit.prevent="handleRegister">
      <div class="form-group">
        <label for="username">用户名</label>
        <div style="position: relative;">
          <input
            type="text"
            id="username"
            v-model="userData.username"
            class="form-control"
            :class="{
              'error': errors.username,
              'success': !errors.username && usernameAvailable === true
            }"
            placeholder="请输入用户名（3-20个字符）"
            required
            autocomplete="username"
            @input="validateUsername"
            @blur="checkUsernameAvailability"
          >
          <i class="fa" :class="[
            errors.username ? 'fa-times input-icon error' : 
            usernameAvailable === true ? 'fa-check input-icon success' : 
            'fa-user input-icon'
          ]"></i>
        </div>
        <div class="error-text" :class="{ 'show': errors.username }">{{ errors.username }}</div>
        <div class="success-text" :class="{ 'show': !errors.username && usernameAvailable === true }">用户名可用</div>
      </div>

      <div class="form-group">
        <label for="password">密码</label>
        <div style="position: relative;">
          <input
            :type="showPassword ? 'text' : 'password'"
            id="password"
            v-model="userData.password"
            class="form-control"
            :class="{ 'error': errors.password }"
            placeholder="请输入密码（至少6个字符）"
            required
            autocomplete="new-password"
            @input="validatePassword"
          >
          <i class="fa" :class="[
            errors.password ? 'fa-times input-icon error' : 
            'fa-lock input-icon'
          ]"></i>
          <button
            type="button"
            id="toggle-password"
            @click="togglePassword"
            style="position: absolute; right: 2.5rem; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; color: var(--text-tertiary);"
            aria-label="显示/隐藏密码"
          >
            <i class="fa" :class="showPassword ? 'fa-eye-slash' : 'fa-eye'"></i>
          </button>
        </div>
        <div class="password-strength">
          <div class="password-strength-bar" :class="passwordStrengthClass"></div>
        </div>
        <div class="password-strength-text" :style="{
          color: userData.password && passwordStrengthClass === 'weak' ? 'var(--error-color)' : 
                 userData.password && passwordStrengthClass === 'medium' ? '#f59e0b' : 
                 userData.password && passwordStrengthClass === 'strong' ? 'var(--success-color)' : 
                 'var(--text-tertiary)'
        }">
          {{ passwordStrengthText }}
        </div>
        <div class="error-text" :class="{ 'show': errors.password }">{{ errors.password }}</div>
      </div>

      <div class="form-group">
        <label for="confirmPassword">确认密码</label>
        <div style="position: relative;">
          <input
            :type="showConfirmPassword ? 'text' : 'password'"
            id="confirmPassword"
            v-model="confirmPassword"
            class="form-control"
            :class="{ 'error': errors.confirmPassword }
            "
            placeholder="请再次输入密码"
            required
            autocomplete="new-password"
            @input="validateConfirmPassword"
          >
          <i class="fa" :class="[
            errors.confirmPassword ? 'fa-times input-icon error' : 
            userData.password && confirmPassword && userData.password === confirmPassword ? 'fa-check input-icon success' : 
            'fa-lock input-icon'
          ]"></i>
          <button
            type="button"
            id="toggle-confirm"
            @click="toggleConfirmPassword"
            style="position: absolute; right: 2.5rem; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; color: var(--text-tertiary);"
            aria-label="显示/隐藏密码"
          >
            <i class="fa" :class="showConfirmPassword ? 'fa-eye-slash' : 'fa-eye'"></i>
          </button>
        </div>
        <div class="error-text" :class="{ 'show': errors.confirmPassword }">{{ errors.confirmPassword }}</div>
      </div>

      <div class="form-group">
        <label style="display: flex; align-items: flex-start; gap: 0.5rem; cursor: pointer;">
          <input
            type="checkbox"
            id="agree-terms"
            v-model="agreeTerms"
            required
            style="margin-top: 0.125rem;"
            @change="validateTerms"
          >
          <span style="font-size: 0.875rem; line-height: 1.4;">
            我已阅读并同意
            <a href="#" style="color: var(--primary-color); text-decoration: none;">服务条款</a>
            和
            <a href="#" style="color: var(--primary-color); text-decoration: none;">隐私政策</a>
          </span>
        </label>
        <div class="error-text" :class="{ 'show': errors.terms }">{{ errors.terms }}</div>
      </div>

      <button type="submit" class="btn" id="submit-btn" :disabled="loading || !isFormValid">
        <span id="btn-text" v-if="!loading">
          <i class="fa fa-user-plus"></i>
          注册账号
        </span>
        <div class="loading" v-else></div>
      </button>
    </form>

    <div class="auth-link">
      已有账号？<router-link to="/login">立即登录</router-link>
    </div>

    <div class="toast" :class="[
      'toast',
      showToast ? 'show' : '',
      toastType
    ]">
      {{ toastMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '../services/api'

const router = useRouter()

// Reactive data
const userData = reactive({
  username: '',
  password: ''
})

const confirmPassword = ref('')
const loading = ref(false)
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('info') // info, success, error
const agreeTerms = ref(false)
const usernameAvailable = ref(null) // null: 未检查, true: 可用, false: 不可用
const checkingUsername = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

// 错误信息
const errors = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  terms: ''
})

// Computed
const toastStyle = computed(() => {
  if (toastType.value === 'error') {
    return { backgroundColor: '#ef4444' }
  } else if (toastType.value === 'success') {
    return { backgroundColor: '#10b981' }
  } else {
    return { backgroundColor: 'rgba(0, 0, 0, 0.9)' }
  }
})

// 密码强度计算
const passwordStrength = computed(() => {
  if (!userData.password) return 0
  
  let strength = 0
  
  // 长度检查
  if (userData.password.length >= 8) strength += 1
  if (userData.password.length >= 12) strength += 1
  
  // 字母检查
  if (/[a-z]/.test(userData.password)) strength += 1
  if (/[A-Z]/.test(userData.password)) strength += 1
  
  // 数字检查
  if (/[0-9]/.test(userData.password)) strength += 1
  
  // 特殊字符检查
  if (/[^a-zA-Z0-9]/.test(userData.password)) strength += 1
  
  return strength
})

// 密码强度类名
const passwordStrengthClass = computed(() => {
  const strength = passwordStrength.value
  if (strength <= 2) return 'weak'
  if (strength <= 4) return 'medium'
  return 'strong'
})

// 密码强度文本
const passwordStrengthText = computed(() => {
  if (!userData.password) return '密码强度'
  
  const strength = passwordStrength.value
  if (strength <= 2) return '密码强度：太弱'
  if (strength <= 4) return '密码强度：中等'
  return '密码强度：强'
})

// 密码显示切换方法
const togglePassword = () => {
  showPassword.value = !showPassword.value
}

const toggleConfirmPassword = () => {
  showConfirmPassword.value = !showConfirmPassword.value
}

// 表单验证
const isFormValid = computed(() => {
  return !errors.username && 
         !errors.password && 
         !errors.confirmPassword && 
         !errors.terms && 
         userData.username.trim() && 
         userData.password && 
         confirmPassword.value && 
         agreeTerms.value && 
         usernameAvailable.value !== false
})

// Methods
const showToastMessage = (message, type = 'info') => {
  toastMessage.value = message
  toastType.value = type
  showToast.value = true
  
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

// 验证函数
const validateUsername = () => {
  if (!userData.username.trim()) {
    errors.username = '用户名不能为空'
  } else if (userData.username.length < 3) {
    errors.username = '用户名长度不能少于3个字符'
  } else if (userData.username.length > 20) {
    errors.username = '用户名长度不能超过20个字符'
  } else if (!/^[a-zA-Z0-9_-]+$/.test(userData.username)) {
    errors.username = '用户名只能包含字母、数字、下划线和短横线'
  } else {
    errors.username = ''
  }
}

const validatePassword = () => {
  if (!userData.password) {
    errors.password = '密码不能为空'
  } else if (userData.password.length < 6) {
    errors.password = '密码长度不能少于6个字符'
  } else {
    errors.password = ''
  }
}

const validateConfirmPassword = () => {
  if (!confirmPassword.value) {
    errors.confirmPassword = '请确认密码'
  } else if (confirmPassword.value !== userData.password) {
    errors.confirmPassword = '两次输入的密码不一致'
  } else {
    errors.confirmPassword = ''
  }
}

const validateTerms = () => {
  if (!agreeTerms.value) {
    errors.terms = '请阅读并同意用户协议和隐私政策'
  } else {
    errors.terms = ''
  }
}

// 检查用户名可用性
const checkUsernameAvailability = async () => {
  if (!userData.username.trim() || errors.username) return
  
  checkingUsername.value = true
  usernameAvailable.value = null
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 这里应该调用真实的API来检查用户名可用性
    // const result = await authAPI.checkUsername(userData.username)
    
    // 模拟结果，实际项目中应该替换为真实API调用
    const takenUsernames = ['admin', 'test', 'demo', 'user']
    usernameAvailable.value = !takenUsernames.includes(userData.username)
  } catch (error) {
    console.error('检查用户名可用性失败:', error)
    showToastMessage('检查用户名可用性失败，请稍后重试', 'error')
  } finally {
    checkingUsername.value = false
  }
}

const handleRegister = async () => {
  // 表单验证
  validateUsername()
  validatePassword()
  validateConfirmPassword()
  validateTerms()
  
  if (!isFormValid.value) {
    showToastMessage('请检查表单填写是否正确', 'error')
    return
  }

  loading.value = true

  try {
    const result = await authAPI.register({
      username: userData.username.trim(),
      password: userData.password
    })
    
    if (result.status === 'success') {
      showToastMessage('注册成功，请登录', 'success')
      
      // 跳转到登录页面
      setTimeout(() => {
        router.push('/login')
      }, 1500)
    } else {
      showToastMessage(result.message, 'error')
    }
  } catch (error) {
    console.error('注册失败:', error)
    if (error.response && error.response.data) {
      showToastMessage(error.response.data.message || '注册失败', 'error')
    } else {
      showToastMessage('注册失败，请检查网络连接或服务器状态', 'error')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
:root {
    --primary-color: #3b82f6;
    --primary-dark: #2563eb;
    --primary-light: #dbeafe;
    --bg-primary: #ffffff;
    --bg-secondary: #f8fafc;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --text-tertiary: #94a3b8;
    --border-color: #e2e8f0;
    --error-color: #ef4444;
    --success-color: #3b82f6;
    --shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --radius: 8px;
    --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

* {
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    margin: 0;
    background-color: #f5f7fa;
    color: var(--text-primary);
    line-height: 1.6;
}

.auth-container {
    background: var(--bg-primary);
    padding: 2.5rem;
    border-radius: var(--radius);
    box-shadow: var(--shadow-lg);
    width: 100%;
    max-width: 420px;
    margin: 20px;
    animation: slideUp 0.5s ease-out;
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
    text-align: center;
    margin-bottom: 2rem;
}

.auth-header h1 {
    color: var(--primary-color);
    margin: 0 0 0.5rem;
    font-size: 1.75rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}

.auth-header p {
    color: var(--text-secondary);
    margin: 0;
    font-size: 0.95rem;
}

.form-group {
    margin-bottom: 1.25rem;
    position: relative;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: var(--text-primary);
    font-weight: 500;
    font-size: 0.9rem;
}

.form-control {
    width: 100%;
    padding: 0.875rem 1rem;
    border: 1px solid var(--border-color);
    border-radius: var(--radius);
    font-size: 1rem;
    transition: var(--transition);
    background-color: var(--bg-primary);
}

.form-control:focus {
    border-color: var(--primary-color);
    outline: none;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-control.error {
    border-color: var(--error-color);
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.form-control.success {
    border-color: var(--success-color);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-control::placeholder {
    color: var(--text-tertiary);
}

.input-icon {
    position: absolute;
    right: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-tertiary);
    font-size: 1rem;
}

.input-icon.success {
    color: var(--success-color);
}

.input-icon.error {
    color: var(--error-color);
}

.btn {
    width: 100%;
    padding: 0.875rem 1.5rem;
    border: none;
    border-radius: var(--radius);
    background-color: var(--primary-color);
    color: white !important;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: var(--transition);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    box-shadow: var(--shadow-md);
    border: 1px solid transparent;
}

.btn:hover {
    background-color: var(--primary-dark);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

.btn:active {
    transform: translateY(0);
}

.btn:disabled {
    background-color: var(--text-tertiary);
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}

.error-text {
    color: var(--error-color);
    font-size: 0.8rem;
    margin-top: 0.25rem;
    display: none;
    animation: slideDown 0.2s ease-out;
}

.error-text.show {
    display: block;
}

.success-text {
    color: var(--success-color);
    font-size: 0.8rem;
    margin-top: 0.25rem;
    display: none;
}

.success-text.show {
    display: block;
}

.auth-link {
    text-align: center;
    margin-top: 1.5rem;
    font-size: 0.9rem;
    color: var(--text-secondary);
}

.auth-link a {
    color: var(--primary-color);
    text-decoration: none;
    font-weight: 500;
    transition: var(--transition);
}

.auth-link a:hover {
    color: var(--primary-dark);
    text-decoration: underline;
}

.password-strength {
    margin-top: 0.5rem;
    height: 4px;
    background-color: var(--border-color);
    border-radius: 2px;
    overflow: hidden;
}

.password-strength-bar {
    height: 100%;
    width: 0%;
    transition: var(--transition);
    border-radius: 2px;
}

.password-strength-bar.weak {
    width: 33%;
    background-color: var(--error-color);
}

.password-strength-bar.medium {
    width: 66%;
    background-color: #f59e0b;
}

.password-strength-bar.strong {
    width: 100%;
    background-color: var(--success-color);
}

.password-strength-text {
    font-size: 0.75rem;
    margin-top: 0.25rem;
    color: var(--text-tertiary);
}

.loading {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: white;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-5px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.toast {
    position: fixed;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%);
    padding: 12px 24px;
    border-radius: var(--radius);
    color: white;
    font-size: 14px;
    z-index: 1000;
    opacity: 0;
    transition: var(--transition);
    box-shadow: var(--shadow-lg);
    backdrop-filter: blur(10px);
    max-width: 90vw;
    text-align: center;
}

.toast.show {
    opacity: 1;
}

.toast.success {
    background-color: var(--success-color);
}

.toast.error {
    background-color: var(--error-color);
}

.toast.info {
    background-color: rgba(0, 0, 0, 0.9);
}

/* Responsive Design */
@media (max-width: 480px) {
    .auth-container {
        padding: 2rem 1.5rem;
        margin: 10px;
    }

    .auth-header h1 {
        font-size: 1.5rem;
    }

    .btn {
        padding: 0.75rem 1.5rem;
    }
}
</style>