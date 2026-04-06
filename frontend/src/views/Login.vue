<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1>登录</h1>
        <p>智联笔记系统</p>
      </div>
      <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" class="login-form">
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            style="width: 100%"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="login-footer">
        <span>没有账号？</span>
        <router-link to="/register">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'

// 初始化路由和Store
const router = useRouter()
const userStore = useUserStore()

// 表单相关
const loginFormRef = ref(null)
const loginForm = ref({
  username: '',
  password: ''
})
const loading = ref(false)

// 表单校验规则
const loginRules = ref({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
})

// 核心：防闪退的登录逻辑（异步+延迟跳转+只走Vue Router）
const handleLogin = async () => {
  // 1. 先校验表单
  if (!loginFormRef.value) return
  try {
    await loginFormRef.value.validate()
  } catch (error) {
    ElMessage.error('请完善登录信息')
    return
  }

  // 2. 异步登录，确保token存到localStorage
  try {
    loading.value = true
    // 等待登录接口返回，确保token已存储
    const res = await userStore.login({
      username: loginForm.value.username,
      password: loginForm.value.password
    })

    // 3. 登录成功提示（必加，延迟跳转）
    ElMessage.success('登录成功！')

    // 4. 延迟300ms跳转（关键！等localStorage完全同步）
    // 只走Vue Router跳转，绝对不用window.location.href
    setTimeout(() => {
      router.push('/dashboard').catch(err => {
        console.log('跳转dashboard失败，兜底跳首页', err)
        router.push('/').catch(() => {})
      })
    }, 300)

  } catch (error) {
    // 登录失败提示，不删token
    ElMessage.error(error.message || '登录失败，请检查账号密码')
    console.error('登录失败详情：', error)
  } finally {
    loading.value = false
  }
}

// 挂载时检测：如果已有token，直接跳dashboard（防重复登录）
onMounted(() => {
  const token = localStorage.getItem('token')
  if (token) {
    ElMessage.info('已检测到登录状态，自动跳转到首页')
    setTimeout(() => {
      router.push('/dashboard').catch(() => {})
    }, 500)
  }
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  margin: 0 0 10px;
  font-size: 28px;
  color: #333;
}

.login-header p {
  margin: 0;
  font-size: 14px;
  color: #999;
}

.login-form {
  margin-bottom: 20px;
}

.login-footer {
  text-align: center;
  font-size: 14px;
  color: #666;
}

.login-footer a {
  color: #409eff;
  text-decoration: none;
  margin-left: 5px;
}

.login-footer a:hover {
  text-decoration: underline;
}
</style>