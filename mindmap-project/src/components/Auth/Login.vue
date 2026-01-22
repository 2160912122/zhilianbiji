<template>
  <div class="login-page">
    <div class="card">
      <h2>登录-智联</h2>
      <form @submit.prevent="login">
        <input class="inp" v-model="username" placeholder="用户名" required />
        <input class="inp" v-model="password" type="password" placeholder="密码" required />
        <button class="btn">登录</button>
      </form>
      <div class="tip">没有账号？<router-link to="/register">立即注册</router-link></div>
      <div class="tip admin-tip" style="margin-top:8px;">
        管理员请点：<router-link to="/admin-login">管理员专属登录</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { userLogin, checkAdmin } from '@/api/authApi'
// ✅ 核心修改1：手动导入路由实例，解决 this.$router 失效问题
import router from '@/router'

export default {
  name: 'AuthLogin',
  data() {
    return {
      username: '',
      password: ''
    }
  },
  methods: {
    async login() {
      if (!this.username || !this.password) return alert('请输入用户名和密码')
      try {
        const res = await userLogin({ username: this.username, password: this.password })
        // 标记为已登录（后端未必返回 token，这里以登录成功为准）
        localStorage.setItem('isLogin', 'true')
        // 如果后端返回 token，一并保存（可选）
        res.data?.token && localStorage.setItem('token', res.data.token)

        // 校验是否为管理员并记录
        try {
          const adminRes = await checkAdmin()
          const isAdmin = !!(adminRes.data && adminRes.data.is_admin)
          localStorage.setItem('isAdmin', isAdmin ? 'true' : 'false')
          router.push(isAdmin ? '/admin-home' : '/welcome')
        } catch (e) {
          // 若校验管理员失败，也允许普通用户登录
          localStorage.setItem('isAdmin', 'false')
          router.push('/welcome')
        }
      } catch (err) {
        alert('登录失败：' + (err.response?.data?.msg || '服务器异常'))
      }
    }
  }
}
</script>

<style scoped>
.login-page {
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