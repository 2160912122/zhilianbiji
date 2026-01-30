<template>
  <div class="table-editor">
    <el-card>
      <template #header>
        <div class="editor-header">
          <div class="header-left">
            <el-button link @click="$router.back()">
              <el-icon><Back /></el-icon>
              返回
            </el-button>
            <el-input
              v-model="table.title"
              placeholder="请输入表格标题"
              style="width: 300px; margin-left: 20px"
              @input="handleAutoSave"
              id="table-title"
              name="table-title"
            />
          </div>
          <div class="header-right">
            <el-button @click="exportExcel">
              <el-icon><Download /></el-icon>
              导出Excel
            </el-button>
            <el-button @click="showVersions = true">
              <el-icon><Clock /></el-icon>
              版本历史
            </el-button>
            <el-button type="primary" @click="handleSave">
              <el-icon><Check /></el-icon>
              保存
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="table-content">
        <div class="formula-bar">
          <div class="cell-address">{{ selectedCellAddress }}</div>
          <input 
            type="text" 
            class="formula-input" 
            v-model="formulaInput"
            placeholder="输入公式或文本..."
            @blur="handleFormulaInput"
            id="formula-input"
            name="formula-input"
          />
        </div>
        
        <div class="table-toolbar">
          <div class="toolbar-section">
            <el-button 
              :type="selectedCellStyles.bold ? 'primary' : ''"
              size="small"
              @click="toggleStyle('bold')"
            >
              <el-icon><Edit /></el-icon>
              加粗
            </el-button>
            <el-button 
              :type="selectedCellStyles.italic ? 'primary' : ''"
              size="small"
              @click="toggleStyle('italic')"
            >
              <el-icon><Edit /></el-icon>
              斜体
            </el-button>
            <el-button 
              :type="selectedCellStyles.underline ? 'primary' : ''"
              size="small"
              @click="toggleStyle('underline')"
            >
              <el-icon><Edit /></el-icon>
              下划线
            </el-button>
          </div>
          <el-divider direction="vertical" />
          <div class="toolbar-section">
            <el-button 
              :type="selectedCellStyles.align === 'left' ? 'primary' : ''"
              size="small"
              @click="setAlignment('left')"
            >
              <el-icon><DArrowLeft /></el-icon>
              左对齐
            </el-button>
            <el-button 
              :type="selectedCellStyles.align === 'center' ? 'primary' : ''"
              size="small"
              @click="setAlignment('center')"
            >
              <el-icon><MoreFilled /></el-icon>
              居中
            </el-button>
            <el-button 
              :type="selectedCellStyles.align === 'right' ? 'primary' : ''"
              size="small"
              @click="setAlignment('right')"
            >
              <el-icon><DArrowRight /></el-icon>
              右对齐
            </el-button>
          </div>
          <el-divider direction="vertical" />
          <div class="toolbar-section">
            <el-button size="small" @click="insertRow">
              <el-icon><Plus /></el-icon>
              插入行
            </el-button>
            <el-button size="small" @click="insertColumn">
              <el-icon><Plus /></el-icon>
              插入列
            </el-button>
          </div>
        </div>
        
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th class="row-header">#</th>
                <th v-for="(col, colIndex) in table.columns" :key="colIndex" class="table-header-cell">
                  <div
                    class="cell-content"
                    :style="getCellStyle(-1, colIndex)"
                    @click="selectCell(-1, colIndex)"
                    @dblclick="startEditing(-1, colIndex)"
                    :contenteditable="editingCell.row === -1 && editingCell.col === colIndex"
                    ref="headerCellsRefs"
                    @blur="stopEditing(-1, colIndex)"
                    @input="handleCellInput(-1, colIndex, $event)"
                  >
                    {{ col || `列${colIndex + 1}` }}
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, rowIndex) in table.rows" :key="rowIndex">
                <td class="row-header">{{ rowIndex + 1 }}</td>
                <td v-for="(cell, colIndex) in row" :key="colIndex" class="table-cell">
                  <div
                    class="cell-content"
                    :style="getCellStyle(rowIndex, colIndex)"
                    @click="selectCell(rowIndex, colIndex)"
                    @dblclick="startEditing(rowIndex, colIndex)"
                    :contenteditable="editingCell.row === rowIndex && editingCell.col === colIndex"
                    ref="bodyCellsRefs"
                    @blur="stopEditing(rowIndex, colIndex)"
                    @input="handleCellInput(rowIndex, colIndex, $event)"
                  >
                    {{ cell || '' }}
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <div class="editor-footer">
        <span class="save-status">{{ saveStatus }}</span>
      </div>
    </el-card>
    
    <el-drawer v-model="showVersions" title="版本历史" size="40%" @open="loadVersions">
      <el-timeline>
        <el-timeline-item
          v-for="version in versions"
          :key="version.id"
          :timestamp="version.updated_at"
          placement="top"
        >
          <div class="version-item">
            <div class="version-content">行数: {{ version.rows?.length || 0 }}, 列数: {{ version.columns?.length || 0 }}</div>
            <div class="version-actions">
              <el-button link type="warning" @click="rollbackVersion(version)">
                回滚
              </el-button>
            </div>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import * as XLSX from 'xlsx'
