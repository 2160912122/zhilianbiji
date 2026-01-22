<template>
  <van-cell
    class="map-item"
    @click="handleItemClick"
  >
    <template #title>
      <div class="map-title">{{ mapItem.title }}</div>
    </template>
    <template #label>
      <div class="map-label">
        <span class="date">{{ formatTime(mapItem.createTime) }}</span>
        <van-tag v-if="mapItem.tags.length" color="#1989fa" plain size="mini">
          {{ typeof mapItem.tags[0] === 'string' ? mapItem.tags[0] : (mapItem.tags[0].name || '未知标签') }}
        </van-tag>
        <van-tag color="#4cd964" plain size="mini">
          {{ getCategoryName(mapItem.category) }}
        </van-tag>
      </div>
    </template>
    <template #right-icon>
      <van-icon name="arrow-right" size="16" color="#c8c9cc" />
    </template>
    <!-- 脑图操作菜单 -->
    <div class="map-action">
      <van-icon name="share-o" @click.stop="emit('openShare', mapItem)" />
      <van-icon name="tag-o" @click.stop="emit('openTags', mapItem)" />
      <van-icon name="delete-o" @click.stop="emit('delMindMap', mapItem.id, index)" />
    </div>
  </van-cell>
</template>

<script setup name="MindmapItem">
import { defineProps, defineEmits } from 'vue'
import { Icon as VanIcon, Tag as VanTag, Cell as VanCell } from 'vant'

// 分类映射
const categoryMap = {
  'work': '工作',
  'study': '学习',
  'personal': '个人',
  '': '其他'
}

// 获取分类名称
const getCategoryName = (category) => {
  return categoryMap[category] || '其他'
}

// 格式化时间函数
const formatTime = (time) => {
  if (!time) return ''
  try {
    const date = new Date(time)
    if (isNaN(date.getTime())) return time
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  } catch (error) {
    return time
  }
}

// 接收父组件传递的单条脑图数据和索引
const props = defineProps({
  mapItem: {
    type: Object,
    required: true,
    default: () => ({})
  },
  index: {
    type: Number,
    required: true
  }
})

// 定义所有操作事件
const emit = defineEmits(['openMindMap', 'openShare', 'openTags', 'delMindMap'])

// 点击列表项打开脑图
const handleItemClick = () => {
  emit('openMindMap', props.mapItem.id)
}
</script>

<style lang="scss" scoped>
.map-item {
  position: relative;
  background: #ffffff;
  border-radius: 12px;
  margin-bottom: 10px;
	padding: 16px;
  overflow: hidden;
  .map-title {
    font-size: 16px;
    color: #333;
    font-weight: 500;
    margin-bottom: 4px;
  }
  .map-label {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    margin-right: 80px; /* 增加右侧间距，避免被操作按钮覆盖 */
    .date {
      font-size: 12px;
      color: #969799;
      margin-right: 8px;
    }
    .van-tag {
      margin-right: 8px;
      margin-bottom: 4px;
    }
  }
  // 脑图操作按钮组
  .map-action {
    position: absolute;
    right: 16px;
    top: 50%;
    transform: translateY(-50%);
    display: flex;
    gap: 16px;
    font-size: 18px;
    color: #969799;
    > i {
      cursor: pointer;
      &:active {
        color: #1989fa;
      }
    }
  }
}
</style>