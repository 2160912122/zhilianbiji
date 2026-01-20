<template>
  <div class="flow-editor">
    <!-- 顶部工具栏 -->
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="flowTitle"
          placeholder="流程图标题"
          @input="updateTitle"
          style="width: 300px;"
          size="small"
          clearable
        />
        <el-button-group>
          <el-button @click="save" :loading="saving" size="small">
            <el-icon><Check /></el-icon>保存
          </el-button>
          <el-dropdown @command="exportFlowchart" split-button size="small">
            <el-icon><Download /></el-icon>导出
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="svg">导出为SVG</el-dropdown-item>
                <el-dropdown-item command="png">导出为PNG</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-button-group>

        <el-button-group style="margin-left: 10px;">
          <el-button @click="undo" :disabled="!canUndo" size="small" title="撤销 (Ctrl+Z)">
            <el-icon><RefreshLeft /></el-icon>
          </el-button>
          <el-button @click="redo" :disabled="!canRedo" size="small" title="重做 (Ctrl+Y)">
            <el-icon><RefreshRight /></el-icon>
          </el-button>
        </el-button-group>

        <el-button-group style="margin-left: 10px;">
          <el-button @click="zoomIn" size="small" title="放大 (Ctrl++)">
            <el-icon><ZoomIn /></el-icon>
          </el-button>
          <el-button @click="zoomOut" size="small" title="缩小 (Ctrl+-)">
            <el-icon><ZoomOut /></el-icon>
          </el-button>
          <el-button @click="zoomReset" size="small" title="重置缩放">
            <el-icon><FullScreen /></el-icon>
          </el-button>
          <el-button @click="fitView" size="small" title="适应画布">
            <el-icon><ScaleToOriginal /></el-icon>
          </el-button>
        </el-button-group>
      </div>

      <div class="toolbar-right">
        <el-button type="primary" @click="shareFlowchart" size="small">
          <el-icon><Share /></el-icon>分享
        </el-button>
      </div>
    </div>

    <!-- 编辑器主体 -->
    <div class="editor-main">
      <!-- 左侧节点库 -->
      <div class="left-sidebar">
        <NodeLibrary @node-drag-start="onNodeDragStart" />
      </div>

      <!-- 中间画布 -->
      <div class="editor-canvas">
        <LogicFlowEditor
          ref="lfEditor"
          v-model:flow-data="graphData"
          :read-only="readOnly"
          @change="handleFlowChange"
          @element-selected="handleElementSelected"
          @save="handleSave"
          class="graph-editor"
        />
      </div>

      <!-- 右侧属性面板 -->
      <div class="right-sidebar">
        <PropertyPanel
          :selected-element="selectedElement"
          @update-element="handleUpdateElement"
          @update-element-position="handleUpdateElementPosition"
          @update-node-type="handleUpdateNodeType"
          @delete-element="handleDeleteElement"
          @clear-selection="handleClearSelection"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Check, Download, Share, RefreshLeft, RefreshRight,
  ZoomIn, ZoomOut, FullScreen, ScaleToOriginal
} from '@element-plus/icons-vue'

// 组件导入
import LogicFlowEditor from '@/components/LogicFlowEditor.vue'
import NodeLibrary from '@/components/NodeLibrary.vue'
import PropertyPanel from '@/components/PropertyPanel.vue'

// 属性
const props = defineProps({
  flowTitle: {
    type: String,
    default: '未命名流程图'
  },
  initialData: {
    type: Object,
    default: () => ({ nodes: {}, edges: {} })
  },
  flowchartId: {
    type: [String, Number],
    default: null
  }
})

// 事件
const emit = defineEmits([
  'title-change',
  'save',
  'share',
  'export'
])

// 状态管理
const flowTitle = ref(props.flowTitle)
const graphData = ref({ ...props.initialData })
const selectedElement = ref(null)
const readOnly = ref(false)
const saving = ref(false)

// 编辑器引用
const lfEditor = ref(null)

