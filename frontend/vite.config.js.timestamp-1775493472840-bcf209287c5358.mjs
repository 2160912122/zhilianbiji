// vite.config.js
import { defineConfig } from "file:///D:/zhilianzhilian/zhilianbiji(2)/zhilianbiji/frontend/node_modules/vite/dist/node/index.js";
import vue from "file:///D:/zhilianzhilian/zhilianbiji(2)/zhilianbiji/frontend/node_modules/@vitejs/plugin-vue/dist/index.mjs";
import { resolve } from "path";
var __vite_injected_original_dirname = "D:\\zhilianzhilian\\zhilianbiji(2)\\zhilianbiji\\frontend";
var vite_config_default = defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": resolve(__vite_injected_original_dirname, "src")
      // 保留@别名，方便前端导入
    }
  },
  server: {
    port: 5173,
    // 前端端口
    open: true,
    // 启动自动打开浏览器
    cors: true,
    // 兜底跨域配置
    proxy: {
      "/api": {
        target: "http://localhost:5000",
        // Flask后端地址
        changeOrigin: true,
        // 必须开启
        ws: true
      },
      "/share": {
        target: "http://localhost:5000",
        // Flask后端地址
        changeOrigin: true,
        // 必须开启
        ws: true
      }
    },
    fs: {
      strict: false
    }
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcuanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJEOlxcXFx6aGlsaWFuemhpbGlhblxcXFx6aGlsaWFuYmlqaSgyKVxcXFx6aGlsaWFuYmlqaVxcXFxmcm9udGVuZFwiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9maWxlbmFtZSA9IFwiRDpcXFxcemhpbGlhbnpoaWxpYW5cXFxcemhpbGlhbmJpamkoMilcXFxcemhpbGlhbmJpamlcXFxcZnJvbnRlbmRcXFxcdml0ZS5jb25maWcuanNcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfaW1wb3J0X21ldGFfdXJsID0gXCJmaWxlOi8vL0Q6L3poaWxpYW56aGlsaWFuL3poaWxpYW5iaWppKDIpL3poaWxpYW5iaWppL2Zyb250ZW5kL3ZpdGUuY29uZmlnLmpzXCI7aW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSAndml0ZSdcclxuaW1wb3J0IHZ1ZSBmcm9tICdAdml0ZWpzL3BsdWdpbi12dWUnXHJcbmltcG9ydCB7IHJlc29sdmUgfSBmcm9tICdwYXRoJ1xyXG5cclxuZXhwb3J0IGRlZmF1bHQgZGVmaW5lQ29uZmlnKHtcclxuICBwbHVnaW5zOiBbdnVlKCldLFxyXG4gIHJlc29sdmU6IHtcclxuICAgIGFsaWFzOiB7XHJcbiAgICAgICdAJzogcmVzb2x2ZShfX2Rpcm5hbWUsICdzcmMnKSAvLyBcdTRGRERcdTc1NTlAXHU1MjJCXHU1NDBEXHVGRjBDXHU2NUI5XHU0RkJGXHU1MjREXHU3QUVGXHU1QkZDXHU1MTY1XHJcbiAgICB9XHJcbiAgfSxcclxuICBzZXJ2ZXI6IHtcclxuICAgIHBvcnQ6IDUxNzMsIC8vIFx1NTI0RFx1N0FFRlx1N0FFRlx1NTNFM1xyXG4gICAgb3BlbjogdHJ1ZSwgLy8gXHU1NDJGXHU1MkE4XHU4MUVBXHU1MkE4XHU2MjUzXHU1RjAwXHU2RDRGXHU4OUM4XHU1NjY4XHJcbiAgICBjb3JzOiB0cnVlLCAvLyBcdTUxNUNcdTVFOTVcdThERThcdTU3REZcdTkxNERcdTdGNkVcclxuICAgIHByb3h5OiB7XHJcbiAgICAgICcvYXBpJzoge1xyXG4gICAgICAgIHRhcmdldDogJ2h0dHA6Ly9sb2NhbGhvc3Q6NTAwMCcsIC8vIEZsYXNrXHU1NDBFXHU3QUVGXHU1NzMwXHU1NzQwXHJcbiAgICAgICAgY2hhbmdlT3JpZ2luOiB0cnVlLCAvLyBcdTVGQzVcdTk4N0JcdTVGMDBcdTU0MkZcclxuICAgICAgICB3czogdHJ1ZSxcclxuICAgICAgfSxcclxuICAgICAgJy9zaGFyZSc6IHtcclxuICAgICAgICB0YXJnZXQ6ICdodHRwOi8vbG9jYWxob3N0OjUwMDAnLCAvLyBGbGFza1x1NTQwRVx1N0FFRlx1NTczMFx1NTc0MFxyXG4gICAgICAgIGNoYW5nZU9yaWdpbjogdHJ1ZSwgLy8gXHU1RkM1XHU5ODdCXHU1RjAwXHU1NDJGXHJcbiAgICAgICAgd3M6IHRydWUsXHJcbiAgICAgIH1cclxuICAgIH0sXHJcbiAgICBmczoge1xyXG4gICAgICBzdHJpY3Q6IGZhbHNlXHJcbiAgICB9XHJcbiAgfVxyXG59KSJdLAogICJtYXBwaW5ncyI6ICI7QUFBMlYsU0FBUyxvQkFBb0I7QUFDeFgsT0FBTyxTQUFTO0FBQ2hCLFNBQVMsZUFBZTtBQUZ4QixJQUFNLG1DQUFtQztBQUl6QyxJQUFPLHNCQUFRLGFBQWE7QUFBQSxFQUMxQixTQUFTLENBQUMsSUFBSSxDQUFDO0FBQUEsRUFDZixTQUFTO0FBQUEsSUFDUCxPQUFPO0FBQUEsTUFDTCxLQUFLLFFBQVEsa0NBQVcsS0FBSztBQUFBO0FBQUEsSUFDL0I7QUFBQSxFQUNGO0FBQUEsRUFDQSxRQUFRO0FBQUEsSUFDTixNQUFNO0FBQUE7QUFBQSxJQUNOLE1BQU07QUFBQTtBQUFBLElBQ04sTUFBTTtBQUFBO0FBQUEsSUFDTixPQUFPO0FBQUEsTUFDTCxRQUFRO0FBQUEsUUFDTixRQUFRO0FBQUE7QUFBQSxRQUNSLGNBQWM7QUFBQTtBQUFBLFFBQ2QsSUFBSTtBQUFBLE1BQ047QUFBQSxNQUNBLFVBQVU7QUFBQSxRQUNSLFFBQVE7QUFBQTtBQUFBLFFBQ1IsY0FBYztBQUFBO0FBQUEsUUFDZCxJQUFJO0FBQUEsTUFDTjtBQUFBLElBQ0Y7QUFBQSxJQUNBLElBQUk7QUFBQSxNQUNGLFFBQVE7QUFBQSxJQUNWO0FBQUEsRUFDRjtBQUNGLENBQUM7IiwKICAibmFtZXMiOiBbXQp9Cg==
