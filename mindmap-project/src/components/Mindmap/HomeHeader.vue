<template>
  <div class="home-header">
    <div class="header-title">智联笔记</div>
    <div class="header-right">
      <template v-if="props.currentUser?.username">
        <span class="username">{{ props.currentUser.username }}</span>
        <span class="divider">|</span>
        <button class="logout-btn" @click="emit('logout')">退出</button>
      </template>
      <template v-else>
        <button class="login-btn" @click="emit('login')">登录</button>
      </template>
    </div>
  </div>
</template>

<script setup name="HomeHeader">
import { defineEmits, defineProps } from 'vue'
// 定义子传父事件
const emit = defineEmits(['logout', 'login'])

// 接收父组件传递的用户信息
const props = defineProps({
  currentUser: {
    type: Object,
    default: () => {}
  }
})
</script>

<style lang="scss" scoped>
.home-header {
  height: 48px;
  background: #1989fa;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  color: white;
  font-size: 16px;
}

.header-title {
  font-size: 18px;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  font-size: 14px;
}

.divider {
  color: rgba(255, 255, 255, 0.7);
}

.logout-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.8);
  color: white;
  font-size: 14px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.3s ease;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.logout-btn:hover {
  background-color: rgba(255, 255, 255, 0.3);
  border-color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.logout-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.login-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.8);
  color: white;
  font-size: 14px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.3s ease;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.login-btn:hover {
  background-color: rgba(255, 255, 255, 0.3);
  border-color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.login-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>