// 撤销/重做栈
const undoStack = ref([JSON.parse(JSON.stringify(graphData.value))])
const redoStack = ref([])
const canUndo = computed(() => undoStack.value.length > 1)
const canRedo = computed(() => redoStack.value.length > 0)

// 生命周期
onMounted(() => {
  // 初始化键盘快捷键
  window.addEventListener('keydown', onKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeyDown)
})

// 键盘快捷键
const onKeyDown = (e) => {
  // 检查当前焦点是否在输入元素上，如果是，不处理快捷键
  if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
    return
  }

  // Ctrl+S 保存
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault()
    save()
  }
  // Ctrl+Z 撤销
  else if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
    e.preventDefault()
    undo()
  }
  // Ctrl+Y 或 Ctrl+Shift+Z 重做
  else if (((e.ctrlKey || e.metaKey) && e.key === 'y') ||
           ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'z')) {
    e.preventDefault()
    redo()
  }
  // Delete 删除选中元素
  else if (e.key === 'Delete' || e.key === 'Backspace') {
    e.preventDefault()
    if (selectedElement.value) {
      handleDeleteElement(selectedElement.value.id)
    }
  }
  // ESC 取消选择
  else if (e.key === 'Escape') {
    handleClearSelection()
  }
}

// 保存状态
const saveState = () => {
  const state = JSON.parse(JSON.stringify(graphData.value))
  undoStack.value.push(state)
  redoStack.value = []
}

// 流程图变化
const handleFlowChange = (data) => {
  graphData.value = data

  // 如果当前有选中元素，更新选中元素的数据
  if (selectedElement.value) {
    const elementId = selectedElement.value.id
    if (selectedElement.value.type === 'node') {
      const updatedNode = graphData.value.nodes[elementId]
      if (updatedNode) {
        selectedElement.value = {
          ...selectedElement.value,
          ...updatedNode,
          nodeType: updatedNode.properties?.originalType || updatedNode.type
        }
      } else {
        selectedElement.value = null
      }
    } else {
      const updatedEdge = graphData.value.edges[elementId]
      if (updatedEdge) {
        selectedElement.value = {
          ...selectedElement.value,
          ...updatedEdge
        }
      } else {
        selectedElement.value = null
      }
    }
  }
}

// 元素选中
const handleElementSelected = (element) => {
  selectedElement.value = element
}

// 更新标题
const updateTitle = () => {
  emit('title-change', flowTitle.value)
}

