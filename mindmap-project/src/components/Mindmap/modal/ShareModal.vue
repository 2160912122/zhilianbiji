<template>
  <!-- 7-3 分享脑图弹窗 完整版 -->
  <van-popup
    v-model:show="isShowModal"
    position="center"
    round
    closeable
    close-icon-position="top-right"
    overlay-closeable
    class="share-modal"
    @close="handleModalClose"
  >
    <!-- 弹窗头部 -->
    <div class="modal-header">
      <h3 class="modal-title">分享脑图</h3>
      <p class="modal-desc">将当前脑图分享给更多人查看吧</p>
    </div>

    <!-- 分享设置区 -->
    <div class="share-settings">
      <!-- 权限设置 -->
      <div class="setting-item">
        <span class="setting-label">分享权限</span>
        <div class="setting-select">
          <van-dropdown-menu>
            <van-dropdown-item v-model="sharePermission" :options="permissionOptions" />
          </van-dropdown-menu>
        </div>
      </div>

      <!-- 时间限制 -->
      <div class="setting-item">
        <span class="setting-label">有效期</span>
        <div class="setting-select">
          <van-dropdown-menu>
            <van-dropdown-item v-model="shareExpiry" :options="expiryOptions" />
          </van-dropdown-menu>
        </div>
      </div>

      <!-- 提示信息 -->
      <div class="setting-tip">
        <van-icon name="info-o" size="14" />
        <span>设置分享权限和有效期后生成链接</span>
      </div>
    </div>

    <!-- 分享链接区 -->
    <div class="share-links">
      <!-- 只读链接 -->
      <div class="link-section">
        <div class="link-title">只读链接：</div>
        <div class="link-content">{{ generateShareLink('readonly') }}</div>
        <van-button type="default" size="small" @click="handleCopyLink('readonly')" class="copy-btn">
          <van-icon name="copy-o" /> 复制只读链接
        </van-button>
      </div>

      <!-- 可编辑链接 -->
      <div class="link-section">
        <div class="link-title">可编辑链接：</div>
        <div class="link-content">{{ generateShareLink('editable') }}</div>
        <van-button type="default" size="small" @click="handleCopyLink('editable')" class="copy-btn">
          <van-icon name="copy-o" /> 复制可编辑链接
        </van-button>
      </div>
    </div>

    <!-- 注意事项 -->
    <div class="warning-section">
      <van-icon name="warning-o" size="16" color="#ff6b6b" />
      <div class="warning-text">
        <strong>注意：</strong>可编辑链接允许他人修改您的脑图内容，请谨慎分享！分享链接将在到期后自动失效。
      </div>
    </div>

    <!-- 底部按钮 -->
    <div class="modal-footer">
      <van-button
        type="default"
        round
        block
        class="cancel-btn"
        @click="handleModalClose"
      >
        关闭
      </van-button>
    </div>
  </van-popup>
</template>

<script setup name="ShareModal">
import { ref, defineProps, defineEmits, watch } from 'vue'
import { showToast } from 'vant'
import { updateShare } from '@/api/mindmapApi'

// 1. 父组件传参 - 双向绑定+脑图业务参数 【核心】
const props = defineProps({
  // 弹窗显隐 双向绑定 必传
  show: {
    type: Boolean,
    default: false
  },
  // 脑图标题 - 父组件传入，分享时回显，可选
  mindMapTitle: {
    type: String,
    default: ''
  },
  // 脑图分享链接 - 父组件传入，复制链接用的核心地址，可选
  mindMapLink: {
    type: String,
    default: ''
  },
  // 脑图ID - 父组件传入，用于生成分享链接，必传
  mindMapId: {
    type: String,
    default: ''
  }
})

// 2. 向外暴露事件 - 父子组件解耦合，和其他弹窗规范一致
const emit = defineEmits(['update:show', 'close', 'share', 'copy-link'])

// ===== 响应式核心数据 =====
const isCopying = ref(false) // 复制链接加载状态
const sharePermission = ref('readonly') // 分享权限：readonly/editable
const shareExpiry = ref('never') // 有效期：never/1day/7days/30days

// 弹窗显隐控制
const isShowModal = ref(props.show)

// 监听props.show变化，确保弹窗能正确显示
watch(
  () => props.show,
  (newVal) => {
    isShowModal.value = newVal
  },
  { immediate: true }
)

// 下拉选择框选项数据
const permissionOptions = ref([
  { text: '只读', value: 'readonly' },
  { text: '可编辑', value: 'editable' }
])

const expiryOptions = ref([
  { text: '永久有效', value: 'never' },
  { text: '1天', value: '1day' },
  { text: '7天', value: '7days' },
  { text: '30天', value: '30days' }
])

// ===== 监听弹窗显隐 核心逻辑 =====
watch(
  () => props.show,
  (newVal) => {
    // 弹窗打开时重置状态
    if (newVal) {
      isCopying.value = false
      sharePermission.value = 'readonly'
      shareExpiry.value = 'never'
    }
  },
  { immediate: true }
)

