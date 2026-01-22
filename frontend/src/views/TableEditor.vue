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
            />
          </div>
          <div class="header-right">
            <el-button @click="addColumn">
              <el-icon><Plus /></el-icon>
              添加列
            </el-button>
            <el-button @click="addRow">
              <el-icon><Plus /></el-icon>
              添加行
            </el-button>
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
      
      <div class="table-container">
        <table class="editable-table">
          <thead>
            <tr>
              <th class="row-header">#</th>
              <th v-for="(col, colIndex) in table.columns" :key="colIndex">
                <el-input
                  v-model="table.columns[colIndex]"
                  size="small"
                  @input="handleAutoSave"
                />
                <el-button
                  link
                  type="danger"
                  size="small"
                  @click="deleteColumn(colIndex)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, rowIndex) in table.rows" :key="rowIndex">
              <td class="row-header">{{ rowIndex + 1 }}</td>
              <td v-for="(cell, colIndex) in row" :key="colIndex">
                <el-input
                  v-model="table.rows[rowIndex][colIndex]"
                  size="small"
                  @input="handleAutoSave"
                />
              </td>
              <td class="action-cell">
                <el-button
                  link
                  type="danger"
                  size="small"
                  @click="deleteRow(rowIndex)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="editor-footer">
        <span class="save-status">{{ saveStatus }}</span>
      </div>
    </el-card>
    
    <el-drawer v-model="showVersions" title="版本历史" size="40%">
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
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import * as XLSX from 'xlsx'
import { tableAPI } from '@/api/editor'
import { ElMessage } from 'element-plus'

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

async function loadTable() {
  if (props.isNew) return
  
  try {
    const data = await tableAPI.get(tableId)
    table.value = data.table
    await loadVersions()
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
    
    await loadVersions()
    
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

.table-container {
  overflow-x: auto;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
}

.editable-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
}

.editable-table th,
.editable-table td {
  border: 1px solid #e6e6e6;
  padding: 8px;
  text-align: center;
}

.editable-table th {
  background: #f5f5f5;
  position: relative;
  min-width: 120px;
}

.editable-table th .el-input {
  width: calc(100% - 40px);
}

.editable-table th .el-button {
  position: absolute;
  right: 5px;
  top: 50%;
  transform: translateY(-50%);
}

.editable-table .row-header {
  background: #f5f5f5;
  width: 50px;
  font-weight: bold;
}

.editable-table .action-cell {
  width: 50px;
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
