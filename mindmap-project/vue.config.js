const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  lintOnSave: false,
  publicPath: './',
  devServer: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        ws: true,
        pathRewrite: { '^/api': '/api' }, // 保持 /api 前缀，确保代理转发到后端的 /api/* 路由
        withCredentials: true // 保留你的配置：允许携带Cookie，必须开启！
      },
      '/share': { // 新增：代理你的分享页面接口，后端有/share路由
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        withCredentials: true
      },
      '/admin': { // 新增：代理管理员接口
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        withCredentials: true
      }
    },
    port: 8080, // 固定前端端口，和你配置一致
    host: '0.0.0.0',
    open: true
  }
})