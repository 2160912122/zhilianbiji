<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <div class="not-found-icon">
        <i class="fa fa-exclamation-triangle"></i>
      </div>
      <h1 class="not-found-title">404</h1>
      <h2 class="not-found-subtitle">页面未找到</h2>
      <p class="not-found-description">
        抱歉，您访问的页面不存在或已被删除
      </p>
      <button class="back-home-btn" @click="goHome">
        <i class="fa fa-home"></i>
        返回首页
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.not-found-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  padding: 20px;
}

.not-found-content {
  text-align: center;
  max-width: 500px;
  background-color: white;
  padding: 4rem 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.not-found-icon {
  font-size: 6rem;
  color: #f59e0b;
  margin-bottom: 1.5rem;
}

.not-found-title {
  font-size: 4rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 0.5rem;
}

.not-found-subtitle {
  font-size: 1.5rem;
  color: #334155;
  margin: 0 0 1rem;
}

.not-found-description {
  color: #64748b;
  font-size: 1rem;
  margin: 0 0 2rem;
  line-height: 1.5;
}

.back-home-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 2rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.back-home-btn:hover {
  background-color: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

@media (max-width: 768px) {
  .not-found-title {
    font-size: 3rem;
  }
  
  .not-found-icon {
    font-size: 4rem;
  }
  
  .not-found-content {
    padding: 3rem 1.5rem;
  }
}
</style>