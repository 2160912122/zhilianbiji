<template>
  <div class="property-panel">
    <div class="panel-header">
      <h3>属性设置</h3>
      <el-button v-if="selectedElement" @click="clearSelection" size="small" type="text">
        <el-icon><Close /></el-icon>
      </el-button>
    </div>

    <div v-if="selectedElement" class="panel-content">
      <!-- 基本信息 -->
      <div class="section">
        <h4>基本信息</h4>
        <div class="form-group">
          <label>元素类型</label>
          <el-tag :type="selectedElement.type === 'node' ? 'primary' : 'success'" size="small">
            {{ selectedElement.type === 'node' ? '节点' : '连线' }}
          </el-tag>
        </div>

        <div class="form-group">
          <label>名称/标签</label>
          <el-input
            v-model="selectedElement.text"
            placeholder="请输入名称"
            @change="updateElement"
            size="small"
          />
        </div>

        <div v-if="selectedElement.type === 'node'" class="form-group">
          <label>节点类型</label>
          <el-select
            v-model="selectedElement.nodeType"
            @change="updateNodeType"
            size="small"
            style="width: 100%;"
          >
            <el-option label="开始" value="start" />
            <el-option label="结束" value="end" />
            <el-option label="处理" value="process" />
            <el-option label="子流程" value="subprocess" />
            <el-option label="定时器" value="timer" />
            <el-option label="判断" value="decision" />
            <el-option label="并行" value="parallel" />
            <el-option label="排他" value="exclusive" />
            <el-option label="事件" value="event" />
            <el-option label="数据输入" value="data-input" />
            <el-option label="数据输出" value="data-output" />
            <el-option label="数据库" value="database" />
            <el-option label="API" value="api" />
            <el-option label="文件" value="file" />
            <el-option label="文本" value="text" />
            <el-option label="注释" value="comment" />
          </el-select>
        </div>
      </div>

      <!-- 样式设置 -->
      <div class="section">
        <h4>样式设置</h4>

        <div class="form-group">
          <label>背景颜色</label>
          <div class="color-picker-container">
            <el-color-picker
              v-model="selectedElement.properties.fill"
              @change="onColorChange('fill')"
              size="small"
              :predefine="predefineColors"
              show-alpha
            />
            <div
              class="color-preview"
              :style="{ backgroundColor: selectedElement.properties.fill || '#409EFF' }"
            ></div>
          </div>
        </div>

        <div class="form-group">
          <label>边框颜色</label>
          <div class="color-picker-container">
            <el-color-picker
              v-model="selectedElement.properties.stroke"
              @change="onColorChange('stroke')"
              size="small"
              :predefine="predefineColors"
              show-alpha
            />
            <div
              class="color-preview"
              :style="{ backgroundColor: selectedElement.properties.stroke || '#333' }"
            ></div>
          </div>
        </div>

        <div class="form-group">
          <label>边框宽度</label>
          <el-input-number
            v-model="selectedElement.properties.strokeWidth"
            @change="updateElement"
            :min="1"
            :max="5"
            size="small"
            controls-position="right"
            style="width: 100%;"
          />
        </div>

        <div class="form-group" v-if="selectedElement.type === 'node'">
          <label>字体大小</label>
          <el-input-number
            v-model="selectedElement.properties.fontSize"
            @change="updateElement"
            :min="10"
            :max="24"
            size="small"
            controls-position="right"
            style="width: 100%;"
          />
        </div>
      </div>

      <!-- 位置设置 -->
      <div v-if="selectedElement.type === 'node'" class="section">
        <h4>位置设置</h4>
        <div class="form-group">
          <label>X坐标</label>
          <el-input-number
            v-model="selectedElement.x"
            @change="updateElementPosition"
            :min="0"
            :step="10"
            size="small"
            controls-position="right"
            style="width: 100%;"
          />
        </div>
        <div class="form-group">
          <label>Y坐标</label>
          <el-input-number
            v-model="selectedElement.y"
            @change="updateElementPosition"
            :min="0"
            :step="10"
            size="small"
            controls-position="right"
            style="width: 100%;"
          />
        </div>
      </div>

      <!-- 其他属性 -->
      <div class="section">
        <h4>其他属性</h4>
        <div class="form-group">
          <label>备注</label>
          <el-input
            v-model="selectedElement.properties.remark"
            type="textarea"
            :rows="2"
            placeholder="请输入备注信息"
            @change="updateElement"
            size="small"
          />
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button
          type="danger"
          @click="deleteElement"
          size="small"
          style="width: 100%;"
        >
          删除{{ selectedElement.type === 'node' ? '节点' : '连线' }}
        </el-button>
      </div>
    </div>

    <div v-else class="empty-panel">
      <el-empty description="选择元素进行编辑" :image-size="100" />
      <div class="help-text">
        <p>提示：</p>
        <ul>
          <li>点击画布中的节点或连线进行编辑</li>
          <li>从左侧拖拽节点到画布创建新节点</li>
          <li>双击节点或连线编辑文本</li>
          <li>使用 Delete 键删除选中元素</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Close } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'