// 保存流程图
const save = async () => {
  if (!lfEditor.value) return

  saving.value = true
  try {
    const data = lfEditor.value.getFlowData()

    // 触发保存事件
    const result = await emit('save', data)

    if (result !== false) {
      ElMessage.success('保存成功')
      saveState()
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 导出流程图
const exportFlowchart = async (format = 'svg') => {
  if (!lfEditor.value) return

  try {
    const imageData = await lfEditor.value.exportImage(format)
    if (imageData) {
      // 触发导出事件，传递格式参数
      emit('export', imageData, format)
    }
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

// 分享流程图
const shareFlowchart = () => {
  // 触发分享事件
  emit('share', props.flowchartId)
}

// 节点拖拽开始
const onNodeDragStart = (node) => {
  console.log('开始拖拽节点:', node)
}

// 更新元素
const handleUpdateElement = (element) => {
  if (!lfEditor.value) return

  if (element.type === 'node') {
    lfEditor.value.updateNodeProperties(element.id, element.properties)
  } else {
    lfEditor.value.updateEdgeProperties(element.id, element.properties)
  }
}

// 更新元素位置
const handleUpdateElementPosition = (position) => {
  if (!lfEditor.value || !selectedElement.value) return

  lfEditor.value.updateNodePosition(position.id, position.x, position.y)
}

// 更新节点类型
const handleUpdateNodeType = (nodeData) => {
  if (!lfEditor.value) return

  lfEditor.value.updateNodeType(nodeData.id, nodeData.nodeType)
}

// 删除元素
const handleDeleteElement = (elementId) => {
  if (!lfEditor.value) return

  const lf = lfEditor.value.getLogicFlowInstance()
  if (!lf) return

  // 从画布中删除
  lf.deleteElement(elementId)

  // 清空选中
  selectedElement.value = null

  // 保存状态
  setTimeout(() => {
    saveState()
  }, 100)
}

// 清空选择
const handleClearSelection = () => {
  selectedElement.value = null
}

// 保存事件
const handleSave = (data) => {
  save()
}

// 编辑器控制方法
const zoomIn = () => lfEditor.value?.zoomIn()
const zoomOut = () => lfEditor.value?.zoomOut()
const zoomReset = () => lfEditor.value?.zoomReset()
const fitView = () => lfEditor.value?.fitView()
const undo = () => {
  if (undoStack.value.length < 2) return

  const currentState = undoStack.value.pop()
  redoStack.value.push(currentState)
  const prevState = undoStack.value[undoStack.value.length - 1]

  // 更新数据
  graphData.value = { ...prevState }

  // 清空选中元素
  selectedElement.value = null

  // 通知编辑器重新渲染
  if (lfEditor.value) {
    const lf = lfEditor.value.getLogicFlowInstance()
    if (lf) {
      setTimeout(() => {
        lf.render(prevState)
      }, 0)
    }
  }
}
const redo = () => {
  if (redoStack.value.length === 0) return

  const nextState = redoStack.value.pop()
  undoStack.value.push(nextState)

  // 更新数据
  graphData.value = { ...nextState }

  // 清空选中元素
  selectedElement.value = null

  // 通知编辑器重新渲染
  if (lfEditor.value) {
    const lf = lfEditor.value.getLogicFlowInstance()
    if (lf) {
      setTimeout(() => {
        lf.render(nextState)
      }, 0)
    }
  }
}

// 暴露方法给父组件
defineExpose({
  // 获取流程图数据
  getFlowData: () => lfEditor.value?.getFlowData() || graphData.value,

  // 保存
  save,

  // 导出
  exportFlowchart: async () => {
    try {
      const imageData = await exportFlowchart()
      return { success: true, data: imageData }
    } catch (error) {
      return { success: false, message: error.message }
    }
  },

  // 编辑器控制
  zoomIn,
  zoomOut,
  zoomReset,
  fitView,
  undo,
  redo,

  // 获取编辑器实例
  getLogicFlowInstance: () => lfEditor.value?.getLogicFlowInstance(),

  // 设置只读模式
  setReadOnly: (readonly) => {
    readOnly.value = readonly
  }
})
</script>

<style scoped>
.flow-editor {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  position: relative;
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  z-index: 100;
  flex-shrink: 0;
}

.editor-main {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
}

.left-sidebar {
  width: 240px;
  min-width: 200px;
  max-width: 300px;
  height: 100%;
  border-right: 1px solid #e4e7ed;
  flex-shrink: 0;
  overflow-y: auto;
}

.editor-canvas {
  flex: 1;
  height: 100%;
  position: relative;
  background: #fafafa;
  overflow: hidden;
  min-height: 0; /* 重要：确保可以收缩 */
}

.graph-editor {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.right-sidebar {
  width: 320px;
  min-width: 280px;
  max-width: 400px;
  height: 100%;
  border-left: 1px solid #e4e7ed;
  flex-shrink: 0;
  overflow-y: auto;
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .left-sidebar {
    width: 200px;
  }

  .right-sidebar {
    width: 280px;
  }
}

@media (max-width: 992px) {
  .left-sidebar {
    display: none;
  }

  .right-sidebar {
    position: absolute;
    right: 0;
    top: 60px;
    bottom: 0;
    width: 100%;
    max-width: 400px;
    box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
    z-index: 100;
  }
}

@media (max-width: 768px) {
  .editor-toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
    padding: 12px;
  }

  .toolbar-left {
    flex-wrap: wrap;
  }
}
</style>