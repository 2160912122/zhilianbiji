<template>
  <div v-if="showOnPage" class="ai-floating-container">
    <!-- AI聊天面板 -->
    <div
      v-if="showChatPanel"
      class="ai-chat-panel"
      :class="{ 'show': showChatPanel }"
    >
      <AIAssistant @close="showChatPanel = false" />
    </div>
    
    <!-- AI浮动按钮 -->
    <div
      class="ai-floating-btn"
      @click="toggleChatPanel"
    >
      <el-icon class="ai-icon">
        <ChatDotRound />
      </el-icon>
      <span class="ai-btn-text">AI助手</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ChatDotRound } from '@element-plus/icons-vue'
import AIAssistant from './AIAssistant.vue'

const props = defineProps({
  showOnPage: {
    type: Boolean,
    default: true
  }
})

const showChatPanel = ref(false)

const toggleChatPanel = () => {
  showChatPanel.value = !showChatPanel.value
}
</script>

<style scoped>
.ai-floating-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

.ai-function-menu {
  width: 220px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  transform: translateY(100%);
  opacity: 0;
  transition: all 0.3s ease;
  overflow: hidden;
}

.ai-function-menu.show {
  transform: translateY(0);
  opacity: 1;
}

.menu-title {
  padding: 12px 16px;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #ebeef5;
  background-color: #f5f7fa;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.menu-item:hover {
  background-color: #f5f7fa;
}

.item-icon {
  margin-right: 12px;
  color: #606266;
  font-size: 18px;
}

.item-text {
  font-size: 14px;
  color: #303133;
}

.ai-chat-panel {
  width: 360px;
  height: 500px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  transform: translateY(100%);
  opacity: 0;
  transition: all 0.3s ease;
  overflow: hidden;
}

.ai-chat-panel.show {
  transform: translateY(0);
  opacity: 1;
}

.ai-floating-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
  position: relative;
}

.ai-floating-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.ai-icon {
  font-size: 28px;
}

.ai-btn-text {
  position: absolute;
  right: 100%;
  margin-right: 10px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 14px;
  white-space: nowrap;
  opacity: 0;
  transform: translateX(10px);
  transition: all 0.3s ease;
}

.ai-floating-btn:hover .ai-btn-text {
  opacity: 1;
  transform: translateX(0);
}
</style>
