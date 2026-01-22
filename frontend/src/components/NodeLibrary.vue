<template>
  <div class="node-library">
    <div class="library-header">
      <el-input
        v-model="searchText"
        placeholder="搜索节点"
        size="small"
        clearable
        @input="filterNodes"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <div class="library-content">
      <!-- 流程节点 -->
      <div class="category-section">
        <h4>流程节点</h4>
        <div class="category-nodes">
          <div
            v-for="node in filteredFlowNodes"
            :key="node.type"
            class="node-item"
            draggable="true"
            @dragstart="onDragStart(node)"
            @click="onNodeClick(node)"
          >
            <div class="node-icon-container">
              <div
                class="node-color-preview"
                :style="{ backgroundColor: node.color }"
              ></div>
              <div
                :class="['node-shape', node.shape]"
                :style="getShapeStyle(node)"
              ></div>
            </div>
            <span class="node-label">{{ node.label }}</span>
          </div>
        </div>
      </div>

      <!-- 逻辑节点 -->
      <div class="category-section">
        <h4>逻辑节点</h4>
        <div class="category-nodes">
          <div
            v-for="node in filteredLogicNodes"
            :key="node.type"
            class="node-item"
            draggable="true"
            @dragstart="onDragStart(node)"
            @click="onNodeClick(node)"
          >
            <div class="node-icon-container">
              <div
                class="node-color-preview"
                :style="{ backgroundColor: node.color }"
              ></div>
              <div
                :class="['node-shape', node.shape]"
                :style="getShapeStyle(node)"
              ></div>
            </div>
            <span class="node-label">{{ node.label }}</span>
          </div>
        </div>
      </div>

      <!-- 数据节点 -->
      <div class="category-section">
        <h4>数据节点</h4>
        <div class="category-nodes">
          <div
            v-for="node in filteredDataNodes"
            :key="node.type"
            class="node-item"
            draggable="true"
            @dragstart="onDragStart(node)"
            @click="onNodeClick(node)"
          >
            <div class="node-icon-container">
              <div
                class="node-color-preview"
                :style="{ backgroundColor: node.color }"
              ></div>
              <div
                :class="['node-shape', node.shape]"
                :style="getShapeStyle(node)"
              ></div>
            </div>
            <span class="node-label">{{ node.label }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'

const nodeCategories = {
  flowNodes: [
    { type: 'start', label: '开始', color: '#67C23A', shape: 'circle' },
    { type: 'end', label: '结束', color: '#F56C6C', shape: 'circle' },
    { type: 'process', label: '处理', color: '#409EFF', shape: 'rect' },
    { type: 'subprocess', label: '子流程', color: '#909399', shape: 'rect' },
    { type: 'timer', label: '定时器', color: '#E6A23C', shape: 'rect' }
  ],

  logicNodes: [
    { type: 'decision', label: '判断', color: '#E6A23C', shape: 'diamond' },
    { type: 'parallel', label: '并行', color: '#67C23A', shape: 'diamond' },
    { type: 'exclusive', label: '排他', color: '#E6A23C', shape: 'diamond' },
    { type: 'event', label: '事件', color: '#F56C6C', shape: 'rect' }
  ],

  dataNodes: [
    { type: 'data-input', label: '数据输入', color: '#409EFF', shape: 'rect' },
    { type: 'data-output', label: '数据输出', color: '#409EFF', shape: 'rect' },
    { type: 'database', label: '数据库', color: '#909399', shape: 'database' },
    { type: 'api', label: 'API', color: '#409EFF', shape: 'rect' },
    { type: 'file', label: '文件', color: '#909399', shape: 'rect' },
    { type: 'text', label: '文本', color: '#FFFFFF', shape: 'rect' },
    { type: 'comment', label: '注释', color: '#F0F9FF', shape: 'rect' }
  ]
}

const searchText = ref('')
const emit = defineEmits(['node-drag-start'])

const getBorderColor = (color) => {
  const hex = color.replace('#', '')
  const r = parseInt(hex.substr(0, 2), 16)
  const g = parseInt(hex.substr(2, 2), 16)
  const b = parseInt(hex.substr(4, 2), 16)

  const brightness = (r * 299 + g * 587 + b * 114) / 1000

  return brightness > 200 ? '#333' : 'rgba(255,255,255,0.8)'
}

const getShapeStyle = (node) => {
  const shapeColor = node.shape === 'text' || node.shape === 'comment' ? '#333' : 'white'
  const borderColor = getBorderColor(node.color)

  return {
    backgroundColor: shapeColor,
    borderColor: borderColor
  }
}

const filterNodes = (nodes) => {
  if (!searchText.value) return nodes
  return nodes.filter(node =>
    node.label.toLowerCase().includes(searchText.value.toLowerCase())
  )
}

const filteredFlowNodes = computed(() => filterNodes(nodeCategories.flowNodes))
const filteredLogicNodes = computed(() => filterNodes(nodeCategories.logicNodes))
const filteredDataNodes = computed(() => filterNodes(nodeCategories.dataNodes))

const onDragStart = (node) => {
  const event = window.event
  const transferData = JSON.stringify({
    type: node.type,
    text: node.label,
    label: node.label,
    properties: {
      fill: node.color,
      shape: node.shape
    }
  })
  event.dataTransfer.setData('nodeData', transferData)
  event.dataTransfer.effectAllowed = 'copy'
  emit('node-drag-start', node)
}

const onNodeClick = (node) => {
  console.log('节点点击:', node)
}
</script>

<style scoped>
.node-library {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-right: 1px solid #e4e7ed;
}

.library-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.library-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.category-section {
  margin-bottom: 24px;
}

.category-section h4 {
  margin: 0 0 12px 0;
  color: #606266;
  font-weight: 500;
  font-size: 14px;
}

.category-nodes {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.node-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  cursor: move;
  user-select: none;
  transition: all 0.2s;
  text-align: center;
}

.node-item:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.node-icon-container {
  position: relative;
  width: 40px;
  height: 40px;
  margin-bottom: 8px;
}

.node-color-preview {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 6px;
  opacity: 0.2;
}

.node-shape {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 24px;
  height: 24px;
  border: 2px solid;
  box-sizing: border-box;
}

.node-shape.circle {
  border-radius: 50%;
}

.node-shape.rect {
  border-radius: 3px;
}

.node-shape.diamond {
  transform: translate(-50%, -50%) rotate(45deg);
  width: 20px;
  height: 20px;
}

.node-shape.database {
  position: relative;
  width: 24px;
  height: 16px;
  border-radius: 3px;
}

.node-shape.database::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  height: 6px;
  border-radius: 3px 3px 0 0;
  border: 2px solid;
  border-bottom: none;
  box-sizing: border-box;
  background: inherit;
}

.node-label {
  font-size: 12px;
  color: #606266;
  line-height: 1.2;
}
</style>
