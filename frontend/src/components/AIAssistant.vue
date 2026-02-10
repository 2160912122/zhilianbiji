<template>
  <div class="ai-assistant">
    <div class="ai-header">
      <h3>AI助手</h3>
      <el-button
        link
        size="small"
        @click="$emit('close')"
      >
        <el-icon><Close /></el-icon>
      </el-button>
    </div>
    <div class="ai-content">
      <div class="ai-messages">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['ai-message', message.type]"
        >
          <div class="message-avatar">
            <el-icon v-if="message.type === 'user'">
              <UserFilled />
            </el-icon>
            <el-icon v-else>
              <ChatDotRound />
            </el-icon>
          </div>
          <div class="message-content">{{ message.content }}</div>
        </div>
      </div>
      <div class="ai-input-area">
        <el-input
          v-model="inputMessage"
          placeholder="请输入您的问题..."
          @keyup.enter="sendMessage"
          clearable
        >
          <template #append>
            <el-button
              type="primary"
              @click="sendMessage"
              :disabled="!inputMessage.trim() || isLoading"
              :loading="isLoading"
            >
              发送
            </el-button>
          </template>
        </el-input>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Close, UserFilled, ChatDotRound } from '@element-plus/icons-vue'
import { aiAPI } from '@/api/ai'
import { ElMessage } from 'element-plus'
import { useAIStore } from '@/store/ai'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

defineEmits(['close'])

// 初始化AI store
const aiStore = useAIStore()

const messages = ref([
  {
    type: 'ai',
    content: '您好！我是您的AI助手，有什么可以帮助您的吗？'
  }
])

const inputMessage = ref('')
const isLoading = ref(false)

const sendMessage = async () => {
    if (!inputMessage.value.trim()) return
    
    // 添加用户消息
    messages.value.push({
      type: 'user',
      content: inputMessage.value
    })
    
    const userMessage = inputMessage.value
    inputMessage.value = ''
    
    // 调用AI接口获取回复
    isLoading.value = true
    try {
      // 转换消息格式为AI API要求的格式
      const aiMessages = messages.value.map(msg => ({
        role: msg.type === 'user' ? 'user' : 'assistant',
        content: msg.content
      }))
      
      console.log('发送AI请求:', aiMessages)
      const response = await aiAPI.chat(aiMessages)
      console.log('收到AI响应:', response)
      
      if (response.code === 200) {
        // 添加AI回复
        messages.value.push({
          type: 'ai',
          content: response.data.content
        })
        
        // 将AI生成的内容设置到store中，以便NoteEditor可以使用
        aiStore.setGeneratedContent(response.data.content)
      } else {
        ElMessage.error(response.message || 'AI回复失败')
      }
    } catch (error) {
      console.error('AI请求错误:', error)
      ElMessage.error('服务器错误，请稍后重试')
    } finally {
      isLoading.value = false
    }
  }
</script>

<style scoped>
.ai-assistant {
  width: 100%;
  height: 100%;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.ai-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
  font-size: 16px;
  font-weight: 600;
}

.ai-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: 16px;
  overflow: hidden;
}

.ai-messages {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ai-message {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.ai-message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ai-message.ai .message-avatar {
  background-color: #ecf5ff;
  color: #409eff;
}

.ai-message.user .message-avatar {
  background-color: #f0f9eb;
  color: #67c23a;
}

.message-content {
  max-width: 70%;
  padding: 8px 12px;
  border-radius: 4px;
  line-height: 1.5;
}

.ai-message.ai .message-content {
  background-color: #ecf5ff;
  color: #333;
  border-radius: 0 8px 8px 8px;
}

.ai-message.user .message-content {
  background-color: #f0f9eb;
  color: #333;
  border-radius: 8px 0 8px 8px;
}

.ai-input-area {
  display: flex;
  gap: 8px;
}
</style>
