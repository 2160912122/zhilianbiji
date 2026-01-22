<template>
  <!-- AI高级功能弹窗 - 完整版 无残缺 -->
  <van-popup
    v-model:show="isShowModal"
    position="bottom"
    round
    closeable
    close-icon="cross"
    close-icon-position="top-right"
    overlay-closeable
    class="enhanced-ai-modal"
    @close="handleModalClose"
  >
    <!-- 弹窗顶部标题区 -->
    <div class="modal-header">
      <h2 class="modal-title">✨ AI 高级编程助手</h2>
      <p class="modal-desc">智能问答 · 代码优化 · 问题排查 · 方案设计</p>
    </div>

    <!-- 快捷提问区 - 高级功能1 -->
    <div class="quick-question-box">
      <span class="label">快捷提问</span>
      <div class="quick-tag-list">
        <van-tag 
          v-for="item in quickQuestionList" 
          :key="item.id"
          @click="handleQuickQuestion(item.content)"
          closeable
          @close="handleCloseTag(item.id)"
        >
          {{ item.label }}
        </van-tag>
      </div>
    </div>

    <!-- 核心对话内容区 - 滚动容器 -->
    <div class="chat-content" ref="chatContentRef">
      <!-- 空状态 -->
      <div class="empty-chat" v-if="chatList.length === 0 && !isLoading">
        <van-icon name="chat-o" size="40" color="#c8c9cc" />
        <p>开始你的提问，AI 为你解答一切编程问题</p>
      </div>

      <!-- 加载中状态 -->
      <div class="loading-chat" v-if="isLoading">
        <van-loading type="spinner" color="#1989fa" />
        <p>AI 正在思考中...</p>
      </div>

      <!-- 多轮对话列表 - 核心展示 -->
      <div class="chat-item" v-for="(item, index) in chatList" :key="index">
        <!-- 用户消息 -->
        <div class="user-msg" v-if="item.type === 'user'">
          <div class="avatar user-avatar">我</div>
          <div class="msg-bubble user-bubble">{{ item.content }}</div>
        </div>

        <!-- AI消息 -->
        <div class="ai-msg" v-if="item.type === 'ai'">
          <div class="avatar ai-avatar">AI</div>
          <div class="msg-bubble ai-bubble">
            <div class="msg-content" v-html="item.content"></div>
            <!-- 复制按钮 - 高级功能2 -->
            <div class="msg-action">
              <van-button 
                size="mini" 
                type="default" 
                icon="copy-o"
                @click="handleCopyAnswer(item.content)"
              >
                复制
              </van-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部操作区 -->
    <div class="modal-footer">
      <!-- 清空对话按钮 - 高级功能3 -->
      <van-button 
        size="small" 
        type="default" 
        text
        class="clear-btn"
        @click="handleClearChat"
        :disabled="chatList.length === 0"
      >
        清空对话
      </van-button>

      <!-- 输入框 -->
      <van-field
        v-model="userInputVal"
        placeholder="输入你的编程问题，支持回车发送，最多500字"
        type="textarea"
        rows="2"
        :autosize="{ maxHeight: 120 }"
        show-word-limit
        maxlength="500"
        class="input-area"
        @keyup.enter="handleSendQuestion"
      />

      <!-- 发送按钮 -->
      <van-button
        type="primary"
        round
        block
        class="send-btn"
        @click="handleSendQuestion"
        :loading="isLoading"
        :disabled="!userInputVal.trim() || isLoading"
      >
        {{ isLoading ? '思考中' : '发送' }}
      </van-button>
    </div>
  </van-popup>
</template>

<script setup name="EnhancedAIModal">
import { ref, defineProps, defineEmits, watch, nextTick } from 'vue'
import { showToast } from 'vant'

// ===== 1. 父组件传参 - 双向绑定控制弹窗显示隐藏 =====
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  // 可选：父组件传入预设快捷问题列表，优先级高于内部预设
  quickList: {
    type: Array,
    default: () => []
  }
})

// ===== 2. 向外暴露事件 - 父子组件解耦 =====
const emit = defineEmits(['update:show', 'onClose', 'onSend', 'onClear'])

