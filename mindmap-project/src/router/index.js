// src/router/index.js 【最终完美版，匹配后端所有路由，零报错】
import { createRouter, createWebHashHistory } from 'vue-router'

// 路径全部匹配你的真实目录
import Login from '@/components/Auth/Login.vue'
import Register from '@/components/Auth/Register.vue'
import AdminLogin from '@/components/Auth/AdminLogin.vue'
import Home from '@/components/Mindmap/Home.vue'
import WelcomePage from '@/components/Mindmap/WelcomePage.vue'
import AdminHome from '@/components/Mindmap/AdminHome.vue'
import ShareMindmap from '@/components/Mindmap/ShareMindmap.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/admin-login', component: AdminLogin },
  { path: '/welcome', component: WelcomePage, meta: { requiresAuth: true } },
  { path: '/home', component: Home, meta: { requiresAuth: true } },
  { path: '/admin-home', component: AdminHome, meta: { requiresAuth: true, isAdmin: true } },
  { path: '/share/:share_type/:mid', component: ShareMindmap } // 匹配后端/share/<share_type>/<mid>路由格式
]

const router = createRouter({
  // 使用 hash 模式，避免直接打开 /login 时由服务器返回 404
  history: createWebHashHistory(),
  routes
})

// ✅ 核心修复：路由守卫逻辑（适配后端session+cookie认证，无token）
router.beforeEach((to, from, next) => {
  // 白名单：无需登录即可访问
  const whiteList = ['/login', '/register', '/admin-login']
  if (whiteList.includes(to.path) || to.path.startsWith('/share/')) {
    return next()
  }
  
  // 核心：判断是否登录（后端用session，前端无需存token，通过接口判断登录态）
  const isLogin = localStorage.getItem('isLogin') === 'true'
  const isAdmin = localStorage.getItem('isAdmin') === 'true'

  if (!isLogin) {
    // 未登录：跳转到对应登录页
    const redirectPath = to.path.includes('admin') ? '/admin-login' : '/login'
    return next(redirectPath)
  }

  // 已登录：判断是否是管理员路由
  if (to.meta.isAdmin && !isAdmin) {
    // showToast 未定义，使用 window.alert 代替以保证提示并避免 ESLint no-undef 错误
    window.alert('暂无管理员权限')
    return next('/welcome')
  }

  next()
})

export default router