import { tableAPI } from '@/api/editor'
import { ElMessage } from 'element-plus'
import { 
  Back, 
  Download, 
  Clock, 
  Check, 
  Edit, 
  DArrowLeft, 
  MoreFilled, 
  DArrowRight, 
  Plus 
} from '@element-plus/icons-vue'

const props = defineProps({
  isNew: {
    type: Boolean,
    default: false
  }
})

const route = useRoute()
const tableId = route.params.id

const table = ref({
  id: null,
  title: '',
  columns: ['列1', '列2', '列3'],
  rows: [['', '', ''], ['', '', ''], ['', '', '']],
  cellStyles: {}
})

const versions = ref([])
const showVersions = ref(false)

const saveStatus = ref('未保存')
let autoSaveTimer = null

const editingCell = reactive({ row: -1, col: -1 })
const selectedCell = reactive({ row: -1, col: -1 })
const selectedCellStyles = reactive({
  bold: false,
  italic: false,
  underline: false,
  align: 'left'
})

const formulaInput = ref('')
const headerCellsRefs = ref([])
const bodyCellsRefs = ref([])

const selectedCellAddress = computed(() => {
  if (selectedCell.row === -1) return ''
  const colLetter = String.fromCharCode(65 + selectedCell.col)
  return `${colLetter}${selectedCell.row + 1}`
})

async function loadTable() {
  if (props.isNew) return
  
  try {
    const data = await tableAPI.get(tableId)
    table.value = data.table
  } catch (error) {
    console.error('Load table error:', error)
  }
}

async function loadVersions() {
  if (!table.value.id) return
  
  try {
    const data = await tableAPI.getVersions(table.value.id)
    versions.value = data.versions
  } catch (error) {
    console.error('Load versions error:', error)
  }
}

function selectCell(rowIdx, colIdx) {
  selectedCell.row = rowIdx
  selectedCell.col = colIdx
  
  const cellKey = `${rowIdx}-${colIdx}`
  const styles = table.value.cellStyles[cellKey] || {}
  selectedCellStyles.bold = styles.bold || false
  selectedCellStyles.italic = styles.italic || false
  selectedCellStyles.underline = styles.underline || false
  selectedCellStyles.align = styles.align || 'left'
  
  const cellValue = rowIdx === -1 
    ? table.value.columns[colIdx] 
    : table.value.rows[rowIdx][colIdx]
  formulaInput.value = cellValue || ''
}

function startEditing(rowIdx, colIdx) {
  stopEditing(editingCell.row, editingCell.col)
  editingCell.row = rowIdx
  editingCell.col = colIdx
  
  setTimeout(() => {
    let targetEl = null
    if (rowIdx === -1) {
      targetEl = headerCellsRefs.value[colIdx]
    } else {
      targetEl = bodyCellsRefs.value[rowIdx * table.value.columns.length + colIdx]
    }
    if (targetEl) {
      targetEl.focus()
      
      const range = document.createRange()
      const sel = window.getSelection()
      if (targetEl && sel) {
        range.selectNodeContents(targetEl)
        sel.removeAllRanges()
        sel.addRange(range)
      }
    }
  }, 0)
}

