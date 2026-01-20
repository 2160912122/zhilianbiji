<template>
    <div class="login-container">
        <div class="login-box">
            <h2>流程图系统登录</h2>
            <el-form
                ref="loginFormRef"
                :model="loginForm"
                :rules="loginRules"
                @submit.prevent="handleLogin"
            >
                <el-form-item prop="username">
                    <el-input
                        v-model="loginForm.username"
                        placeholder="请输入用户名"
                        prefix-icon="User"
                        size="large"
                    />
                </el-form-item>
                <el-form-item prop="password">
                    <el-input
                        v-model="loginForm.password"
                        type="password"
                        placeholder="请输入密码"
                        prefix-icon="Lock"
                        size="large"
                        @keyup.enter="handleLogin"
                    />
                </el-form-item>
                <el-form-item>
                    <el-button
                        type="primary"
                        size="large"
                        @click="handleLogin"
                        :loading="loading"
                        style="width: 100%;"
                    >
                        登录
                    </el-button>
                </el-form-item>
            </el-form>
            <div class="login-footer">
                <span>还没有账号？</span>
                <el-link type="primary" @click="$router.push('/register')">立即注册</el-link>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from '@/utils/axiosInstance'

const router = useRouter()
const loginFormRef = ref()
const loading = ref(false)

const loginForm = reactive({
    username: '',
    password: ''
})

const loginRules = {
    username: [
        { required: true, message: '请输入用户名', trigger: 'blur' }
    ],
    password: [
        { required: true, message: '请输入密码', trigger: 'blur' }
    ]
}

const handleLogin = async () => {
    if (!loginFormRef.value) return

    await loginFormRef.value.validate(async (valid) => {
        if (valid) {
            loading.value = true
            try {
                const response = await axios.post('/api/login', loginForm)

                localStorage.setItem('token', response.data.access_token)
                localStorage.setItem('user', JSON.stringify(response.data.user))

                ElMessage.success('登录成功')
                router.push('/dashboard')
            } catch (error) {
                ElMessage.error(error.response?.data?.message || '登录失败')
            } finally {
                loading.value = false
            }
        }
    })
}
</script>

<style scoped>
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
    width: 400px;
    padding: 40px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 15px 35px rgba(50, 50, 93, 0.1), 0 5px 15px rgba(0, 0, 0, 0.07);
}

.login-box h2 {
    text-align: center;
    margin-bottom: 30px;
    color: #333;
}

.login-footer {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 20px;
    color: #666;
}

.login-footer span {
    margin-right: 10px;
}
</style>