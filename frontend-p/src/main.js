import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 导入样式
import './style.css'
import '@fortawesome/fontawesome-free/css/all.min.css'

// 导入路由配置
import router from './router'

// 创建Vue应用
const app = createApp(App)

// 使用路由
app.use(router)
// 使用Element-Plus
app.use(ElementPlus)

// 挂载应用
app.mount('#app')
