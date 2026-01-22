<template>
  <!-- 7-4 标签管理弹窗 完整版 -->
  <van-popup
    v-model:show="isShowModal"
    position="center"
    round
    closeable
    close-icon-position="top-right"
    overlay-closeable
    class="tags-modal"
    @close="handleModalClose"
  >
    <!-- 弹窗头部 -->
    <div class="modal-header">
      <h3 class="modal-title">标签与分类管理</h3>
      <p class="modal-desc">添加/编辑/删除标签，设置脑图分类</p>
    </div>

    <!-- 核心内容区 -->
    <div class="modal-content">
      <!-- 分类选择区 -->
      <div class="category-section">
        <div class="section-title">脑图分类</div>
        <div class="category-select">
          <van-field
            v-model="selectedCategory"
            placeholder="请选择分类"
            readonly
            clickable
            label="分类"
            @click="openCategorySelect"
          >
            <template #right>
              <van-icon name="arrow" size="16" color="#c8c9cc" />
            </template>
          </van-field>
          <!-- 分类选择弹窗 -->
          <van-popup
            v-model:show="showCategoryActionSheet"
            position="bottom"
            round
            :overlay="true"
            overlay-class="category-overlay"
          >
            <div class="category-popup">
              <div class="popup-header">
                <h3>选择脑图分类</h3>
                <van-icon name="cross" size="20" @click="showCategoryActionSheet = false" />
              </div>
              <div class="category-list">
                <div
                  v-for="(option, index) in categoryOptions"
                  :key="index"
                  class="category-item"
                  @click="handleCategorySelect(index)"
                >
                  {{ option.name }}
                </div>
              </div>
            </div>
          </van-popup>
        </div>
      </div>

      <!-- 标签输入新增区 -->
      <div class="tag-input-box">
        <van-field
          v-model="inputTagVal"
          placeholder="请输入标签（最多8个字）"
          clearable
          maxlength="8"
          show-word-limit
          class="tag-input"
          @keyup.enter="handleAddTag"
        />
        <van-button
          type="primary"
          round
          size="small"
          class="add-btn"
          @click="handleAddTag"
          :disabled="!((typeof inputTagVal === 'string' && inputTagVal.trim()) || inputTagVal)"
        >
          添加
        </van-button>
      </div>

      <!-- 标签展示列表 -->
      <div class="tag-list-box">
        <div class="list-title">已添加标签 ({{ tagList.length }}/{{ maxTagNum }})</div>
        <!-- 无标签空状态 -->
        <div class="empty-tag" v-if="tagList.length === 0">
          <van-icon name="tag-o" size="24" color="#c8c9cc" />
          <span>暂无标签，添加第一个标签吧</span>
        </div>
        <!-- 标签列表 -->
        <div class="tag-list">
          <van-tag
            v-for="(tag, index) in tagList"
            :key="index"
            color="#1989fa"
            class="tag-item"
            @click="handleEditTag(index)"
            closeable
            @close="handleDelTag(index)"
          >
            {{ typeof tag === 'string' ? tag : tag.name }}
          </van-tag>
        </div>
      </div>
    </div>

    <!-- 弹窗底部操作按钮 -->
    <div class="modal-footer">
      <van-button type="default" round class="btn cancel-btn" @click="handleCancel">取消</van-button>
      <van-button type="primary" round class="btn confirm-btn" @click="handleConfirm">确定</van-button>
    </div>
  </van-popup>
</template>

<script setup name="TagsModal">
import { ref, defineProps, defineEmits, watch, nextTick } from 'vue'
import { showToast, showConfirmDialog } from 'vant'

// 1. 父组件传参 - 核心：回显标签列表 + 双向绑定弹窗显隐
const props = defineProps({
  // 弹窗显隐 双向绑定
  show: {
    type: Boolean,
    default: false
  },
  // 父组件传入的已有标签列表 必传
  tags: {
    type: Array,
    default: () => []
  },
  // 父组件传入的已有分类
  category: {
    type: String,
    default: ''
  },
  // 最大标签数量限制 可选
  maxTagNum: {
    type: Number,
    default: 20
  }
})

// 2. 向外暴露事件 - 父子组件解耦合
const emit = defineEmits(['update:show', 'confirm', 'cancel', 'close'])

