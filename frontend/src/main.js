import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import './style.css'

// 导入请求工具
import request from './utils/request'

// 移除：启动时的强制跳转（交给路由拦截器统一处理，避免冲突）

const app = createApp(App)
const pinia = createPinia()

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 全局挂载request请求工具
app.config.globalProperties.$request = request

// 注册插件（顺序不变）
app.use(pinia)
app.use(router)
app.use(ElementPlus)

app.mount('#app')

// 修复：简化路由就绪后的逻辑，只做“状态校验”，不强制跳转
// 路由拦截器会统一处理跳转，这里只打印日志方便调试
router.isReady().then(() => {
  const token = localStorage.getItem('token')
  const currentPath = router.currentRoute.value.path

  // 只打印状态，不强制跳转（跳转逻辑完全交给路由拦截器）
  if (token && (currentPath === '/login' || currentPath === '/register')) {
    console.log('检测到已登录，但当前在登录/注册页，路由拦截器会处理跳转')
  } else if (!token && currentPath !== '/login' && currentPath !== '/register') {
    console.log('检测到未登录，且不在登录/注册页，路由拦截器会处理跳转')
  }
})