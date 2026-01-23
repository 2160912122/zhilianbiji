import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src') // 保留@别名，方便前端导入
    }
  },
  server: {
    port: 5173, // 前端端口
    open: true, // 启动自动打开浏览器
    cors: true, // 兜底跨域配置
    proxy: {
      '/api': {
        target: 'http://localhost:5000', // Flask后端地址
        changeOrigin: true, // 必须开启
        ws: true,
      }
    }
  }
})