// ===== 响应式核心数据 =====
const isShowModal = ref(props.show)
const inputTagVal = ref('') // 输入框绑定值
const tagList = ref([]) // 标签列表 核心数据源
const editIndex = ref(-1) // 编辑标签的下标 -1=非编辑状态
const selectedCategory = ref('') // 选中的分类
const showCategoryActionSheet = ref(false) // 分类选择弹窗

// 分类选项
const categoryOptions = [
  { name: '工作', value: 'work' },
  { name: '学习', value: 'study' },
  { name: '个人', value: 'personal' },
  { name: '其他', value: '' }
]

// ===== 监听弹窗显隐 + 回显标签列表 核心逻辑 =====
watch(
  () => props.show,
  (newVal) => {
    isShowModal.value = newVal
    // 弹窗打开时：初始化标签列表、重置输入框、重置编辑状态
    if (newVal) {
      tagList.value = [...props.tags] // 深拷贝 防止修改父组件数据
      selectedCategory.value = props.category || ''
      inputTagVal.value = ''
      editIndex.value = -1
    }
  },
  { immediate: true }
)

// ===== 所有核心业务方法 完整实现 =====
/**
 * 添加标签 核心方法
 */
const handleAddTag = () => {
  // 统一处理字符串和对象类型的标签值
  const tagVal = typeof inputTagVal.value === 'string' ? inputTagVal.value.trim() : inputTagVal.value
  // 1. 空值校验
  if (!tagVal || (typeof tagVal === 'string' && !tagVal.trim())) {
    showToast('请输入标签内容')
    return
  }
  // 2. 重复标签校验
  const tagName = typeof tagVal === 'string' ? tagVal : tagVal.name
  const isDuplicate = tagList.value.some((tag, index) => {
    const currentTagName = typeof tag === 'string' ? tag : tag.name
    return currentTagName === tagName && index !== editIndex.value
  })
  if (isDuplicate) {
    showToast('该标签已存在，请勿重复添加')
    inputTagVal.value = ''
    return
  }
  // 3. 数量上限校验
  if (tagList.value.length >= props.maxTagNum) {
    showToast(`最多只能添加${props.maxTagNum}个标签`)
    return
  }

  // 判断：是【编辑标签】还是【新增标签】
  if (editIndex.value > -1) {
    // 编辑标签逻辑：保持原有标签类型一致性
    const originalTag = tagList.value[editIndex.value]
    if (typeof originalTag === 'string') {
      tagList.value[editIndex.value] = tagVal
    } else {
      tagList.value[editIndex.value] = { ...originalTag, name: tagVal }
    }
    showToast('标签修改成功')
    editIndex.value = -1
  } else {
    // 新增标签逻辑：统一使用字符串类型
    tagList.value.push(tagVal)
    showToast('标签添加成功')
  }
  // 清空输入框
  inputTagVal.value = ''
}

/**
 * 编辑标签 - 点击标签触发
 */
const handleEditTag = (index) => {
  editIndex.value = index
  // 获取标签名称，处理字符串和对象类型的标签
  const tag = tagList.value[index]
  inputTagVal.value = typeof tag === 'string' ? tag : tag.name || ''
  // 自动聚焦输入框
  nextTick(() => {
    const inputDom = document.querySelector('.tag-input input')
    inputDom && inputDom.focus()
  })
  showToast('可直接修改标签内容，按回车/点添加确认')
}

/**
 * 删除标签 - 点击标签关闭按钮触发 带二次确认
 */
const handleDelTag = async (index) => {
  try {
    await showConfirmDialog({
      title: '确认删除',
      message: '确定要删除该标签吗？删除后不可恢复',
      confirmButtonText: '删除',
      confirmButtonColor: '#f53f3f'
    })
    tagList.value.splice(index, 1)
    showToast('标签删除成功')
  } catch {
    // 取消删除 无操作
  }
}

/**
 * 打开分类选择弹窗
 */
const openCategorySelect = () => {
  showCategoryActionSheet.value = true
}

/**
 * 选择分类
 */
