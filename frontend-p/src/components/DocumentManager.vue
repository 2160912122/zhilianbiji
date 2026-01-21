<template>
  <div class="doc-container">
    <!-- 操作按钮区 -->
    <div class="doc-actions">
      <el-button type="primary" @click="handleNewTable">新建表格</el-button>
      <el-button type="success" @click="handleNewWhiteboard">新建白板</el-button>
    </div>

    <!-- 表格预览区 -->
    <div v-if="currentTable" class="table-preview">
      <h3>{{ currentTable.title }}</h3>
      <el-table :data="formatTableData(currentTable)" border style="width: 100%">
        <el-table-column
          v-for="(col, idx) in currentTable.columns"
          :key="idx"
          :label="col"
          :prop="`col${idx}`"
        />
      </el-table>
    </div>

    <!-- 白板跳转区 -->
    <div v-if="currentWhiteboard" class="whiteboard-preview">
      <h3>{{ currentWhiteboard.title }}</h3>
      <el-button
        type="info"
        @click="openExcalidraw(currentWhiteboard.room_key)"
      >
        打开Excalidraw白板
      </el-button>
    </div>

    <!-- 提示信息 -->
    <el-message :show-close="true" v-model="messageShow" :type="messageType">
      {{ messageText }}
    </el-message>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { ElMessage, ElInput, ElMessageBox } from 'element-plus';

// 配置axios
axios.defaults.withCredentials = true; // 携带cookie

// 响应数据-表格
const currentTable = ref(null);
// 响应数据-白板
const currentWhiteboard = ref(null);
// 所有文档列表
const documents = ref([]);
// 消息提示
const messageShow = ref(false);
const messageType = ref('success');
const messageText = ref('');

// 获取所有文档列表
const fetchDocuments = async () => {
  try {
    const res = await axios.get('/api/documents');
    if (Array.isArray(res.data)) {
      documents.value = res.data;
    }
  } catch (error) {
    console.error('获取文档列表失败:', error);
  }
};

// 组件挂载时获取文档列表
onMounted(() => {
  fetchDocuments();
});

/**
 * 检查文档名称是否已存在
 * @param name 要检查的文档名称
 * @param type 文档类型（table或whiteboard）
 * @returns 是否存在重复名称
 */
const isNameExists = (name, type) => {
  return documents.value.some(doc => 
    doc.name === name && doc.type === type
  );
};

/**
 * 格式化表格数据（适配Element-Plus Table组件）
 * @param table 后端返回的表格数据
 */
const formatTableData = (table) => {
  return table.rows.map((row, rowIdx) => {
    const rowObj = {};
    table.columns.forEach((col, colIdx) => {
      rowObj[`col${colIdx}`] = row[colIdx] || '';
    });
    return rowObj;
  });
};

/**
 * 新建表格 - 对接后端/api/table/new
 */
const handleNewTable = async () => {
  try {
    // 提示用户输入表格名称
    const name = await ElMessageBox.prompt('请输入表格名称', '新建表格', {
      confirmButtonText: '创建',
      cancelButtonText: '取消',
      inputValidator: (value) => {
        if (!value.trim()) {
          return '表格名称不能为空';
        }
        if (isNameExists(value.trim(), 'table')) {
          return '该表格名称已存在';
        }
        return true;
      },
      inputValue: `新表格_${new Date().getTime()}` // 默认名称
    }).then(({ value }) => value.trim());

    const res = await axios.post('/api/table/new', {
      title: name
    });
    if (res.data.status === 'success') {
      // 获取新建表格的完整数据
      const tableRes = await axios.get('/api/table', {
        params: { id: res.data.id },
      });
      currentTable.value = tableRes.data;
      currentWhiteboard.value = null; // 清空白板状态
      // 更新文档列表
      await fetchDocuments();
      showMessage('success', '表格创建成功！');
    }
  } catch (err) {
    if (err === 'cancel') {
      // 用户取消操作，不显示错误信息
      return;
    }
    showMessage('error', err.response?.data?.message || '表格创建失败');
  }
};

/**
 * 新建白板 - 对接后端/api/whiteboard/new
 */
const handleNewWhiteboard = async () => {
  try {
    // 提示用户输入白板名称
    const name = await ElMessageBox.prompt('请输入白板名称', '新建白板', {
      confirmButtonText: '创建',
      cancelButtonText: '取消',
      inputValidator: (value) => {
        if (!value.trim()) {
          return '白板名称不能为空';
        }
        if (isNameExists(value.trim(), 'whiteboard')) {
          return '该白板名称已存在';
        }
        return true;
      },
      inputValue: `新白板_${new Date().getTime()}` // 默认名称
    }).then(({ value }) => value.trim());

    const res = await axios.post('/api/whiteboard/new', {
      title: name
    });
    if (res.data.status === 'success') {
      // 获取新建白板的完整数据
      const whiteboardRes = await axios.get('/api/whiteboard', {
        params: { id: res.data.id },
      });
      currentWhiteboard.value = whiteboardRes.data;
      currentTable.value = null; // 清空表格状态
      // 更新文档列表
      await fetchDocuments();
      showMessage('success', '白板创建成功！');
    }
  } catch (err) {
    if (err === 'cancel') {
      // 用户取消操作，不显示错误信息
      return;
    }
    showMessage('error', err.response?.data?.message || '白板创建失败');
  }
};

/**
 * 打开Excalidraw白板（通过room_key关联）
 * @param roomKey 后端生成的room_key
 */
const openExcalidraw = (roomKey) => {
  // Excalidraw支持通过URL参数传递roomId（自定义room_key）
  const excalidrawUrl = `https://excalidraw.com/#room=${roomKey}`;
  window.open(excalidrawUrl, '_blank'); // 新窗口打开Excalidraw
};

/**
 * 通用消息提示
 */
const showMessage = (type, text) => {
  messageType.value = type;
  messageText.value = text;
  messageShow.value = true;
  // 3秒后关闭
  setTimeout(() => {
    messageShow.value = false;
  }, 3000);
};
</script>

<style scoped>
.doc-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.doc-actions {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.table-preview,
.whiteboard-preview {
  margin-top: 20px;
  padding: 20px;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
}

.table-preview h3,
.whiteboard-preview h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #333;
}
</style>