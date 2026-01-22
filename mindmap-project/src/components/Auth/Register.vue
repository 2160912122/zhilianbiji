<template>
  <div class="register-page">
    <div class="card">
      <h2>注册-智联</h2>
      <form @submit.prevent="register">
        <input class="inp" v-model="username" placeholder="用户名" required />
        <input class="inp" v-model="password" type="password" placeholder="密码（≥6位）" required minlength="6" />
        <button class="btn">注册</button>
      </form>
      <div class="tip">已有账号？<router-link to="/login">立即登录</router-link></div>
    </div>
  </div>
</template>

<script>
import { userRegister, userLogin } from '@/api/authApi'
import router from '@/router'
export default {
  name: 'AuthRegister',
  data() {
    return {
      username: '',
      password: ''
    }
  },
  methods: {
    async register() {
      if (this.password.length <6) return alert('密码长度不能少于6位')
      try {
        await userRegister({ username: this.username.trim(), password: this.password })
        // 注册成功自动登录并保存登录态
        const res = await userLogin({ username: this.username.trim(), password: this.password })
        localStorage.setItem('isLogin', 'true')
        res.data?.token && localStorage.setItem('token', res.data.token)
        localStorage.setItem('isAdmin', 'false')
        router.push('/home')
      } catch (err) {
        alert('注册失败：' + (err.response?.data?.msg || '服务器异常'))
      }
    }
  }
}
</script>

<style scoped>
.register-page {
  height: 100vh;display: flex;align-items: center;justify-content: center;background: #f5f7fa;
}
.card {width:360px;padding:40px 32px;background:#fff;border-radius:8px;box-shadow:0 4px 20px rgba(0,0,0,.08)}
h2 {text-align:center;margin-bottom:28px;font-weight:500;color:#333}
.inp {width:100%;height:44px;margin-bottom:20px;padding:0 14px;border:1px solid #dcdfe6;border-radius:4px;font-size:15px;transition:.2s}
.inp:focus {outline:none;border-color:#409eff}
.btn {width:100%;height:46px;border:none;border-radius:4px;background:#409eff;color:#fff;font-size:16px;cursor:pointer;transition:.2s}
.btn:hover {background:#3a8ee6}
.tip {text-align:center;margin-top:18px;font-size:14px;color:#606266}
.tip a {color:#409eff;text-decoration:none}
</style>