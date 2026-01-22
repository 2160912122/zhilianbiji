<template>
  <aside>
    <h3>我的脑图</h3>
    <div class="file-actions">
      <button class="btn primary" @click="emit('newMap')">新建脑图</button>
      <div style="margin-bottom:12px;">
        <label style="font-size:12px;">分类</label>
        <select id="categoryFilter" @change="(e) => emit('filterByCategory', e.target.value)" style="width:100%;padding:6px;border:1px solid #dcdfe6;border-radius:4px;">
              <option value="all">全部分类</option>
              <option value="recent">最近使用</option>
              <option value="favorite">收藏</option>
              <option value="work">工作</option>
              <option value="study">学习</option>
              <option value="personal">个人</option>
            </select>
      </div>
      <div style="margin-bottom:12px;">
        <label style="font-size:12px;">标签</label>
        <select id="tagFilter" @change="emit('filterByTag')" style="width:100%;padding:6px;border:1px solid #dcdfe6;border-radius:4px;">
          <option value="all">全部</option>
          <option v-for="tag in allTags" :key="tag.id" :value="tag.id">{{ tag.name }}</option>
        </select>
      </div>
      <div style="margin-bottom:12px;">
        <label style="font-size:12px;">搜索类型</label>
        <select v-model="searchType" style="width:100%;padding:6px;border:1px solid #dcdfe6;border-radius:4px;">
          <option value="all">全部</option>
          <option value="name">文件名</option>
          <option value="tag">标签</option>
          <option value="category">分类</option>
        </select>
      </div>
      <input type="text" v-model="localSearchKw" placeholder="搜索脑图..." style="width:100%;padding:6px;border:1px solid #dcdfe6;border-radius:4px;margin-top:8px">
    </div>
    <ul id="fileList">
      <li v-if="!filterMapList.length" style="padding:16px;color:#999">暂无脑图</li>
      <li v-for="m in filterMapList" :key="m.id" :class="{active: m.id === currentId}" @click="emit('openMap', m.id)">
        <div style="flex:1;">
          <div style="font-weight:500;margin-bottom:4px;">{{ m.title || m.name }}</div>
          <div style="font-size:12px;color:#909399;margin-bottom:4px;">{{ formatTime(m.createTime || m.created_at) }}</div>
          <div style="display:flex;flex-wrap:wrap;gap:2px;">
            <template v-if="m.tags && m.tags.length">
              <span v-for="(tag, ti) in m.tags" :key="ti" class="tag-badge" :style="{background: (tag.color || '#1989fa')}">{{ typeof tag === 'string' ? tag : (tag.name || tag) }}</span>
            </template>
            <!-- 分类标签 -->
            <span class="tag-badge" style="background: #4cd964;">{{ getCategoryName(m.category) }}</span>
          </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:4px;">
          <button @click.stop="emit('manageTags', m.id)" style="border:none;background:none;color:#409eff;"><i class="fas fa-tags"></i></button>
          <button @click.stop="emit('delMap', m.id)" style="border:none;background:none;color:#f56c6c;"><i class="fas fa-trash"></i></button>
        </div>
      </li>
    </ul>
  </aside>
</template>

<script setup>
import { defineProps, defineEmits, ref, watch } from 'vue';

// 定义props
const props = defineProps({
  mapList: { type: Array, default: () => [] },
  filterMapList: { type: Array, default: () => [] },
  allTags: { type: Array, default: () => [] },
  searchKw: { type: String, default: '' },
  searchType: { type: String, default: 'all' },
  currentId: { type: [String, Number], default: null },
  formatTime: { type: Function, required: true }
});

// 定义事件
const emit = defineEmits(['newMap', 'filterByCategory', 'filterByTag', 'openMap', 'manageTags', 'delMap', 'update:searchKw', 'update:searchType']);

// 分类映射
const categoryMap = {
  'work': '工作',
  'study': '学习',
  'personal': '个人',
  '': '其他'
};

// 获取分类名称
const getCategoryName = (category) => {
  return categoryMap[category] || '其他';
};

// 创建本地响应式变量
const localSearchKw = ref(props.searchKw);
const searchType = ref(props.searchType);

// 监听本地变量变化，发送事件给父组件
watch(localSearchKw, (newValue) => {
  emit('update:searchKw', newValue);
});

watch(searchType, (newValue) => {
  emit('update:searchType', newValue);
});

// 监听props变化，更新本地变量
watch(() => props.searchKw, (newValue) => {
  localSearchKw.value = newValue;
});

watch(() => props.searchType, (newValue) => {
  searchType.value = newValue;
});
</script>

<style scoped>
aside{
  width:260px;
  background:#fff;
  border-right:1px solid #e4e7ed;
  display:flex;
  flex-direction:column;
  flex-shrink: 0;
  height: 100%;
  max-height: 100%;
}
aside h3{
  padding: 10px 16px;
  font-weight:500;
  border-bottom:1px solid #e4e7ed;
  flex-shrink: 0;
}
#fileList{
  flex:1;
  overflow-y:auto;
  padding:8px;
  list-style:none;
  max-height: 100%;
}
#fileList li {
  padding: 12px;
  margin-bottom: 6px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
	border: 1px solid #f0f0f0;
	transition: all 0.2s;
}
#fileList li:hover { background: #f0f9ff; border-color: #c6e2ff; }
#fileList li.active { background: #e6f7ff; color: #409eff; border-color: #91d5ff; }
.file-actions { padding: 8px 16px; border-bottom: 1px solid #e4e7ed; }
.file-actions .btn { width: 100%; margin-bottom: 8px; }
.btn.primary {
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(64, 158, 255, 0.2);
  flex-shrink: 0;
}
.btn.primary:hover { background: #66b1ff; transform: translateY(-1px); box-shadow: 0 4px 8px rgba(64, 158, 255, 0.3); }
.btn.primary:active { transform: translateY(0); box-shadow: 0 1px 2px rgba(64, 158, 255, 0.2); }
.tag-badge {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
  margin-right: 4px;
  color: white;
  font-weight: 500;
}
</style>