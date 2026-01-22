<template>
  <div class="welcome-page">
    <div class="welcome-container">
      <h1 class="welcome-title">欢迎使用智联笔记！</h1>
      <div class="welcome-buttons">
        <button class="btn-create" @click="handleCreateMindMap">创建脑图</button>
        <button class="btn-collaborate" @click="handleCollaborate">多人协作</button>
      </div>
    </div>
  </div>
</template>

<script setup name="WelcomePage">
import { useRouter } from 'vue-router'
import { showToast } from 'vant'

const router = useRouter()


// 处理创建脑图按钮点击
const handleCreateMindMap = () => {
  // 跳转到Home页面，默认进入编辑模式
  router.push('/home')
}

// 处理多人协作按钮点击
const handleCollaborate = () => {
  // 这里可以添加多人协作的逻辑
  showToast('多人协作功能开发中')
}
</script>

<style lang="scss" scoped>
.welcome-page {
  min-height: calc(100vh - 48px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.welcome-container {
  text-align: center;
  background: rgba(255, 255, 255, 0.95);
  padding: 60px;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  width: 90%;
}

.welcome-title {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin-bottom: 40px;
  line-height: 1.4;
}

.welcome-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-create,
.btn-collaborate {
  padding: 14px 32px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.btn-create {
  background: #1989fa;
  color: white;
}

.btn-create:hover {
  background: #3296fa;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(25, 137, 250, 0.3);
}

.btn-create:active {
  transform: translateY(0);
  box-shadow: 0 4px 12px rgba(25, 137, 250, 0.2);
}

.btn-collaborate {
  background: #52c41a;
  color: white;
}

.btn-collaborate:hover {
  background: #73d13d;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(82, 196, 26, 0.3);
}

.btn-collaborate:active {
  transform: translateY(0);
  box-shadow: 0 4px 12px rgba(82, 196, 26, 0.2);
}

// 响应式设计
@media (max-width: 480px) {
  .welcome-container {
    padding: 40px 20px;
  }
  
  .welcome-title {
    font-size: 24px;
    margin-bottom: 30px;
  }
  
  .welcome-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .btn-create,
  .btn-collaborate {
    width: 200px;
  }
}
</style>