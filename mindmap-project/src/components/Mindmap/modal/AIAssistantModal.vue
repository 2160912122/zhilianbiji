<template>
  <!-- AI助手弹窗组件 - 完整版 -->
  <van-popup
    v-model:show="isShowModal"
    position="bottom"
    round
    closeable
    close-icon-position="top-right"
    overlay-closeable
    class="ai-assistant-modal"
    @close="handleModalClose"
  >
    <!-- 弹窗头部 -->
    <div class="modal-header">
      <h3 class="title">AI 编程助手</h3>
      <p class="subtitle">智能解答 · 代码优化 · 问题排查</p>
    </div>

    <!-- 主体内容区 -->
    <div class="modal-content">
      <!-- 历史对话/回复内容区 -->
      <div class="chat-content" style="overflow-y: auto;">
        <div class="chat-item ai-chat" v-if="hasAiReply">
          <div class="avatar">AI</div>
          <div class="chat-bubble">{{ aiReplyContent }}</div>
        </div>
        <div class="chat-item user-chat" v-if="userInputVal">
          <div class="avatar">我</div>
          <div class="chat-bubble">{{ userInputVal }}</div>
        </div>
        <div class="empty-tip" v-else>
          有任何编程问题，随时问我吧 💻
        </div>
      </div>

      <!-- 底部输入区 -->
      <div class="input-footer">
        <van-field
          v-model="userInputVal"
          placeholder="请输入你的问题，比如：vue怎么封装组件？"
          type="textarea"
          rows="2"
          autosize
          show-word-limit
          maxlength="500"
          class="input-area"
        />
        <van-button 
          type="primary" 
          round 
          class="send-btn"
          @click="handleSendQuestion"
          :loading="isLoading"
          :disabled="!userInputVal || isLoading"
        >
          {{ isLoading ? '思考中...' : '发送' }}
        </van-button>
      </div>
    </div>
  </van-popup>
</template>

<script setup name="AIAssistantModal">
import { ref, defineEmits, defineProps } from 'vue'

// 1. 父组件传参 - 控制弹窗显示隐藏
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  }
})

// 2. 向外暴露事件
const emit = defineEmits(['update:show', 'onClose', 'onSendQuestion'])

// ===== 响应式数据 =====
// 弹窗显示状态（双向绑定）
const isShowModal = ref(props.show)
// 用户输入的问题
const userInputVal = ref('')
// AI回复的内容
const aiReplyContent = ref('')
// 是否有AI回复内容
const hasAiReply = ref(false)
// 加载状态 - 发送请求时loading
const isLoading = ref(false)

// ===== 监听弹窗显示状态 - 双向绑定核心 =====
import { watch } from 'vue'
watch(
  () => props.show,
  (newVal) => {
    isShowModal.value = newVal
    // 弹窗打开时，重置内容
    if (newVal) {
      resetModalContent()
    }
  },
  { immediate: true }
)

// ===== 核心方法 =====
/**
 * 弹窗关闭事件处理
 */
const handleModalClose = () => {
  resetModalContent()
  emit('update:show', false)
  emit('onClose')
}

/**
 * 发送问题给AI
 */
const handleSendQuestion = async () => {
  const question = userInputVal.value.trim()
  if (!question) return

  isLoading.value = true
  hasAiReply.value = false

  try {
    // 1. 向外派发【发送问题】事件，父组件可在这里对接真实AI接口
    emit('onSendQuestion', question)

    // 模拟AI接口请求 - 实际开发时删除这段，替换为真实接口请求
    await new Promise(resolve => setTimeout(resolve, 1500))
    aiReplyContent.value = `已收到你的问题：【${question}】\n\n这是AI的回复内容，实际开发中替换为真实接口返回的结果即可。支持多行文本、代码块、markdown解析等扩展。`
    hasAiReply.value = true
  } catch (err) {
    aiReplyContent.value = '哎呀，请求失败了，请稍后重试～'
    hasAiReply.value = true
    console.error('AI请求失败：', err)
  } finally {
    isLoading.value = false
    // 清空输入框
    userInputVal.value = ''
    // 滚动到底部，显示最新回复
    nextTick(() => {
      const scrollDom = document.querySelector('.chat-content')
      scrollDom.scrollTop = scrollDom.scrollHeight
    })
  }
}

/**
 * 重置弹窗内容 - 打开/关闭时调用
 */
const resetModalContent = () => {
  userInputVal.value = ''
  aiReplyContent.value = ''
  hasAiReply.value = false
  isLoading.value = false
}

// 补充nextTick
import { nextTick } from 'vue'
</script>

<style lang="scss" scoped>
.ai-assistant-modal {
  height: 85vh;
  display: flex;
  flex-direction: column;
  padding: 16px 0;
  box-sizing: border-box;

  // 弹窗头部样式
  .modal-header {
    text-align: center;
    padding: 0 16px 16px;
    border-bottom: 1px solid #f2f3f5;
    margin-bottom: 16px;
    .title {
      font-size: 18px;
      font-weight: 600;
      color: #333;
      margin: 0 0 4px;
    }
    .subtitle {
      font-size: 12px;
      color: #969799;
      margin: 0;
    }
  }

  // 主体内容区 - 撑满剩余高度
  .modal-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 0 16px;

    // 对话内容滚动区
    .chat-content {
      flex: 1;
      height: 0; // 关键：flex:1 + height:0 实现自适应高度
      overflow-y: auto;
      padding-bottom: 16px;

      .chat-item {
        display: flex;
        margin-bottom: 12px;
        max-width: 100%;

        .avatar {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: #f2f3f5;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 12px;
          color: #666;
          flex-shrink: 0;
          margin-right: 8px;
        }

        .chat-bubble {
          background: #f7f8fa;
          border-radius: 8px;
          padding: 10px 12px;
          font-size: 14px;
          color: #333;
          line-height: 1.5;
          white-space: pre-wrap; // 保留换行符
          word-break: break-all;
        }
      }

      // 自己的消息靠右
      .user-chat {
        flex-direction: row-reverse;
        .avatar {
          margin-right: 0;
          margin-left: 8px;
          background: #1989fa;
          color: #fff;
        }
        .chat-bubble {
          background: #e8f3ff;
        }
      }

      // 空状态提示
      .empty-tip {
        text-align: center;
        font-size: 14px;
        color: #969799;
        margin-top: 40px;
      }
    }

    // 底部输入区
    .input-footer {
      padding-top: 12px;
      border-top: 1px solid #f2f3f5;

      .input-area {
        --van-field-label-width: 0;
        --van-field-border-radius: 8px;
        margin-bottom: 12px;
        background: #f7f8fa;
      }

      .send-btn {
        width: 100%;
        height: 44px;
        font-size: 16px;
      }
    }
  }
}

// 滚动条美化
::v-deep .chat-content::-webkit-scrollbar {
  width: 4px;
}
::v-deep .chat-content::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 2px;
}
</style>