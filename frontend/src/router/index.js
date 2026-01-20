import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import NoteList from '../views/NoteList.vue'
import NoteDetail from '../views/NoteDetail.vue'
import NoteTypeSelect from '../views/NoteTypeSelect.vue'
import NoteCreate from '../views/NoteCreate.vue'
import NoteEdit from '../views/NoteEdit.vue'
import NoteHistory from '../views/NoteHistory.vue'
import NoteVersionDetail from '../views/NoteVersionDetail.vue'
import NoteShare from '../views/NoteShare.vue'
import CategoryManager from '../views/CategoryManager.vue'
import TagManager from '../views/TagManager.vue'
import AdminPanel from '../views/AdminPanel.vue'
import { useUserStore } from '../store/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresGuest: true }
  },
  {
    path: '/',
    name: 'NoteList',
    component: NoteList,
    meta: { requiresAuth: true }
  },
  {
    path: '/notes',
    redirect: '/',
    meta: { requiresAuth: true }
  },
  {
    path: '/notes/:id',
    name: 'NoteDetail',
    component: NoteDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/notes/create',
    name: 'NoteTypeSelect',
    component: NoteTypeSelect,
    meta: { requiresAuth: true }
  },
  {
    path: '/notes/create/:type',
    name: 'NoteCreate',
    component: NoteCreate,
    meta: { requiresAuth: true }
  },
  {
    path: '/notes/:id/edit',
    name: 'NoteEdit',
    component: NoteEdit,
    meta: { requiresAuth: true }
  },
  {
    path: '/notes/:id/history',
    name: 'NoteHistory',
    component: NoteHistory,
    meta: { requiresAuth: true }
  },
  {
    path: '/notes/:id/versions/:versionId',
    name: 'NoteVersionDetail',
    component: NoteVersionDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/notes/:id/share',
    name: 'NoteShare',
    component: NoteShare,
    meta: { requiresAuth: true }
  },
  {
    path: '/categories',
    name: 'CategoryManager',
    component: CategoryManager,
    meta: { requiresAuth: true }
  },
  {
    path: '/tags',
    name: 'TagManager',
    component: TagManager,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'AdminPanel',
    component: AdminPanel,
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

// Export routes
export default routes

// Navigation guard function
export function setupNavigationGuard(router) {
  router.beforeEach((to, from, next) => {
    const userStore = useUserStore()
    
    if (to.matched.some(record => record.meta.requiresAuth)) {
      if (!userStore.isAuthenticated) {
        next({ name: 'Login' })
      } else {
        if (to.matched.some(record => record.meta.requiresAdmin) && !userStore.user?.is_admin) {
          next({ name: 'NoteList' })
        } else {
          next()
        }
      }
    } else if (to.matched.some(record => record.meta.requiresGuest)) {
      if (userStore.isAuthenticated) {
        next({ name: 'NoteList' })
      } else {
        next()
      }
    } else {
      next()
    }
  })
}