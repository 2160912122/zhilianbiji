<template>
    <div class="register-container">
        <div class="register-box">
            <h2>用户注册</h2>
            <el-form
                ref="registerFormRef"
                :model="registerForm"
                :rules="registerRules"
                @submit.prevent="handleRegister"
            >
                <el-form-item prop="username">
                    <el-input
                        v-model="registerForm.username"
                        placeholder="请输入用户名"
                        prefix-icon="User"
                        size="large"
                    />
                </el-form-item>
                <el-form-item prop="email">
                    <el-input
                        v-model="registerForm.email"
                        placeholder="请输入邮箱"
                        prefix-icon="Message"
                        size="large"
                    />
                </el-form-item>
                <el-form-item prop="password">
                    <el-input
                        v-model="registerForm.password"
                        type="password"
                        placeholder="请输入密码"
                        prefix-icon="Lock"
                        size="large"
                    />
                </el-form-item>
                <el-form-item prop="confirmPassword">
                    <el-input
                        v-model="registerForm.confirmPassword"
                        type="password"
                        placeholder="请确认密码"
                        prefix-icon="Lock"
                        size="large"
                        @keyup.enter="handleRegister"
                    />
                </el-form-item>
                <el-form-item>
                    <el-button
                        type="primary"
                        size="large"
                        @click="handleRegister"
                        :loading="loading"
                        style="width: 100%;"
                    >
                        注册
                    </el-button>
                </el-form-item>
            </el-form>
            <div class="register-footer">
                <span>已有账号？</span>
                <el-link type="primary" @click="$router.push('/login')">立即登录</el-link>
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
const registerFormRef = ref()
const loading = ref(false)

const registerForm = reactive({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
})

const validatePassword = (rule, value, callback) => {
    if (value !== registerForm.password) {
        callback(new Error('两次输入密码不一致'))
    } else {
        callback()
    }
}

const registerRules = {
    username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, message: '用户名长度至少3个字符', trigger: 'blur' }
    ],
    email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
    ],
    password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度至少6位', trigger: 'blur' }
    ],
    confirmPassword: [
        { required: true, message: '请确认密码', trigger: 'blur' },
        { validator: validatePassword, trigger: 'blur' }
    ]
}

const handleRegister = async () => {
    if (!registerFormRef.value) return

    await registerFormRef.value.validate(async (valid) => {
        if (valid) {
            loading.value = true
            try {
                const { confirmPassword, ...registerData } = registerForm
                const response = await axios.post('/api/register', registerData)

                localStorage.setItem('token', response.data.access_token)
                localStorage.setItem('user', JSON.stringify(response.data.user))

                ElMessage.success('注册成功')
                router.push('/dashboard')
            } catch (error) {
                ElMessage.error(error.response?.data?.message || '注册失败')
            } finally {
                loading.value = false
            }
        }
    })
}
</script>

<style scoped>
.register-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-box {
    width: 400px;
    padding: 40px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 15px 35px rgba(50, 50, 93, 0.1), 0 5px 15px rgba(0, 0, 0, 0.07);
}

.register-box h2 {
    text-align: center;
    margin-bottom: 30px;
    color: #333;
}

.register-footer {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 20px;
    color: #666;
}

.register-footer span {
    margin-right: 10px;
}
</style>