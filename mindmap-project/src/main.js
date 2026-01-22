// src/main.js 【Vue3完整版 最终完美修复版 - 仅改此处，其他无任何修改】
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// ============ 1. 全局引入 jsmind 核心样式 ✅ 直接从node_modules引入
import 'jsmind/style/jsmind.css'

// ============ 2. 全局引入 jsmind 核心JS + 插件 ✅ 直接从node_modules引入
window.jsMind = require('jsmind')
require('jsmind/draggable-node')

// ============ 3. 引入全局样式 ============
import './assets/style.css'

// ============ 4. 引入Font Awesome字体图标库 ============
import '@fortawesome/fontawesome-free/css/all.css'
// 引入 Vant 样式（部分页面使用 Vant 组件）
import 'vant/lib/index.css'
import { Button, Icon, Cell, CellGroup, Field, Popup, Tag, ShareSheet, ActionSheet, Dialog, Notify, Toast, NavBar, DropdownMenu, DropdownItem, Loading } from 'vant'

// ============ 5. Vue3 正确挂载axios ============
import axios from 'axios'
const app = createApp(App)
app.config.globalProperties.$axios = axios

// 全局注册常用 Vant 组件
app.use(Button)
app.use(Icon)
app.use(Cell)
app.use(CellGroup)
app.use(Field)
app.use(Popup)
app.use(Tag)
app.use(ShareSheet)
app.use(ActionSheet)
app.use(Dialog)
app.use(Notify)
app.use(Toast)
app.use(NavBar)
app.use(DropdownMenu)
app.use(DropdownItem)
app.use(Loading)

// ============ 6. 挂载路由并启动 ============
app.use(router).mount('#app')