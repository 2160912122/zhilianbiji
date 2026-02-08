<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2 class="login-title">登录</h2>
      <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" class="login-btn">登录</el-button>
          <el-button @click="goToRegister" link>没有账号？去注册</el-button>
        </el-form-item>
      </el-form>
    </el-card>
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
  }
}

// 跳注册页（同样用Vue Router）
const goToRegister = () => {
  router.push('/register').catch(() => {})
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
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f5f5;
}
.login-card {
  width: 400px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}
.login-title {
  text-align: center;
  margin-bottom: 20px;
  color: #1989fa;
}
.login-btn {
  width: 100%;
}
</style>