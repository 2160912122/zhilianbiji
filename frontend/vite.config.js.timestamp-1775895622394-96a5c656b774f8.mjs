// vite.config.js
import { defineConfig } from "file:///D:/zhilianbiji/frontend/node_modules/vite/dist/node/index.js";
import vue from "file:///D:/zhilianbiji/frontend/node_modules/@vitejs/plugin-vue/dist/index.mjs";
import { resolve } from "path";
var __vite_injected_original_dirname = "D:\\zhilianbiji\\frontend";
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
      },
      "/wbo": {
        target: "http://localhost:8080",
        // Whitebophir白板服务
        changeOrigin: true,
        ws: true,
        rewrite: (path) => path.replace(/^\/wbo/, "")
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
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcuanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJEOlxcXFx6aGlsaWFuYmlqaVxcXFxmcm9udGVuZFwiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9maWxlbmFtZSA9IFwiRDpcXFxcemhpbGlhbmJpamlcXFxcZnJvbnRlbmRcXFxcdml0ZS5jb25maWcuanNcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfaW1wb3J0X21ldGFfdXJsID0gXCJmaWxlOi8vL0Q6L3poaWxpYW5iaWppL2Zyb250ZW5kL3ZpdGUuY29uZmlnLmpzXCI7aW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSAndml0ZSdcbmltcG9ydCB2dWUgZnJvbSAnQHZpdGVqcy9wbHVnaW4tdnVlJ1xuaW1wb3J0IHsgcmVzb2x2ZSB9IGZyb20gJ3BhdGgnXG5cbmV4cG9ydCBkZWZhdWx0IGRlZmluZUNvbmZpZyh7XG4gIHBsdWdpbnM6IFt2dWUoKV0sXG4gIHJlc29sdmU6IHtcbiAgICBhbGlhczoge1xuICAgICAgJ0AnOiByZXNvbHZlKF9fZGlybmFtZSwgJ3NyYycpIC8vIFx1NEZERFx1NzU1OUBcdTUyMkJcdTU0MERcdUZGMENcdTY1QjlcdTRGQkZcdTUyNERcdTdBRUZcdTVCRkNcdTUxNjVcbiAgICB9XG4gIH0sXG4gIHNlcnZlcjoge1xuICAgIHBvcnQ6IDUxNzMsIC8vIFx1NTI0RFx1N0FFRlx1N0FFRlx1NTNFM1xuICAgIG9wZW46IHRydWUsIC8vIFx1NTQyRlx1NTJBOFx1ODFFQVx1NTJBOFx1NjI1M1x1NUYwMFx1NkQ0Rlx1ODlDOFx1NTY2OFxuICAgIGNvcnM6IHRydWUsIC8vIFx1NTE1Q1x1NUU5NVx1OERFOFx1NTdERlx1OTE0RFx1N0Y2RVxuICAgIHByb3h5OiB7XG4gICAgICAnL2FwaSc6IHtcbiAgICAgICAgdGFyZ2V0OiAnaHR0cDovL2xvY2FsaG9zdDo1MDAwJywgLy8gRmxhc2tcdTU0MEVcdTdBRUZcdTU3MzBcdTU3NDBcbiAgICAgICAgY2hhbmdlT3JpZ2luOiB0cnVlLCAvLyBcdTVGQzVcdTk4N0JcdTVGMDBcdTU0MkZcbiAgICAgICAgd3M6IHRydWUsXG4gICAgICB9LFxuICAgICAgJy9zaGFyZSc6IHtcbiAgICAgICAgdGFyZ2V0OiAnaHR0cDovL2xvY2FsaG9zdDo1MDAwJywgLy8gRmxhc2tcdTU0MEVcdTdBRUZcdTU3MzBcdTU3NDBcbiAgICAgICAgY2hhbmdlT3JpZ2luOiB0cnVlLCAvLyBcdTVGQzVcdTk4N0JcdTVGMDBcdTU0MkZcbiAgICAgICAgd3M6IHRydWUsXG4gICAgICB9LFxuICAgICAgJy93Ym8nOiB7XG4gICAgICAgIHRhcmdldDogJ2h0dHA6Ly9sb2NhbGhvc3Q6ODA4MCcsIC8vIFdoaXRlYm9waGlyXHU3NjdEXHU2NzdGXHU2NzBEXHU1MkExXG4gICAgICAgIGNoYW5nZU9yaWdpbjogdHJ1ZSxcbiAgICAgICAgd3M6IHRydWUsXG4gICAgICAgIHJld3JpdGU6IChwYXRoKSA9PiBwYXRoLnJlcGxhY2UoL15cXC93Ym8vLCAnJylcbiAgICAgIH1cbiAgICB9LFxuICAgIGZzOiB7XG4gICAgICBzdHJpY3Q6IGZhbHNlXG4gICAgfVxuICB9XG59KSJdLAogICJtYXBwaW5ncyI6ICI7QUFBNlAsU0FBUyxvQkFBb0I7QUFDMVIsT0FBTyxTQUFTO0FBQ2hCLFNBQVMsZUFBZTtBQUZ4QixJQUFNLG1DQUFtQztBQUl6QyxJQUFPLHNCQUFRLGFBQWE7QUFBQSxFQUMxQixTQUFTLENBQUMsSUFBSSxDQUFDO0FBQUEsRUFDZixTQUFTO0FBQUEsSUFDUCxPQUFPO0FBQUEsTUFDTCxLQUFLLFFBQVEsa0NBQVcsS0FBSztBQUFBO0FBQUEsSUFDL0I7QUFBQSxFQUNGO0FBQUEsRUFDQSxRQUFRO0FBQUEsSUFDTixNQUFNO0FBQUE7QUFBQSxJQUNOLE1BQU07QUFBQTtBQUFBLElBQ04sTUFBTTtBQUFBO0FBQUEsSUFDTixPQUFPO0FBQUEsTUFDTCxRQUFRO0FBQUEsUUFDTixRQUFRO0FBQUE7QUFBQSxRQUNSLGNBQWM7QUFBQTtBQUFBLFFBQ2QsSUFBSTtBQUFBLE1BQ047QUFBQSxNQUNBLFVBQVU7QUFBQSxRQUNSLFFBQVE7QUFBQTtBQUFBLFFBQ1IsY0FBYztBQUFBO0FBQUEsUUFDZCxJQUFJO0FBQUEsTUFDTjtBQUFBLE1BQ0EsUUFBUTtBQUFBLFFBQ04sUUFBUTtBQUFBO0FBQUEsUUFDUixjQUFjO0FBQUEsUUFDZCxJQUFJO0FBQUEsUUFDSixTQUFTLENBQUMsU0FBUyxLQUFLLFFBQVEsVUFBVSxFQUFFO0FBQUEsTUFDOUM7QUFBQSxJQUNGO0FBQUEsSUFDQSxJQUFJO0FBQUEsTUFDRixRQUFRO0FBQUEsSUFDVjtBQUFBLEVBQ0Y7QUFDRixDQUFDOyIsCiAgIm5hbWVzIjogW10KfQo=
