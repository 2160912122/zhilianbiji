import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/',
    component: () => import('@/layout/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      {
        path: 'notes',
        name: 'Notes',
        component: () => import('@/views/Notes.vue')
      },
      {
        path: 'notes/new',
        name: 'NoteNew',
        component: () => import('@/views/NoteEditor.vue'),
        props: { isNew: true }
      },
      {
        path: 'notes/:id',
        name: 'NoteEdit',
        component: () => import('@/views/NoteEditor.vue')
      },
      {
        path: 'tables',
        name: 'Tables',
        component: () => import('@/views/Tables.vue')
      },
      {
        path: 'tables/new',
        name: 'TableNew',
        component: () => import('@/views/TableEditor.vue'),
        props: { isNew: true }
      },
      {
        path: 'tables/:id',
        name: 'TableEdit',
        component: () => import('@/views/TableEditor.vue')
      },
      {
        path: 'whiteboards',
        name: 'Whiteboards',
        component: () => import('@/views/Whiteboards.vue')
      },
      {
        path: 'whiteboards/new',
        name: 'WhiteboardNew',
        component: () => import('@/views/WhiteboardEditor.vue'),
        props: { isNew: true }
      },
      {
        path: 'whiteboards/:id',
        name: 'WhiteboardEdit',
        component: () => import('@/views/WhiteboardEditor.vue')
      },
      {
        path: 'mindmaps',
        name: 'Mindmaps',
        component: () => import('@/views/Mindmaps.vue')
      },
      {
        path: 'mindmaps/new',
        name: 'MindmapNew',
        component: () => import('@/views/MindmapEditor.vue'),
        props: { isNew: true }
      },
      {
        path: 'mindmaps/:id',
        name: 'MindmapEdit',
        component: () => import('@/views/MindmapEditor.vue')
      },
      {
        path: 'flowcharts',
        name: 'Flowcharts',
        component: () => import('@/views/Flowcharts.vue')
      },
      {
        path: 'flowcharts/new',
        name: 'FlowchartNew',
        component: () => import('@/views/FlowchartEditor.vue'),
        props: { isNew: true }
      },
      {
        path: 'flowcharts/:id',
        name: 'FlowchartEdit',
        component: () => import('@/views/FlowchartEditor.vue')
      },
      {
        path: 'categories',
        name: 'Categories',
        component: () => import('@/views/Categories.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'tags',
        name: 'Tags',
        component: () => import('@/views/Tags.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'admin',
        name: 'Admin',
        component: () => import('@/views/Admin.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'admin/user-manage',
        name: 'UserManage',
        component: () => import('@/views/UserManage.vue'),
        meta: { requiresAdmin: true }
      }

    ]
  },
  // 404重定向简化，避免任何读取异常
  {
    path: '/share/:token',
    name: 'SharedContent',
    component: () => import('@/views/SharedContent.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 极简拦截器：只保留必要逻辑，杜绝冲突
router.beforeEach((to, from, next) => {
    // 强制容错：防止localStorage读取失败
    let token = ''
    try {
      token = localStorage.getItem('token') || ''
    } catch (e) {
      token = ''
    }

    // 1. 访问登录/注册页：如果有token，直接跳dashboard
    if (to.meta.requiresGuest && token) {
      next('/dashboard')
      return
    }

    // 2. 访问需要权限的页面：没token才跳登录
    if (to.meta.requiresAuth && !token) {
      next('/login')
      return
    }

    // 3. 访问需要管理员权限的页面：非管理员跳dashboard
    if (to.meta.requiresAdmin && token) {
      let isAdmin = false
      try {
        // 从localStorage检查，支持多种格式
        const storedIsAdmin = localStorage.getItem('is_admin')
        isAdmin = storedIsAdmin === '1' || storedIsAdmin === 1 || storedIsAdmin === true
        
        // 额外从user对象检查
        const userStr = localStorage.getItem('user')
        if (userStr) {
          const user = JSON.parse(userStr)
          if (user.is_admin === 1 || user.is_admin === true) {
            isAdmin = true
          }
        }
      } catch (e) {
        isAdmin = false
      }
      
      if (!isAdmin) {
        alert('无管理员权限')
        next('/dashboard')
        return
      }
    }

    // 所有情况都放行
    next()
  })

export default router