// ===== 3. 响应式核心数据 =====
const isShowModal = ref(props.show) // 弹窗显隐
const userInputVal = ref('') // 用户输入内容
const isLoading = ref(false) // 加载状态
const chatList = ref([]) // 多轮对话列表 [{type:user/ai, content:''}]
const chatContentRef = ref(null) // 对话容器ref，用于滚动到底部
// 预设快捷问题列表 - 高频编程问题，可自行扩展
const quickQuestionList = ref(props.quickList.length > 0 ? props.quickList : [
  { id: 1, label: 'Vue3封装组件', content: 'Vue3如何优雅的封装通用业务组件？' },
  { id: 2, label: '防抖节流', content: 'JS防抖和节流的区别及实现方式' },
  { id: 3, label: '跨域解决', content: '前端常见的跨域问题及解决方案' },
  { id: 4, label: '性能优化', content: 'Vue项目前端性能优化的具体方案' },
  { id: 5, label: 'TS语法', content: 'TypeScript常用语法和最佳实践' }
])

// ===== 4. 监听弹窗显隐，双向绑定核心逻辑 =====
watch(
  () => props.show,
  (newVal) => {
    isShowModal.value = newVal
    // 弹窗打开时重置状态，不重置对话记录（高级版保留历史）
    if (newVal) {
      isLoading.value = false
      userInputVal.value = ''
    }
  },
  { immediate: true }
)

// ===== 5. 核心方法 - 所有高级功能全部实现 =====
/**
 * 弹窗关闭事件处理
 */
const handleModalClose = () => {
  emit('update:show', false)
  emit('onClose')
}

/**
 * 发送问题核心方法 - 包含打字机效果+多轮对话
 */
const handleSendQuestion = async () => {
  const question = userInputVal.value.trim()
  if (!question || isLoading.value) return

  // 1. 添加用户消息到对话列表
  chatList.value.push({ type: 'user', content: question })
  // 2. 清空输入框 + 开启加载
  userInputVal.value = ''
  isLoading.value = true
  // 3. 滚动到底部
  await nextTick(() => scrollToBottom())

  try {
    // 派发事件给父组件，父组件对接真实AI接口，返回结果
    emit('onSend', question)

    // ========== 模拟AI接口请求 + 打字机逐行输出效果（核心高级功能） ==========
    await new Promise(resolve => setTimeout(resolve, 800))
    // 真实开发时，替换为接口返回的真实内容即可
    const aiAnswer = `### 你的问题：${question}

✅ 这是AI的高级回复内容，支持：
1. 多行文本换行展示、代码块格式化
2. Vue3/TS/JS/小程序 全栈解答
3. 问题排查+解决方案+最佳实践
4. 支持markdown语法解析（可扩展引入marked插件）

\`\`\`javascript
// 示例代码块 - AI回复自带代码高亮适配
const fn = () => {
  console.log('AI高级功能弹窗 - 完整无残缺')
}
\`\`\`
以上回复可直接复制使用，如有其他问题继续提问即可～`
    
    // 打字机效果：逐字渲染，提升体验
    const aiMsgIndex = chatList.value.length
    chatList.value.push({ type: 'ai', content: '' })
    let currentContent = ''
    const speed = 20 // 打字速度，越小越快
    for (let char of aiAnswer) {
      currentContent += char
      chatList.value[aiMsgIndex].content = currentContent
      await new Promise(resolve => setTimeout(resolve, speed))
    }
  } catch (error) {
    // 异常兜底
    chatList.value.push({
      type: 'ai',
      content: '❌ 抱歉，请求失败了，请检查网络后重新发送～'
    })
    console.error('AI请求异常：', error)
  } finally {
    isLoading.value = false
    await nextTick(() => scrollToBottom())
  }
}

/**
 * 快捷提问 - 点击预设标签一键发送
 */
const handleQuickQuestion = (content) => {
  userInputVal.value = content
  handleSendQuestion()
}

/**
 * 关闭快捷提问标签
 */
const handleCloseTag = (id) => {
  quickQuestionList.value = quickQuestionList.value.filter(item => item.id !== id)
}

