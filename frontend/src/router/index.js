import { createRouter, createWebHistory } from 'vue-router'
// 适配你的文件路径：layout在src/layout/下，views在src/views/下
import MainLayout from '@/layout/MainLayout.vue'
import LoginPage from '@/views/LoginPage.vue'
import DashboardPage from '@/views/DashboardPage.vue'
import UserManagement from '@/views/UserManagement.vue'
import NoteManagement from '@/views/NoteManagement.vue'

// 路由守卫：校验登录状态（优化逻辑，避免重复跳转）
const requireAuth = (to, from, next) => {
  const token = localStorage.getItem('token')
  // 有Token → 正常跳转；无Token → 跳登录页（并记录当前路径，登录后返回）
  if (token) {
    next()
  } else {
    next({ path: '/login', query: { redirect: to.fullPath } })
  }
}

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    // 新增：登录页只允许未登录访问，避免重复登录
    beforeEnter: (to, from, next) => {
      const token = localStorage.getItem('token')
      token ? next('/dashboard') : next()
    }
  },
  {
    path: '/',
    component: MainLayout,
    redirect: '/dashboard',
    beforeEnter: requireAuth, // 父路由统一校验登录
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: DashboardPage
      },
      {
        path: 'user',
        name: 'User',
        component: UserManagement
      },
      {
        path: 'note',
        name: 'Note',
        component: NoteManagement
      }
    ]
  },
  // 新增：404页面（匹配不存在的路由）
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router