const props = defineProps({
  selectedElement: {
    type: Object,
    default: null
  }
})

const emit = defineEmits([
  'update-element',
  'update-element-position',
  'update-node-type',
  'delete-element',
  'clear-selection'
])

// 预定义颜色
const predefineColors = ref([
  '#409EFF',
  '#67C23A',
  '#E6A23C',
  '#F56C6C',
  '#909399',
  '#FF9E29',
  '#9B26B6',
  '#00BCD4',
  '#FFFFFF',
  '#F0F9FF',
  '#FEF0F0',
  '#F0F9EB',
  '#FF0000',
  '#00FF00',
  '#0000FF',
  '#FFFF00',
  '#FF00FF',
  '#00FFFF'
])

// 清空选择
const clearSelection = () => {
  emit('clear-selection')
}

// 颜色变化处理
const onColorChange = (colorType) => {
  // 确保属性对象存在
  if (!props.selectedElement.properties) {
    props.selectedElement.properties = {}
  }

  // 触发元素更新
  updateElement()
}

// 更新元素
const updateElement = () => {
  // 确保属性对象存在
  if (!props.selectedElement.properties) {
    props.selectedElement.properties = {}
  }

  emit('update-element', { ...props.selectedElement })
}

// 更新元素位置
const updateElementPosition = () => {
  emit('update-element-position', {
    id: props.selectedElement.id,
    x: props.selectedElement.x,
    y: props.selectedElement.y
  })
}

// 更新节点类型
const updateNodeType = () => {
  // 确保 nodeType 有值
  if (!props.selectedElement.nodeType) {
    props.selectedElement.nodeType = 'process' // 设置默认值
  }

  // 确保属性对象存在
  if (!props.selectedElement.properties) {
    props.selectedElement.properties = {}
  }

  emit('update-node-type', {
    id: props.selectedElement.id,
    nodeType: props.selectedElement.nodeType
  })
}

// 删除元素
const deleteElement = () => {
  ElMessageBox.confirm(
    `确定要删除这个${props.selectedElement.type === 'node' ? '节点' : '连线'}吗？`,
    '提示',
    {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    }
  ).then(() => {
    emit('delete-element', props.selectedElement.id)
  }).catch(() => {
    // 取消删除
  })
}
</script>

<style scoped>
.property-panel {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-left: 1px solid #e4e7ed;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
  font-weight: 600;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.section {
  margin-bottom: 24px;
}

.section h4 {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: #606266;
  font-weight: 500;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
}

.color-picker-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-preview {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  cursor: pointer;
  transition: all 0.3s;
}

.color-preview:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.action-buttons {
  margin-top: 32px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.empty-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
}

.help-text {
  margin-top: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
  width: 100%;
}

.help-text p {
  margin: 0 0 8px 0;
  font-weight: 500;
  color: #303133;
}

.help-text ul {
  margin: 0;
  padding-left: 18px;
  color: #606266;
}

.help-text li {
  margin-bottom: 4px;
  font-size: 13px;
}
</style>