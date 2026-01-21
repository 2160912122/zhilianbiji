<template>
  <div class="table-create-container">
    <!-- 新建表格按钮 -->
    <el-button type="primary" @click="handleCreateTable">新建表格</el-button>
    <!-- 表格容器 -->
    <el-table
      v-if="tableData.length"
      :data="tableData"
      border
      style="width: 100%; margin-top: 20px"
    >
      <el-table-column
        v-for="(col, idx) in tableColumns"
        :key="idx"
        :prop="col.prop"
        :label="col.label"
      />
    </el-table>
    <!-- 空状态 -->
    <div v-else class="empty-tip">暂无表格数据，点击新建表格生成</div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// 表格列配置
const tableColumns = ref([
  { label: '序号', prop: 'id' },
  { label: '名称', prop: 'name' },
  { label: '内容', prop: 'content' },
]);

// 表格数据
const tableData = ref([]);

// 新建表格逻辑
const handleCreateTable = () => {
  // 生成初始空表格（可根据需求自定义初始行数/列数）
  const initData = [
    { id: 1, name: '', content: '' },
    { id: 2, name: '', content: '' },
    { id: 3, name: '', content: '' },
  ];
  tableData.value = initData;
  // 若需动态新增列，可在此扩展 tableColumns
  // 例如：tableColumns.value.push({ label: '新列', prop: 'newCol' });
};
</script>

<style scoped>
.table-create-container {
  padding: 20px;
}
.empty-tip {
  margin-top: 20px;
  color: #999;
  text-align: center;
}
</style>