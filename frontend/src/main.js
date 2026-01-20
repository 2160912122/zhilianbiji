import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import service from './utils/request'

// 👇 页面加载时，自动给localStorage塞一个假Token（跳过登录校验）
localStorage.setItem('token', 'fake-token-123456')

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
// 挂载axios到全局（可选）
app.config.globalProperties.$axios = service
app.mount('#app')