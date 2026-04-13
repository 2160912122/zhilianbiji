import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresGuest: true }
  },
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
        path: 'search',
        name: 'SearchResults',
        component: () => import('@/views/SearchResults.vue')
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue')
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue')
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
        path: 'trash',
        name: 'Trash',
        component: () => import('@/views/Trash.vue')
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
        path: 'knowledge-graphs',
        name: 'KnowledgeGraphs',
        component: () => import('@/views/KnowledgeGraphs.vue')
      },
      {
        path: 'knowledge-graphs/new',
        name: 'KnowledgeGraphNew',
        component: () => import('@/views/KnowledgeGraphEditor.vue'),
        props: { isNew: true }
      },
      {
        path: 'knowledge-graphs/:id',
        name: 'KnowledgeGraphEdit',
        component: () => import('@/views/KnowledgeGraphEditor.vue')
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
      },
      {
        path: 'admin/note-manage',
        name: 'NoteManage',
        component: () => import('@/views/NoteManage.vue'),
        meta: { requiresAdmin: true }
      }

    ]
  },
  {
    path: '/share/:token',
    name: 'SharedContent',
    component: () => import('@/views/SharedContent.vue')
  },
  {
    path: '/test',
    name: 'Test',
    component: () => import('@/views/Test.vue')
  },
  {
    path: '/test/:id',
    name: 'TestDynamic',
    component: () => import('@/views/Test.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
    let token = ''
    try {
      token = localStorage.getItem('token') || ''
    } catch (e) {
      token = ''
    }

    if (to.path.startsWith('/share/')) {
      next()
      return
    }

    if (to.meta.requiresGuest && token) {
      next('/dashboard')
      return
    }

    if (to.meta.requiresAuth && !token) {
      next('/')
      return
    }

    if (to.meta.requiresAdmin && token) {
      let isAdmin = false
      try {
        const storedIsAdmin = localStorage.getItem('is_admin')
        isAdmin = storedIsAdmin === '1' || storedIsAdmin === 1 || storedIsAdmin === true
        
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

    next()
  })

export default router
