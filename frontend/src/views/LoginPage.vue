<template>
  <div class="login-container">
    <!-- 错误提示 -->
    <div v-if="showError" class="error-tip">
      <i class="error-icon">❌</i>
      用户名或密码错误!
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <h1 class="title">知行织网 - 后台管理系统</h1>
      
      <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" class="login-form">
        <el-form-item prop="username">
          <label class="label">* 用户名</label>
          <el-input v-model="loginForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>

        <el-form-item prop="password">
          <label class="label">* 密码</label>
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" class="login-btn" @click="handleLogin">登录</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import service from '@/utils/request'

const router = useRouter()
const loginFormRef = ref(null)
const showError = ref(false)

// 表单数据
const loginForm = reactive({
  username: 'admin',
  password: '123456'
})

// 表单校验规则
const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

// 登录方法
const handleLogin = async () => {
  try {
    await loginFormRef.value.validate()
    const formData = new FormData()
    formData.append('username', loginForm.username)
    formData.append('password', loginForm.password)
    
    const res = await service.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    localStorage.setItem('token', res.access_token)
    ElMessage.success('登录成功！')
    router.push('/dashboard')
    showError.value = false
  } catch (error) {
    console.error('登录失败：', error)
    showError.value = true
  }
}
</script>

<style scoped>
.login-container {
  width: 100vw;
  height: 100vh;
  background-color: #f9f9f9;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding-top: 20px;
}

.error-tip {
  background-color: #ffebee;
  color: #c62828;
  padding: 8px 20px;
  border-radius: 4px;
  margin-bottom: 30px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.error-icon {
  font-size: 16px;
}

.login-card {
  width: 500px;
  background: #fff;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.title {
  font-size: 24px;
  color: #1976d2;
  margin-bottom: 30px;
  font-weight: 600;
}

.login-form {
  width: 100%;
}

.label {
  font-size: 14px;
  color: #333;
  margin-bottom: 6px;
  display: inline-block;
  text-align: left;
  width: 100%;
}

.login-btn {
  width: 100%;
  background-color: #42a5f5;
  border: none;
  height: 40px;
  font-size: 16px;
  border-radius: 4px;
}

.login-btn:hover {
  background-color: #1e88e5;
}

.el-input {
  width: 100%;
  margin-top: 4px;
}
</style>