// ===== 所有核心业务方法 完整实现 无残缺 =====
/**
 * 弹窗关闭公共方法 - 点击叉号/遮罩/取消按钮 统一调用
 */
const handleModalClose = () => {
  isCopying.value = false
  emit('update:show', false)
  emit('close')
}

/**
 * 生成完整的分享链接，与后端API路由匹配
 * @param {String} permission - 分享权限：readonly/editable，默认使用当前选择的权限
 */
const generateShareLink = (permission = sharePermission.value) => {
    // 如果没有提供脑图id，则返回空字符串
    if (!props.mindMapId) {
      return ''
    }
    
    // 生成与路由配置一致的hash模式分享链接：/#/share/<share_type>/<mid>
    const link = `${window.location.origin}/#/share/${permission}/${props.mindMapId}`
    
    return link
  }



/**
 * 调用后端API更新分享权限
 */
const updateSharePermission = async () => {
  try {
    // 根据有效期计算expires_in（小时）
    let expires_in = null
    if (shareExpiry.value !== 'never') {
      if (shareExpiry.value === '1day') {
        expires_in = 24
      } else if (shareExpiry.value === '7days') {
        expires_in = 168
      } else if (shareExpiry.value === '30days') {
        expires_in = 720
      }
    }
    
    // 使用项目中已有的updateShare API函数
    const result = await updateShare(props.mindMapId, {
      permission: sharePermission.value,
      expires_in: expires_in
    })
    
    return result
  } catch (error) {
    console.error('更新分享权限失败：', error)
    showToast(error.message || '更新分享权限失败')
    return null
  }
}

/**
 * 复制脑图链接 核心方法 - 带加载+成功/失败提示+异常兜底
 * @param {String} permission - 分享权限：readonly/editable，默认使用当前选择的权限
 */
const handleCopyLink = async (permission = sharePermission.value) => {
  if (isCopying.value) return // 防重复点击
  
  // 先更新分享权限
  const updateResult = await updateSharePermission()
  if (!updateResult) {
    return
  }
  
  const link = generateShareLink(permission)
  if (!link) {
    showToast('脑图分享链接为空，复制失败')
    return
  }

  isCopying.value = true
  try {
    // 原生复制剪切板API
    await navigator.clipboard.writeText(link)
    showToast('链接复制成功 ✅')
    // 派发复制成功事件给父组件
    emit('copy-link', link)
    emit('close')
  } catch (err) {
    // 复制失败兜底提示（兼容浏览器权限/无https环境）
    showToast('复制失败，请手动复制链接')
    console.error('脑图链接复制失败：', err)
  } finally {
    // 无论成功失败都关闭加载状态
    setTimeout(() => {
      isCopying.value = false
    }, 800)
  }
}
</script>

<style lang="scss" scoped>
// 弹窗整体样式 - 和其他弹窗统一规范
.share-modal {
  width: 90%;
  max-width: 420px;
  padding: 20px 16px;
  box-sizing: border-box;
  border-radius: 16px;
  background: #ffffff;
}

// 弹窗头部样式
.modal-header {
  text-align: center;
  margin-bottom: 24px;
  .modal-title {
    font-size: 18px;
    font-weight: 600;
    color: #333;
    margin: 0 0 4px;
  }
  .modal-desc {
    font-size: 12px;
    color: #969799;
    margin: 0;
  }
}

// 分享设置区
.share-settings {
  margin-bottom: 24px;
  
  .setting-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    
    .setting-label {
      font-size: 14px;
      color: #666;
    }
    
    .setting-select {
      width: 160px;
    }
  }
  
  .setting-tip {
    display: flex;
    align-items: center;
    padding: 10px;
    margin-top: 8px;
    background: #f7f8fa;
    border-radius: 6px;
    font-size: 12px;
    color: #969799;
    
    span {
      margin-left: 6px;
    }
  }
}

// 分享链接区
.share-links {
  margin-bottom: 20px;
  
  .link-section {
    margin-bottom: 16px;
    
    .link-title {
      font-size: 14px;
      color: #666;
      margin-bottom: 8px;
    }
    
    .link-content {
      padding: 10px;
      margin-bottom: 8px;
      background: #f7f8fa;
      border-radius: 6px;
      font-size: 13px;
      color: #333;
      word-break: break-all;
    }
    
    .copy-btn {
      width: 100%;
      height: 34px;
      font-size: 13px;
    }
  }
}

// 警告区域
.warning-section {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  margin-bottom: 20px;
  background: #fff5f5;
  border-radius: 6px;
  border-left: 4px solid #ff6b6b;
  
  .warning-text {
    margin-left: 8px;
    font-size: 12px;
    color: #666;
    line-height: 1.4;
  }
}

// 底部按钮区
.modal-footer {
  .cancel-btn {
    height: 44px;
    font-size: 16px;
    background: #f7f8fa;
    color: #666;
    &:active {
      background: #e5e6eb;
    }
  }
}
</style>