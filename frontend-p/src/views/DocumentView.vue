<template>
  <Layout>
    <div class="document-container">
      <div class="document-header">
        <div class="document-info">
          <h2>{{ document.name }}</h2>
          <div class="document-meta">
            <span>{{ document.type === 'table' ? '表格文档' : '白板文档' }}</span>
            <span class="modified-time">
              最后修改: {{ formatDate(document.modified) }}
            </span>
          </div>
        </div>
        <div class="document-actions">
          <button class="action-btn" @click="saveDocument">
            <i class="fa fa-save"></i>
            保存
          </button>
          <button class="action-btn share-btn" @click="showShareModal = true">
            <i class="fa fa-share-alt"></i>
            分享
          </button>
        </div>
      </div>

      <div class="document-editor">
        <!-- 表格编辑器 -->
        <div class="table-editor" v-if="document.type === 'table' && document.content">
          <div class="table-toolbar">
            <div class="toolbar-group">
              <button class="toolbar-btn" @click="addRow">
                <i class="fa fa-plus"></i> 行
              </button>
              <button class="toolbar-btn" @click="addColumn">
                <i class="fa fa-plus"></i> 列
              </button>
              <button class="toolbar-btn" @click="removeRow" :disabled="selectedRow === null">
                <i class="fa fa-minus"></i> 行
              </button>
              <button class="toolbar-btn" @click="removeColumn" :disabled="selectedColumn === null">
                <i class="fa fa-minus"></i> 列
              </button>
            </div>
          </div>
          <div class="table-container">
            <table class="table-editor-table">
              <thead>
                <tr>
                  <th class="row-header">#</th>
                  <th v-for="(col, colIndex) in document.content.columns" :key="`col-${colIndex}`" 
                      class="column-header"
                      @click="selectColumn(colIndex)">
                    {{ col || colIndex + 1 }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, rowIndex) in document.content.rows" :key="`row-${rowIndex}`">
                  <td class="row-header" @click="selectRow(rowIndex)">
                    {{ rowIndex + 1 }}
                  </td>
                  <td v-for="(cell, colIndex) in row" :key="`cell-${rowIndex}-${colIndex}`" 
                      class="table-cell"
                      :class="{
                        'selected-row': selectedRow === rowIndex,
                        'selected-column': selectedColumn === colIndex
                      }"
                      @click="selectCell(rowIndex, colIndex)"
                      @dblclick="startEdit(rowIndex, colIndex)">
                    <div v-if="!isEditing || editRow !== rowIndex || editCol !== colIndex" 
                         class="cell-content">
                      {{ cell || '' }}
                    </div>
                    <input v-else 
                           type="text" 
                           class="cell-input" 
                           v-model="editingValue"
                           @blur="finishEdit"
                           @keyup.enter="finishEdit"
                           ref="cellInputRef">
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 白板编辑器 - 使用Excalidraw -->
        <div class="whiteboard-editor" v-else-if="document.type === 'whiteboard'">
          <div class="excalidraw-container">
            <Excalidraw
                ref="excalidrawRef"
                :width="3000"
                :height="2000"
                :on-change="onExcalidrawChange"
                :initial-data="excalidrawData"
                :theme="'light'"
                :lang="'zh-CN'"
                :auto-save="{}"
              />
          </div>
        </div>

        <!-- 加载状态 -->
        <div class="loading-editor" v-if="loading">
          <div class="loading-spinner"></div>
          <p>加载文档中...</p>
        </div>

        <!-- 空状态 -->
        <div class="empty-editor" v-if="!loading && !document.content">
          <div class="empty-icon">
            <i class="fa fa-file-text-o"></i>
          </div>
          <p>文档内容为空</p>
        </div>
      </div>

      <!-- 分享模态框 -->
      <div class="modal" v-if="showShareModal" @click="closeShareModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>分享文档</h3>
            <button class="close-btn" @click="closeShareModal">
              <i class="fa fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <div class="share-link-container">
              <input type="text" :value="shareLink" readonly ref="shareLinkRef">
              <button class="copy-btn" @click="copyShareLink">
                <i class="fa fa-copy"></i>
                复制
              </button>
            </div>
            <div class="share-info">
              <p>分享链接可以让其他人访问此文档</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Layout from '../components/Layout.vue'
