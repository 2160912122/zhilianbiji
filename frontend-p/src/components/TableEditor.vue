<template>
  <div class="table-editor-container">
    <!-- 表格标题编辑 -->
    <div class="table-title-edit">
      <el-input
        v-model="tableTitle"
        placeholder="请输入表格标题"
        @blur="handleTitleBlur"
        style="width: 300px; margin-bottom: 20px"
      />
    </div>

    <!-- 表格操作按钮 -->
    <div class="table-actions" style="margin-bottom: 10px">
      <el-button type="primary" size="small" @click="addColumn">新增列</el-button>
      <el-button type="primary" size="small" @click="addRow">新增行</el-button>
      <el-button type="success" size="small" @click="saveTable">保存表格</el-button>
      <el-button type="danger" size="small" @click="clearTable">清空表格</el-button>
    </div>

    <!-- 表格主体（可编辑） -->
    <div class="table-wrapper" style="overflow-x: auto">
      <table class="editable-table" border="1" cellpadding="0" cellspacing="0">
        <thead>
          <tr>
            <!-- 表头列 -->
            <th v-for="(col, colIdx) in tableColumns" :key="`col-${colIdx}`" class="table-header-cell">
              <div
                class="cell-content"
                @click="startEditing(colIdx, -1)"
                :contenteditable="editingCell.col === colIdx && editingCell.row === -1"
                ref="headerCellsRefs"
                @blur="stopEditing(colIdx, -1)"
                @input="handleCellInput(colIdx, -1, $event)"
              >
                {{ col || `列${colIdx + 1}` }}
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <!-- 表格行 -->
          <tr v-for="(row, rowIdx) in tableRows" :key="`row-${rowIdx}`" class="table-row">
            <!-- 表格单元格 -->
            <td v-for="(cell, colIdx) in row" :key="`cell-${rowIdx}-${colIdx}`" class="table-cell">
              <div
                class="cell-content"
                @click="startEditing(colIdx, rowIdx)"
                :contenteditable="editingCell.col === colIdx && editingCell.row === rowIdx"
                ref="bodyCellsRefs"
                @blur="stopEditing(colIdx, rowIdx)"
                @input="handleCellInput(colIdx, rowIdx, $event)"
              >
                {{ cell || '' }}
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 保存状态提示 - 已改为使用API调用 -->
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, onUnmounted } from 'vue';
import { ElMessage } from 'element-plus';
import { documentAPI } from '../services/api';
import { getCurrentUser } from '../utils/auth';
import * as XLSX from 'xlsx';
// vue3-click-outside 可能不提供默认导出，我们暂时移除它，后续可以使用其他方式实现点击外部失焦功能

// ------------------- 基础数据定义 -------------------
// 表格ID（新建表格后从后端返回）
const tableId = ref<string>('');
// 表格标题
const tableTitle = ref<string>('新表格');
// 表格列（对应后端columns_data）
const tableColumns = ref<string[]>(['列1', '列2', '列3']);
// 表格行（对应后端rows_data）
const tableRows = ref<string[][]>([
  ['', '', ''],
  ['', '', ''],
  ['', '', '']
]);
// 单元格样式（对应后端cellStyles）
const cellStyles = ref<Record<string, any>>({});
// 编辑中单元格标识 { col: 列索引, row: 行索引（-1代表表头） }
const editingCell = reactive({ col: -1, row: -1 });
// 消息提示 - 已改为使用ElMessage API，不再需要这些变量
// const messageShow = ref(false);
// const messageType = ref<'success' | 'error'>('success');
// const messageText = ref('');

// ------------------- 引用与指令 -------------------
// 表头单元格引用
const headerCellsRefs = ref<HTMLElement[]>([]);
// 内容单元格引用
const bodyCellsRefs = ref<HTMLElement[]>([]);
// 点击外部停止编辑功能将在后续实现

// ------------------- 初始化表格 -------------------
/**
 * 初始化表格数据（新建表格后调用，传入后端返回的表格ID）
 * @param initTableId 后端返回的表格ID
 */
const initTable = async (initTableId: string) => {
  try {
    tableId.value = initTableId;
    // 调用后端接口获取表格完整数据
    const res = await documentAPI.getTable(initTableId);
    // 同步后端数据到前端
    tableTitle.value = res.title;
    tableColumns.value = res.columns;
    tableRows.value = res.rows;
    cellStyles.value = res.cellStyles || {};
    ElMessage.success('表格加载成功！');
  } catch (err: any) {
    ElMessage.error(err.response?.data?.message || '表格初始化失败');
  }
};

// ------------------- 单元格编辑逻辑 -------------------
/**
 * 开始编辑单元格
 * @param colIdx 列索引
 * @param rowIdx 行索引（-1=表头）
 */
const startEditing = (colIdx: number, rowIdx: number) => {
  // 先停止之前的编辑
  stopEditing(editingCell.col, editingCell.row);
  // 设置当前编辑单元格
  editingCell.col = colIdx;
  editingCell.row = rowIdx;
  // 聚焦到编辑单元格
  setTimeout(() => {
    let targetEl: HTMLElement | null = null;
    if (rowIdx === -1) {
      // 表头单元格
      targetEl = headerCellsRefs.value[colIdx];
    } else {
      // 内容单元格（行索引 * 列数 + 列索引）
      targetEl = bodyCellsRefs.value[rowIdx * tableColumns.value.length + colIdx];
    }
    targetEl?.focus();
    // 选中单元格内容
    const range = document.createRange();
    const sel = window.getSelection();
    if (targetEl && sel) {
      range.selectNodeContents(targetEl);
      sel.removeAllRanges();
      sel.addRange(range);
    }
  }, 0);
};

