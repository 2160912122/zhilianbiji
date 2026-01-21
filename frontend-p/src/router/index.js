import { createRouter, createWebHistory } from 'vue-router'
import { getCurrentUser } from '../utils/auth'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/document-manager',
    name: 'DocumentManager',
    component: () => import('../views/DocumentManagerView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue')
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/AdminView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/document/:id',
    name: 'Document',
    component: () => import('../views/DocumentView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const currentUser = getCurrentUser()
  
  // 需要登录的页面
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!currentUser) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
    } else {
      // 需要管理员权限的页面
      if (to.matched.some(record => record.meta.requiresAdmin)) {
        if (currentUser.role === 'admin') {
          next()
        } else {
          next({ name: 'Home' })
        }
      } else {
        next()
      }
    }
  } else {
    next()
  }
})

export default router