function stopEditing(rowIdx, colIdx) {
  if (rowIdx === -1 && colIdx === -1) return
  
  let targetEl = null
  if (rowIdx === -1) {
    targetEl = headerCellsRefs.value[colIdx]
  } else {
    targetEl = bodyCellsRefs.value[rowIdx * table.value.columns.length + colIdx]
  }
  
  if (targetEl) {
    const value = targetEl.textContent || ''
    if (rowIdx === -1) {
      table.value.columns[colIdx] = value
    } else {
      table.value.rows[rowIdx][colIdx] = value
    }
    handleAutoSave()
  }
  
  editingCell.row = -1
  editingCell.col = -1
}

function handleCellInput(rowIdx, colIdx, e) {
}

function handleFormulaInput() {
  if (selectedCell.row === -1 && selectedCell.col === -1) return
  
  if (selectedCell.row === -1) {
    table.value.columns[selectedCell.col] = formulaInput.value
  } else {
    table.value.rows[selectedCell.row][selectedCell.col] = formulaInput.value
  }
  
  handleAutoSave()
}

function getCellStyle(rowIdx, colIdx) {
  const cellKey = `${rowIdx}-${colIdx}`
  const styles = table.value.cellStyles[cellKey] || {}
  
  return {
    'font-weight': styles.bold ? 'bold' : 'normal',
    'font-style': styles.italic ? 'italic' : 'normal',
    'text-decoration': styles.underline ? 'underline' : 'none',
    'text-align': styles.align || 'left'
  }
}

function toggleStyle(styleName) {
  if (selectedCell.row === -1) return
  
  const cellKey = `${selectedCell.row}-${selectedCell.col}`
  if (!table.value.cellStyles[cellKey]) {
    table.value.cellStyles[cellKey] = {}
  }
  
  table.value.cellStyles[cellKey][styleName] = !table.value.cellStyles[cellKey][styleName]
  selectedCellStyles[styleName] = table.value.cellStyles[cellKey][styleName]
  
  handleAutoSave()
}

function setAlignment(align) {
  if (selectedCell.row === -1) return
  
  const cellKey = `${selectedCell.row}-${selectedCell.col}`
  if (!table.value.cellStyles[cellKey]) {
    table.value.cellStyles[cellKey] = {}
  }
  
  table.value.cellStyles[cellKey].align = align
  selectedCellStyles.align = align
  
  handleAutoSave()
}

function handleAutoSave() {
  saveStatus.value = '正在保存...'
  
  if (autoSaveTimer) clearTimeout(autoSaveTimer)
  autoSaveTimer = setTimeout(() => {
    handleSave(true)
  }, 2000)
}

async function handleSave(silent = false) {
  if (autoSaveTimer) clearTimeout(autoSaveTimer)
  
  try {
    const data = {
      title: table.value.title || '新表格',
      columns: table.value.columns,
      rows: table.value.rows,
      cellStyles: table.value.cellStyles
    }
    
    if (table.value.id) {
      await tableAPI.update(table.value.id, data)
    } else {
      const result = await tableAPI.create(data)
      table.value.id = result.table.id
      table.value.title = result.table.title
    }
    
    saveStatus.value = '已保存'
    if (!silent) ElMessage.success('保存成功')
  } catch (error) {
    console.error('Save table error:', error)
    saveStatus.value = '保存失败'
    if (!silent) ElMessage.error('保存失败')
  }
}

async function rollbackVersion(version) {
  try {
    await tableAPI.rollbackVersion(table.value.id, version.id)
    table.value.columns = version.columns || []
    table.value.rows = version.rows || []
    table.value.cellStyles = version.cellStyles || {}
    await loadVersions()
    ElMessage.success('回滚成功')
  } catch (error) {
    console.error('Rollback version error:', error)
    ElMessage.error('回滚失败')
  }
}