import { documentAPI, shareAPI } from '../services/api'
import { Excalidraw } from '@excalidraw/excalidraw'

const route = useRoute()
const router = useRouter()

// Reactive data
const document = reactive({
  id: null,
  name: '未命名文档',
  type: 'table',
  content: null,
  modified: null
})

const loading = ref(true)
const showShareModal = ref(false)
const shareLink = ref('')

// 表格编辑器状态
const selectedRow = ref(null)
const selectedColumn = ref(null)
const isEditing = ref(false)
const editRow = ref(-1)
const editCol = ref(-1)
const editingValue = ref('')
const cellInputRef = ref(null)

// Excalidraw状态
const excalidrawRef = ref(null)
const excalidrawData = ref({
  elements: [],
  appState: {
    theme: 'light',
    language: 'zh-CN',
  }
})

const shareLinkRef = ref(null)

// Methods
const fetchDocument = async () => {
  const docId = route.params.id
  if (!docId) return
  
  loading.value = true
  try {
    // 先获取文档列表以确定文档类型
    const docsResult = await documentAPI.getDocuments()
    const docInfo = docsResult.find(doc => doc.id === docId)
    
    if (docInfo) {
      document.id = docId
      document.name = docInfo.name
      document.type = docInfo.type
      document.modified = docInfo.modified
      
      let result
      if (docInfo.type === 'table') {
        result = await documentAPI.getTable(docId)
      } else if (docInfo.type === 'whiteboard') {
        result = await documentAPI.getWhiteboard(docId)
      }
      
      if (result) {
        // 更新文档内容
        if (docInfo.type === 'table') {
          // 初始化表格内容
          document.content = {
            columns: result.columns || Array(10).fill().map((_, i) => `列${i+1}`),
            rows: result.rows || Array(10).fill().map(() => Array(10).fill('')),
            cellStyles: result.cellStyles || {}
          }
        } else if (docInfo.type === 'whiteboard') {
          // 初始化Excalidraw内容
          document.content = { 
            excalidrawData: result.excalidraw_data ? JSON.parse(result.excalidraw_data) : {
              elements: [],
              appState: { theme: 'light', language: 'zh-CN' }
            },
            roomKey: result.room_key || ''
          }
          // 同步到Excalidraw组件
          excalidrawData.value = document.content.excalidrawData
        }
      }
    } else {
      throw new Error('文档不存在')
    }
  } catch (error) {
    console.error('获取文档失败:', error)
    alert('获取文档失败，请稍后重试')
    router.push('/')
  } finally {
    loading.value = false
  }
}

// Excalidraw数据变化处理
const onExcalidrawChange = (elements, appState) => {
  if (document.type === 'whiteboard') {
    document.content = {
      ...document.content,
      excalidrawData: { elements, appState }
    }
  }
}

const saveDocument = async () => {
  if (!document.id) return
  
  try {
    let result
    
    if (document.type === 'table') {
      // 表格需要将content拆分为columns、rows和cellStyles字段
      result = await documentAPI.saveTable({
        id: document.id,
        title: document.name,
        columns: document.content?.columns || [],
        rows: document.content?.rows || [],
        cellStyles: document.content?.cellStyles || {}
      })
    } else if (document.type === 'whiteboard') {
        // 保存Excalidraw数据
        result = await documentAPI.saveWhiteboard({
          id: document.id,
          title: document.name,
          room_key: document.content?.roomKey || '',
          excalidraw_data: JSON.stringify(document.content?.excalidrawData || { elements: [], appState: {}})
        })
    }
    
    if (result && (result.status === 'success' || result.message)) {
      document.modified = new Date().toISOString()
      alert('文档已保存')
    }
  } catch (error) {
    console.error('保存文档失败:', error)
    alert('保存文档失败，请稍后重试')
  }
}