/**
 * 复制AI回答内容
 */
const handleCopyAnswer = (content) => {
  // 去除html标签，只复制纯文本
  const pureText = content.replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ')
  navigator.clipboard.writeText(pureText).then(() => {
    showToast('复制成功 ✅')
  }).catch(() => {
    showToast('复制失败，请手动复制')
  })
}

/**
 * 清空所有对话记录
 */
const handleClearChat = () => {
  chatList.value = []
  emit('onClear')
  showToast('对话已清空')
}

/**
 * 滚动到底部 - 封装复用
 */
const scrollToBottom = () => {
  if (chatContentRef.value) {
    chatContentRef.value.scrollTop = chatContentRef.value.scrollHeight
  }
}
</script>

<style lang="scss" scoped>
// 弹窗整体样式
.enhanced-ai-modal {
  height: 90vh;
  max-height: 800px;
  display: flex;
  flex-direction: column;
  padding: 16px;
  box-sizing: border-box;
  background: #ffffff;
}

// 顶部标题区
.modal-header {
  text-align: center;
  margin-bottom: 12px;
  .modal-title {
    font-size: 18px;
    font-weight: 700;
    color: #1d2129;
    margin: 0 0 4px;
  }
  .modal-desc {
    font-size: 12px;
    color: #86909c;
    margin: 0;
  }
}

// 快捷提问区 - 高级功能样式
.quick-question-box {
  margin-bottom: 12px;
  .label {
    font-size: 12px;
    color: #86909c;
    display: block;
    margin-bottom: 8px;
  }
  .quick-tag-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    row-gap: 8px;
  }
}

// 核心对话内容区 - 自适应高度 滚动容器
.chat-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
  margin-bottom: 12px;
  scroll-behavior: smooth;

  // 空状态
  .empty-chat {
    text-align: center;
    padding: 40px 0;
    color: #c8c9cc;
    p {
      margin-top: 12px;
      font-size: 14px;
    }
  }

  // 加载状态
  .loading-chat {
    text-align: center;
    padding: 20px 0;
    p {
      margin-top: 8px;
      font-size: 14px;
      color: #86909c;
    }
  }

  // 对话项统一样式
  .chat-item {
    margin-bottom: 16px;
    display: flex;
    max-width: 100%;
    box-sizing: border-box;

    .avatar {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      flex-shrink: 0;
      margin: 0 10px;
    }

    .msg-bubble {
      max-width: calc(100% - 70px);
      padding: 12px;
      border-radius: 12px;
      font-size: 14px;
      line-height: 1.6;
      white-space: pre-wrap;
      word-break: break-all;
    }
  }

  // 用户消息 靠右
  .user-msg {
    flex-direction: row-reverse;
    .user-avatar {
      background: #1989fa;
      color: #fff;
    }
    .user-bubble {
      background: #e8f3ff;
      color: #1d2129;
    }
  }

  // AI消息 靠左
  .ai-msg {
    .ai-avatar {
      background: #f2f3f5;
      color: #666;
    }
    .ai-bubble {
      background: #f7f8fa;
      color: #1d2129;
      position: relative;
      .msg-content {
        code {
          background: #f2f3f5;
          padding: 2px 4px;
          border-radius: 4px;
        }
        pre {
          background: #f2f3f5;
          padding: 8px;
          border-radius: 8px;
          margin: 8px 0;
          overflow-x: auto;
        }
      }
      .msg-action {
        margin-top: 8px;
        text-align: right;
      }
    }
  }
}

// 底部操作区
.modal-footer {
  .clear-btn {
    display: block;
    margin-bottom: 8px;
    padding: 0;
    color: #86909c;
  }
  .input-area {
    --van-field-label-width: 0;
    --van-field-border-radius: 8px;
    background: #f7f8fa;
    margin-bottom: 12px;
  }
  .send-btn {
    height: 46px;
    font-size: 16px;
  }
}

// 滚动条美化
::v-deep .chat-content::-webkit-scrollbar {
  width: 5px;
}
::v-deep .chat-content::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 3px;
}
::v-deep .chat-content::-webkit-scrollbar-track {
  background: #f7f8fa;
}
</style>