/**
 * 停止编辑单元格
 * @param colIdx 列索引
 * @param rowIdx 行索引（-1=表头）
 */
const stopEditing = (colIdx: number, rowIdx: number) => {
  if (colIdx === -1 && rowIdx === -1) return;
  editingCell.col = -1;
  editingCell.row = -1;
};

/**
 * 单元格内容输入事件
 * @param colIdx 列索引
 * @param rowIdx 行索引（-1=表头）
 * @param e 输入事件
 */
const handleCellInput = (colIdx: number, rowIdx: number, e: Event) => {
  const target = e.target as HTMLElement;
  const value = target.textContent || '';
  if (rowIdx === -1) {
    // 编辑表头
    tableColumns.value[colIdx] = value;
  } else {
    // 编辑内容单元格
    tableRows.value[rowIdx][colIdx] = value;
  }
};

/**
 * 表格标题失焦事件
 */
const handleTitleBlur = () => {
  if (!tableTitle.value.trim()) {
    tableTitle.value = '新表格';
    showMessage('warning', '表格标题不能为空，已设置为默认标题');
  }
};

// ------------------- 表格操作 -------------------
/**
 * 新增列
 */
const addColumn = () => {
  // 表头新增一列
  tableColumns.value.push(`列${tableColumns.value.length + 1}`);
  // 每一行新增一个单元格
  tableRows.value.forEach(row => {
    row.push('');
  });
};

/**
 * 新增行
 */
const addRow = () => {
  // 新增一行，单元格数量与列数相同
  const newRow: string[] = Array(tableColumns.value.length).fill('');
  tableRows.value.push(newRow);
};

/**
 * 删除选中行
 */
const deleteRow = () => {
  // 这里简单实现为删除最后一行
  if (tableRows.value.length > 0) {
    tableRows.value.pop();
  } else {
    ElMessage.warning('没有可以删除的行');
  }
};

/**
 * 保存表格
 */
const saveTable = async () => {
  if (!tableId.value) {
    showMessage('error', '表格ID不存在，无法保存');
    return;
  }

  try {
    const res = await documentAPI.saveTable({
      id: tableId.value,
      title: tableTitle.value,
      columns: tableColumns.value,
      rows: tableRows.value,
      cellStyles: cellStyles.value
    });

    if (res.status === 'success') {
      showMessage('success', '表格保存成功！');
    } else {
      showMessage('error', res.message || '表格保存失败');
    }
  } catch (err: any) {
    showMessage('error', err.response?.data?.message || '表格保存失败');
  }
};

/**
 * 清空表格
 */
const clearTable = () => {
  // 清空表头
  tableColumns.value = [];
  // 清空行
  tableRows.value = [];
  // 清空单元格样式
  cellStyles.value = {};
  ElMessage.success('表格已清空');
};

/**
 * 导出表格到Excel文件
 */
const exportTable = () => {
  try {
    // 创建工作表
    const worksheet = XLSX.utils.aoa_to_sheet([]);
    
    // 添加表头
    if (tableColumns.value.length > 0) {
      XLSX.utils.sheet_add_aoa(worksheet, [tableColumns.value], { origin: 'A1' });
    }
    
    // 添加数据行
    if (tableRows.value.length > 0) {
      XLSX.utils.sheet_add_aoa(worksheet, tableRows.value, { origin: 'A2' });
    }
    
    // 创建工作簿
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1');
    
    // 生成文件名
    const fileName = `${tableTitle.value || '未命名表格'}.xlsx`;
    
    // 导出文件
    XLSX.writeFile(workbook, fileName);
    
    ElMessage.success('表格导出成功');
  } catch (error) {
    console.error('导出表格失败:', error);
    ElMessage.error('表格导出失败');
  }
};

// ------------------- 辅助函数 -------------------
/**
 * 显示消息提示
 * @param type 消息类型
 * @param message 消息内容
 */
const showMessage = (type: 'success' | 'error' | 'warning', message: string) => {
  // 使用Element Plus的ElMessage API而不是模板组件
  ElMessage({
    type: type,
    message: message,
    showClose: true,
    duration: 3000
  });
};

// ------------------- 组件生命周期 -------------------
onMounted(() => {
  // 组件挂载时不需要重复初始化，因为数据定义中已经设置了默认值
});

// 导出组件方法
defineExpose({
  initTable,
  saveTable,
  clearTable,
  exportTable,
  addColumn,
  addRow,
  deleteRow
});
</script>

<style scoped>
.table-editor-container {
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.table-title-edit {
  margin-bottom: 20px;
}

.table-actions {
  margin-bottom: 10px;
}

.table-wrapper {
  overflow-x: auto;
  background-color: white;
  padding: 10px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.editable-table {
  width: 100%;
  border-collapse: collapse;
}

.table-header-cell {
  background-color: #f5f7fa;
  font-weight: bold;
  text-align: left;
  padding: 8px;
  border: 1px solid #e4e7ed;
}

.table-cell {
  border: 1px solid #e4e7ed;
  padding: 8px;
  min-width: 100px;
}

.cell-content {
  cursor: text;
  padding: 5px;
  border-radius: 3px;
  transition: background-color 0.2s;
}

.cell-content:focus {
  background-color: #e6f7ff;
  outline: 2px solid #1890ff;
}

/* 编辑状态高亮 */
.cell-content[contenteditable="true"] {
  background-color: #e6f7ff;
  outline: 2px solid #1890ff;
}
</style>