// 表格编辑器方法
const addRow = () => {
  if (!document.content) return
  const newRow = Array(document.content.columns.length).fill('')
  document.content.rows.push(newRow)
}

const addColumn = () => {
  if (!document.content) return
  document.content.columns.push(`列${document.content.columns.length + 1}`)
  document.content.rows.forEach(row => {
    row.push('')
  })
}

const removeRow = () => {
  if (!document.content || selectedRow.value === null || document.content.rows.length <= 1) return
  document.content.rows.splice(selectedRow.value, 1)
  selectedRow.value = null
}

const removeColumn = () => {
  if (!document.content || selectedColumn.value === null || document.content.columns.length <= 1) return
  document.content.columns.splice(selectedColumn.value, 1)
  document.content.rows.forEach(row => {
    row.splice(selectedColumn.value, 1)
  })
  selectedColumn.value = null
}

const selectRow = (rowIndex) => {
  selectedRow.value = rowIndex
  selectedColumn.value = null
}

const selectColumn = (colIndex) => {
  selectedColumn.value = colIndex
  selectedRow.value = null
}

const selectCell = (rowIndex, colIndex) => {
  selectedRow.value = rowIndex
  selectedColumn.value = colIndex
}

const startEdit = (rowIndex, colIndex) => {
  isEditing.value = true
  editRow.value = rowIndex
  editCol.value = colIndex
  editingValue.value = document.content.rows[rowIndex][colIndex] || ''
  
  nextTick(() => {
    if (cellInputRef.value) {
      cellInputRef.value.focus()
      cellInputRef.value.select()
    }
  })
}

const finishEdit = () => {
  if (isEditing.value && editRow.value !== -1 && editCol.value !== -1) {
    document.content.rows[editRow.value][editCol.value] = editingValue.value
    isEditing.value = false
    editRow.value = -1
    editCol.value = -1
  }
}

// 白板编辑器方法
const initCanvas = () => {
  if (!whiteboardCanvas.value) return
  
  const canvas = whiteboardCanvas.value
  ctx.value = canvas.getContext('2d')
  
  // 设置画布大小
  canvas.width = canvas.offsetWidth
  canvas.height = canvas.offsetHeight
  
  // 加载已有内容
  if (document.content && document.content.strokes) {
    drawSavedStrokes()
  }
}



// 分享功能
const generateShareLink = async () => {
  if (!document.id) return
  
  try {
    const result = await shareAPI.createShare({
      doc_id: document.id,
      doc_type: document.type
    })
    if (result.status === 'success' && result.share_id) {
      shareLink.value = `${window.location.origin}/share/${result.share_id}`
    }
  } catch (error) {
    console.error('生成分享链接失败:', error)
    alert('生成分享链接失败，请稍后重试')
  }
}

const copyShareLink = () => {
  if (shareLinkRef.value) {
    shareLinkRef.value.select()
    document.execCommand('copy')
    alert('分享链接已复制到剪贴板')
  }
}

