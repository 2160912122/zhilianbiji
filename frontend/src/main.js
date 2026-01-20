import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import App from './App.vue'
import routes, { setupNavigationGuard } from './router'

const app = createApp(App)
const router = createRouter({
  history: createWebHistory(),
  routes
})
const pinia = createPinia()

// Setup navigation guard after router and pinia are created
app.use(pinia)
app.use(router)
setupNavigationGuard(router)

app.mount('#app')