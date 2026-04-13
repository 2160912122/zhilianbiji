<template>
  <div v-if="showOnPage" class="ai-floating-container">
    <!-- AI侧拉面板 -->
    <div
      v-if="showSidePanel"
      class="ai-side-panel"
      :class="{ 'show': showSidePanel }"
    >
      <div class="panel-header">
        <h3>AI助手</h3>
        <el-button
          link
          size="small"
          @click="showSidePanel = false"
        >
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
      <div class="panel-content">
        <div class="model-section">
          <h4>Doubao-Seed-2.0-pro</h4>
          <p class="model-description">火山方舟最新的AI模型，支持多轮对话、内容创作、知识问答、图片分析等功能。</p>
          <el-button
            type="primary"
            class="chat-button"
            @click="openChat"
          >
            开始聊天
          </el-button>
        </div>
        <div class="feature-buttons">
          <h5>快捷功能</h5>
          <div class="button-grid">
            <el-button
              type="default"
              class="feature-btn"
              @click="openChatWithAction('upload-file')"
            >
              <el-icon><Upload /></el-icon>
              <span>上传文件</span>
            </el-button>
            <el-button
              type="default"
              class="feature-btn"
              @click="openChatWithAction('upload-image')"
            >
              <el-icon><Picture /></el-icon>
              <span>上传图片</span>
            </el-button>
            <el-button
              type="default"
              class="feature-btn"
              @click="openChatWithAction('upload-video')"
            >
              <el-icon><VideoCamera /></el-icon>
              <span>上传视频</span>
            </el-button>
          </div>
        </div>
        <div class="model-features">
          <h5>模型能力</h5>
          <ul>
            <li>智能对话</li>
            <li>内容创作</li>
            <li>知识问答</li>
            <li>代码生成</li>
            <li>图片分析</li>
            <li>文档分析</li>
          </ul>
        </div>
      </div>
    </div>
    
    <!-- AI聊天面板 -->
    <div
      v-if="showChatPanel"
      class="ai-chat-panel"
      :class="{ 'show': showChatPanel }"
    >
      <AIAssistant 
        @close="closeChat"
        :action="selectedAction"
        @action-completed="selectedAction = null"
      />
    </div>
    
    <!-- AI浮动按钮 -->
    <div
      class="ai-floating-btn"
      @click="toggleSidePanel"
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
import { ChatDotRound, Close, Upload, Picture, Camera } from '@element-plus/icons-vue'
import AIAssistant from './AIAssistant.vue'

const props = defineProps({
  showOnPage: {
    type: Boolean,
    default: true
  }
})

const showSidePanel = ref(false)
const showChatPanel = ref(false)
const selectedAction = ref(null)

const toggleSidePanel = () => {
  showSidePanel.value = !showSidePanel.value
  if (showSidePanel.value) {
    showChatPanel.value = false
  }
}

const openChat = () => {
  showSidePanel.value = false
  showChatPanel.value = true
  selectedAction.value = null
}

const openChatWithAction = (action) => {
  showSidePanel.value = false
  showChatPanel.value = true
  selectedAction.value = action
}

const closeChat = () => {
  showChatPanel.value = false
  selectedAction.value = null
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

.ai-side-panel {
  width: 360px;
  height: 450px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  transform: translateX(100%);
  opacity: 0;
  transition: all 0.3s ease;
  overflow: hidden;
  position: absolute;
  bottom: 90px;
  right: 0;
  border: 1px solid #e8e8e8;
}

.ai-side-panel.show {
  transform: translateX(-15px);
  opacity: 1;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  font-size: 18px;
  font-weight: 600;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
}

.panel-content {
  padding: 20px;
  height: calc(100% - 64px);
  overflow-y: auto;
}

.model-section {
  margin-bottom: 24px;
}

.model-section h4 {
  margin-bottom: 12px;
  color: #303133;
  font-size: 16px;
}

.model-description {
  margin-bottom: 20px;
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  background-color: #f9f9f9;
  padding: 12px;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.chat-button {
  width: 100%;
  margin-bottom: 24px;
  padding: 12px;
  font-size: 16px;
  border-radius: 8px;
  background: linear-gradient(135deg, #409eff 0%, #3a8ee6 100%);
  border: none;
  transition: all 0.3s ease;
}

.chat-button:hover {
  background: linear-gradient(135deg, #3a8ee6 0%, #3071e7 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.feature-buttons {
  margin-bottom: 24px;
}

.feature-buttons h5 {
  margin-bottom: 12px;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.button-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
}

.feature-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px 8px;
  border-radius: 12px;
  border: 1px solid #e8e8e8;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  transition: all 0.3s ease;
  height: 90px;
  position: relative;
  overflow: visible;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  white-space: nowrap;
  text-align: center;
}

.feature-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #409eff, #69b1ff);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.feature-btn:hover {
  border-color: #409eff;
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.feature-btn:hover::before {
  transform: scaleX(1);
}

.feature-btn .el-icon {
  font-size: 28px;
  margin-bottom: 10px;
  color: #409eff;
  transition: all 0.3s ease;
}

.feature-btn:hover .el-icon {
  transform: scale(1.1);
  color: #3a8ee6;
}

.feature-btn span {
  font-size: 11px;
  color: #606266;
  font-weight: 500;
  transition: all 0.3s ease;
  line-height: 1.2;
  max-width: 100%;
  overflow: visible;
}

.feature-btn:hover span {
  color: #303133;
}

.model-features h5 {
  margin-bottom: 12px;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.model-features ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.model-features li {
  padding: 10px 0;
  font-size: 14px;
  color: #606266;
  display: flex;
  align-items: center;
  transition: all 0.2s ease;
  border-radius: 4px;
  padding-left: 12px;
}

.model-features li:hover {
  background-color: #ecf5ff;
  color: #409eff;
  margin-left: -12px;
}

.model-features li::before {
  content: "✓";
  color: #409eff;
  font-weight: bold;
  margin-right: 8px;
  font-size: 12px;
}

.ai-chat-panel {
  width: 450px;
  height: 600px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  transform: translateY(100%);
  opacity: 0;
  transition: all 0.3s ease;
  overflow: visible;
  position: absolute;
  bottom: 90px;
  right: 0;
  border: 1px solid #e8e8e8;
  z-index: 9999;
}

.ai-chat-panel.show {
  transform: translateY(0);
  opacity: 1;
}

.ai-floating-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 65px;
  height: 65px;
  background: linear-gradient(135deg, #409eff 0%, #3a8ee6 100%);
  color: white;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.4);
  transition: all 0.3s ease;
  position: relative;
  z-index: 10000;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.ai-floating-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.5);
  background: linear-gradient(135deg, #3a8ee6 0%, #3071e7 100%);
}

.ai-icon {
  font-size: 28px;
}

.ai-btn-text {
  position: absolute;
  right: 100%;
  margin-right: 12px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  white-space: nowrap;
  opacity: 0;
  transform: translateX(10px);
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.ai-floating-btn:hover .ai-btn-text {
  opacity: 1;
  transform: translateX(0);
}

/* 滚动条样式 */
.panel-content::-webkit-scrollbar {
  width: 6px;
}

.panel-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.panel-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.panel-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