const closeShareModal = () => {
  showShareModal.value = false
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Lifecycle hooks
onMounted(() => {
  fetchDocument()
  
  // 监听来自Layout组件的事件
  window.addEventListener('export-document', exportDocument)
  window.addEventListener('open-share-modal', () => {
    showShareModal.value = true
  })
  window.addEventListener('open-properties-modal', () => {
    // 这里可以添加文档属性模态框的显示逻辑
    alert('文档属性功能将在后续版本实现')
  })
})

// 导出文档功能
const exportDocument = () => {
  if (!document.id || !document.type) return
  
  if (document.type === 'table') {
    // 导出表格为CSV
    let csvContent = "data:text/csv;charset=utf-8,\uFEFF" // 添加UTF-8 BOM解决中文乱码
    
    if (document.content && document.content.columns && document.content.rows) {
      // 添加表头
      csvContent += document.content.columns.join(",") + "\r\n"
      
      // 添加数据行
      document.content.rows.forEach(row => {
        csvContent += row.join(",") + "\r\n"
      })
      
      const encodedUri = encodeURI(csvContent)
      const link = document.createElement("a")
      link.setAttribute("href", encodedUri)
      link.setAttribute("download", `${document.name || '表格'}.csv`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      alert('表格已导出为CSV文件')
    }
  } else if (document.type === 'whiteboard') {
    // 导出白板为图片
    if (whiteboardCanvas.value) {
      try {
        const dataUrl = whiteboardCanvas.value.toDataURL("image/png")
        const link = document.createElement("a")
        link.setAttribute("href", dataUrl)
        link.setAttribute("download", `${document.name || '白板'}.png`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        alert('白板已导出为PNG图片')
      } catch (error) {
        console.error('导出白板失败:', error)
        alert('导出白板失败，请稍后重试')
      }
    }
  }
}

watch(() => showShareModal.value, (newVal) => {
  if (newVal) {
    generateShareLink()
  }
})

</script>

<style scoped>
.document-container {
  width: 100%;
}

.document-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.document-info h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #1e293b;
}

.document-meta {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #64748b;
}

.document-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background-color: #2563eb;
  transform: translateY(-1px);
}

.share-btn {
  background-color: #10b981;
}

.share-btn:hover {
  background-color: #059669;
}

.document-editor {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* 表格编辑器 */
.table-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.table-toolbar {
  padding: 1rem;
  background-color: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.toolbar-group {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.toolbar-btn {
  padding: 0.5rem 1rem;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.toolbar-btn:hover {
  background-color: #f1f5f9;
  border-color: #cbd5e1;
}

.toolbar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.table-container {
  padding: 1rem;
  overflow: auto;
  max-height: calc(100vh - 300px);
}

.table-editor-table {
  border-collapse: collapse;
  width: 100%;
  min-width: 600px;
}

.table-editor-table th,
.table-editor-table td {
  border: 1px solid #e2e8f0;
  padding: 8px;
  min-width: 100px;
  height: 40px;
  text-align: left;
}

.table-editor-table th {
  background-color: #f8fafc;
  font-weight: 600;
  color: #475569;
}

.row-header {
  background-color: #f8fafc;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  user-select: none;
}

.column-header {
  cursor: pointer;
  user-select: none;
}

.row-header:hover,
.column-header:hover {
  background-color: #e2e8f0;
}

.table-cell {
  position: relative;
  cursor: cell;
}

.table-cell.selected-row {
  background-color: #dbeafe;
}

.table-cell.selected-column {
  background-color: #dbeafe;
}

.cell-content {
  width: 100%;
  height: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cell-input {
  width: 100%;
  height: 100%;
  border: none;
  outline: none;
  padding: 0;
  margin: 0;
  font-size: inherit;
  font-family: inherit;
  background: none;
}

/* 白板编辑器 */
.whiteboard-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.whiteboard-toolbar {
  padding: 1rem;
  background-color: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
}

.whiteboard-toolbar .toolbar-btn.active {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.toolbar-label {
  font-size: 0.875rem;
  color: #64748b;
  margin-right: 0.5rem;
}

.color-picker {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  padding: 0;
  overflow: hidden;
}

.range-input {
  width: 100px;
}

.whiteboard-container {
  padding: 1rem;
  overflow: auto;
}

.whiteboard-editor canvas {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background-color: white;
  cursor: crosshair;
}

/* 分享模态框 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
  margin: 20px;
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
  color: #1e293b;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  transition: all 0.2s;
}

.close-btn:hover {
  background-color: #f1f5f9;
  color: #1e293b;
}

.modal-body {
  padding: 2rem 1.5rem;
}

.share-link-container {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.share-link-container input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.875rem;
  background-color: #f8fafc;
}

.copy-btn {
  padding: 0.75rem 1.25rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.copy-btn:hover {
  background-color: #2563eb;
}

.share-info {
  color: #64748b;
  font-size: 0.875rem;
}

/* 加载和空状态 */
.loading-editor,
.empty-editor {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 4rem;
  text-align: center;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #10b981;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 4rem;
  color: #cbd5e1;
  margin-bottom: 1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .document-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .document-actions {
    justify-content: flex-start;
  }
  
  .whiteboard-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .toolbar-group {
    justify-content: center;
  }
}
</style>