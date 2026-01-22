import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

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
      {
        path: '',
        redirect: '/dashboard'
      },
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
        name: 'NoteCreate',
        component: () => import('@/views/NoteEditor.vue'),
        props: { isNew: true }
      },
      {
        path: 'notes/:id',
        name: 'NoteEdit',
        component: () => import('@/views/NoteEditor.vue'),
        props: { isNew: false }
      },
      {
        path: 'tables',
        name: 'Tables',
        component: () => import('@/views/Tables.vue')
      },
      {
        path: 'tables/new',
        name: 'TableCreate',
        component: () => import('@/views/TableEditor.vue'),
        props: { isNew: true }
      },
      {
        path: 'tables/:id',
        name: 'TableEdit',
        component: () => import('@/views/TableEditor.vue'),
        props: { isNew: false }
      },
      {
        path: 'whiteboards',
        name: 'Whiteboards',
        component: () => import('@/views/Whiteboards.vue')
      },
      {
        path: 'whiteboards/new',
        name: 'WhiteboardCreate',
        component: () => import('@/views/WhiteboardEditor.vue'),
        props: { isNew: true }
      },
      {
        path: 'whiteboards/:id',
        name: 'WhiteboardEdit',
        component: () => import('@/views/WhiteboardEditor.vue'),
        props: { isNew: false }
      },
      {
        path: 'mindmaps',
        name: 'Mindmaps',
        component: () => import('@/views/Mindmaps.vue')
      },
      {
        path: 'mindmaps/new',
        name: 'MindmapCreate',
        component: () => import('@/views/MindmapEditor.vue'),
        props: { isNew: true }
      },
      {
        path: 'mindmaps/:id',
        name: 'MindmapEdit',
        component: () => import('@/views/MindmapEditor.vue'),
        props: { isNew: false }
      },
      {
        path: 'flowcharts',
        name: 'Flowcharts',
        component: () => import('@/views/Flowcharts.vue')
      },
      {
        path: 'flowcharts/new',
        name: 'FlowchartCreate',
        component: () => import('@/views/FlowchartEditor.vue'),
        props: { isNew: true }
      },
      {
        path: 'flowcharts/:id',
        name: 'FlowchartEdit',
        component: () => import('@/views/FlowchartEditor.vue'),
        props: { isNew: false }
      },
      {
        path: 'categories',
        name: 'Categories',
        component: () => import('@/views/Categories.vue')
      },
      {
        path: 'tags',
        name: 'Tags',
        component: () => import('@/views/Tags.vue')
      },
      {
        path: 'admin',
        name: 'Admin',
        component: () => import('@/views/Admin.vue'),
        meta: { requiresAdmin: true }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const token = localStorage.getItem('token')

  if (to.meta.requiresAuth && !token) {
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else if (to.meta.requiresGuest && token) {
    next('/dashboard')
  } else if (to.meta.requiresAdmin) {
    if (!token) {
      next({ path: '/login', query: { redirect: to.fullPath } })
    } else if (!userStore.user?.is_admin) {
      next('/dashboard')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
