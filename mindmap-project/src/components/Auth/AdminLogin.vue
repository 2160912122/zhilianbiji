<template>
  <div class="admin-login-page">
    <div class="login-box">
      <h2>🧠 智联笔记 - 管理员登录</h2>
      <div class="alert" v-show="alertMsg" :style="alertStyle">{{ alertMsg }}</div>
      <div class="form-group">
        <label>管理员账号</label>
        <input 
          type="text" 
          v-model="username" 
          placeholder="请输入管理员账号"
        >
      </div>
      <div class="form-group">
        <label>密码</label>
        <input 
          type="password" 
          v-model="password" 
          placeholder="请输入密码"
        >
      </div>
      <button 
        class="login-btn" 
        @click="login"
        :disabled="isLoading"
      >
        {{ isLoading ? '登录中...' : '登录' }}
      </button>
      <div class="back-link">
        <router-link to="/login">← 返回用户登录</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { adminLogin } from '@/api/authApi'
// ✅ 改动1：顶部新增【手动导入路由实例】，解决this.$router无效的问题
import router from '@/router'

export default {
  name: 'AdminLogin',
  data() {
    return {
      username: '',
      password: '',
      alertMsg: '',
      isLoading: false
    }
  },
  computed: {
    alertStyle() {
      return {
        background: this.alertMsg.includes('成功') ? '#f0f9ff' : '#fef0f0',
        color: this.alertMsg.includes('成功') ? '#409eff' : '#f56c6c',
        padding: '10px',
        borderRadius: '4px',
        marginBottom: '20px',
        fontSize: '14px',
        display: this.alertMsg ? 'block' : 'none'
      }
    }
  },
  methods: {
    handleKeyPress(e) {
      if (e.key === 'Enter') this.login()
    },
    async login() {
      const username = this.username.trim()
      const password = this.password
      if (!username || !password) {
        this.alertMsg = '请输入管理员账号和密码'
        return
      }

      this.isLoading = true
      try {
        const res = await adminLogin({ username, password })
        this.alertMsg = '登录成功，正在跳转...'
        
        // ✅ 改动2：把 this.$router.push 替换为 导入的router.push，核心修复跳转无效
        // 【重点】这里手动存一下token到localStorage，解决路由守卫拦截问题！！！
        // 保存登录态与管理员标记，路由守卫会读取这些标记
        localStorage.setItem('isLogin', 'true')
        localStorage.setItem('isAdmin', 'true')
        res.data?.token && localStorage.setItem('token', res.data.token)

        setTimeout(() => {
          router.push('/admin-home')
        }, 500)
      } catch (err) {
        this.alertMsg = err.response?.data?.msg || '网络错误，请重试'
      } finally {
        this.isLoading = false
      }
    }
  },
  mounted() {
    document.addEventListener('keypress', this.handleKeyPress)
  },
  // ✅ 改动3：把 unmounted 改为 beforeDestroy，修复生命周期钩子错误
  beforeUnmount() {
    document.removeEventListener('keypress', this.handleKeyPress)
  }
}
</script>

<style scoped>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei";
}
.admin-login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-box {
  background: #fff;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  width: 400px;
}
.login-box h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-weight: 500;
}
.form-group {
  margin-bottom: 20px;
}
.form-group label {
  display: block;
	margin-bottom: 8px;
	color: #555;
	font-size: 14px;
}
.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s;
}
.form-group input:focus {
  outline: none;
  border-color: #409eff;
}
.login-btn {
  width: 100%;
  padding: 12px;
  background: #409eff;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
}
.login-btn:hover {
  background: #66b1ff;
}
.login-btn:disabled {
  background: #a0cfff;
  cursor: not-allowed;
}
.back-link {
  text-align: center;
  margin-top: 20px;
}
.back-link a {
  color: #409eff;
  text-decoration: none;
  font-size: 14px;
}
.back-link a:hover {
  text-decoration: underline;
}
</style>