const handleCategorySelect = (index) => {
  // Vant 4 ActionSheet的select事件直接传递索引值
  const selected = categoryOptions[index]
  if (selected) {
    selectedCategory.value = selected.value
    showCategoryActionSheet.value = false
    showToast(`已选择分类：${selected.name}`)
  }
}

/**
 * 弹窗关闭 - 点击右上角叉号/遮罩层
 */
const handleModalClose = () => {
  resetModal()
  emit('update:show', false)
  emit('close')
}

/**
 * 取消按钮 - 点击取消
 */
const handleCancel = () => {
  resetModal()
  emit('update:show', false)
  emit('cancel')
}

/**
 * 确定按钮 - 核心回调 向父组件返回最新标签列表和分类
 */
const handleConfirm = () => {
  // 去重+过滤空标签 兜底处理
  // 统一处理字符串和对象类型的标签
  const finalTags = [...new Set(tagList.value)].filter(item => {
    if (typeof item === 'string') {
      return item.trim() // 字符串类型标签：去除空格后判断是否为空
    } else {
      return item && item.name && item.name.trim() // 对象类型标签：判断name属性是否存在且不为空
    }
  })
  emit('confirm', finalTags, selectedCategory.value) // 回传最终标签列表和分类给父组件
  resetModal()
  emit('update:show', false)
  showToast('标签保存成功')
}

/**
 * 重置弹窗状态 - 公共方法
 */
const resetModal = () => {
  inputTagVal.value = ''
  editIndex.value = -1
}
</script>

<style lang="scss" scoped>
// 弹窗整体样式
.tags-modal {
  width: 90%;
  max-width: 400px;
  padding: 20px 16px;
  box-sizing: border-box;
  border-radius: 16px;
}

// 头部样式
.modal-header {
  text-align: center;
  margin-bottom: 20px;
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

// 主体内容区
.modal-content {
  margin-bottom: 24px;

  // 分类选择区
  .category-section {
    margin-bottom: 24px;
    .section-title {
      font-size: 14px;
      font-weight: 500;
      color: #333;
      margin-bottom: 12px;
    }
    .category-select {
      position: relative;
    }
  }

  // 输入框+添加按钮区域
  .tag-input-box {
    display: flex;
    align-items: flex-end;
    gap: 8px;
    margin-bottom: 20px;
    .tag-input {
      flex: 1;
      --van-field-label-width: 0;
      --van-field-border-radius: 8px;
    }
    .add-btn {
      flex-shrink: 0;
      padding: 0 16px;
      height: 34px;
    }
  }

  // 标签列表区域
  .tag-list-box {
    .list-title {
      font-size: 14px;
      color: #666;
      margin-bottom: 12px;
    }
    .empty-tag {
      text-align: center;
      padding: 20px 0;
      color: #c8c9cc;
      font-size: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }
    .tag-list {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      row-gap: 10px;
      .tag-item {
        padding: 4px 10px;
        font-size: 13px;
        cursor: pointer;
        user-select: none;
        &:active {
          opacity: 0.8;
        }
      }
    }
  }
}

// 底部按钮区
.modal-footer {
  display: flex;
  gap: 10px;
  .btn {
    flex: 1;
    height: 44px;
    font-size: 16px;
  }
  .cancel-btn {
    background: #f7f8fa;
    color: #666;
  }
}

/* 分类选择弹窗 */
.category-overlay {
  background-color: rgba(0, 0, 0, 0.5);
}

.category-popup {
  background-color: #fff;
  border-radius: 12px 12px 0 0;
  padding: 20px;
  max-height: 80vh;
  overflow-y: auto;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
  h3 {
    font-size: 16px;
    font-weight: 500;
    color: #323233;
    margin: 0;
  }
}

.category-list {
  display: flex;
  flex-direction: column;
  .category-item {
    padding: 15px 0;
    border-bottom: 1px solid #f0f0f0;
    font-size: 14px;
    color: #323233;
    text-align: center;
    cursor: pointer;
    transition: background-color 0.2s;
    &:hover {
      background-color: #f5f5f5;
    }
    &:last-child {
      border-bottom: none;
    }
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .category-popup {
    padding: 16px;
  }
  .popup-header {
    margin-bottom: 16px;
    padding-bottom: 12px;
  }
  .category-item {
    padding: 12px 0;
  }
}
</style>