function insertColumn() {
  table.value.columns.push(`列${table.value.columns.length + 1}`)
  table.value.rows.forEach(row => row.push(''))
  handleAutoSave()
}

function insertRow() {
  const newRow = new Array(table.value.columns.length).fill('')
  table.value.rows.push(newRow)
  handleAutoSave()
}

function addColumn() {
  table.value.columns.push(`列${table.value.columns.length + 1}`)
  table.value.rows.forEach(row => row.push(''))
  handleAutoSave()
}

function addRow() {
  const newRow = new Array(table.value.columns.length).fill('')
  table.value.rows.push(newRow)
  handleAutoSave()
}

function deleteColumn(colIndex) {
  if (table.value.columns.length <= 1) {
    ElMessage.warning('至少保留一列')
    return
  }
  
  table.value.columns.splice(colIndex, 1)
  table.value.rows.forEach(row => row.splice(colIndex, 1))
  handleAutoSave()
}

function deleteRow(rowIndex) {
  if (table.value.rows.length <= 1) {
    ElMessage.warning('至少保留一行')
    return
  }
  
  table.value.rows.splice(rowIndex, 1)
  handleAutoSave()
}

function exportExcel() {
  const ws = XLSX.utils.aoa_to_sheet([table.value.columns, ...table.value.rows])
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Sheet1')
  XLSX.writeFile(wb, `${table.value.title || '表格'}.xlsx`)
  ElMessage.success('导出成功')
}

onMounted(() => {
  loadTable()
})

onUnmounted(() => {
  if (autoSaveTimer) clearTimeout(autoSaveTimer)
})
</script>

<style scoped>
.table-editor {
  padding: 20px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.table-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.formula-bar {
  height: 40px;
  background-color: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  padding: 0 16px;
}

.cell-address {
  width: 70px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border-right: 1px solid #e2e8f0;
  font-size: 13px;
  background-color: #f1f5f9;
  font-weight: 500;
  color: #64748b;
}

.formula-input {
  flex: 1;
  height: 100%;
  border: none;
  padding: 0 16px;
  font-size: 14px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.formula-input:focus {
  outline: none;
}

.table-toolbar {
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: white;
  flex-wrap: wrap;
}

.toolbar-section {
  display: flex;
  align-items: center;
  gap: 8px;
}

.table-container {
  flex: 1;
  overflow: auto;
  padding: 20px;
  background-color: #f8fafc;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  border-radius: 6px;
  overflow: hidden;
  background-color: white;
}

.data-table th,
.data-table td {
  border: 1px solid #e2e8f0;
  padding: 12px 16px;
  text-align: left;
  min-width: 120px;
}

.data-table th {
  background-color: #f1f5f9;
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 10;
  color: #334155;
}

.data-table td {
  position: relative;
  transition: background-color 0.2s;
}

.data-table td:hover {
  background-color: #f1f5f9;
}

.data-table td.selected {
  background-color: #d1fae5;
  box-shadow: inset 0 0 0 1px #10b981;
}

.table-header-cell {
  position: relative;
  padding: 0;
}

.table-header-cell .cell-content {
  padding: 12px 16px;
  min-width: 100px;
}

.table-cell {
  padding: 0;
}

.table-cell .cell-content {
  padding: 12px 16px;
  min-width: 120px;
}

.cell-content {
  cursor: text;
  padding: 5px;
  border-radius: 3px;
  transition: background-color 0.2s;
  min-height: 20px;
}

.cell-content:focus {
  background-color: #e6f7ff;
  outline: 2px solid #1890ff;
}

.cell-content[contenteditable="true"] {
  background-color: #e6f7ff;
  outline: 2px solid #1890ff;
}

.row-header {
  background-color: #f1f5f9;
  width: 50px;
  font-weight: bold;
  text-align: center;
}

.editor-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #e6e6e6;
}

.save-status {
  font-size: 12px;
  color: #999;
}
</style>