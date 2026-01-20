<template>
  <div class="logic-flow-editor" ref="editorContainer">
    <div id="lf-container" 
         ref="container"
         @dragover.prevent
         @drop="onDrop"
         @dragenter.prevent
         @dragleave.prevent
    ></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import html2canvas from 'html2canvas'

// LogicFlow 导入
import LogicFlow from '@logicflow/core'
import '@logicflow/core/dist/style/index.css'

// 扩展插件
import { DndPanel, SelectionSelect, MiniMap, Control, Menu } from '@logicflow/extension'
import '@logicflow/extension/lib/style/index.css'

const props = defineProps({
  flowData: {
    type: Object,
    default: () => ({ nodes: {}, edges: {} })
  },
  readOnly: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:flowData', 'change', 'save', 'element-selected'])

const container = ref(null)
const lf = ref(null)
const isInitialized = ref(false)

// 节点类型映射表
const nodeTypeMap = {
  // 流程节点
  'start': 'circle',
  'end': 'circle',
  'process': 'rect',
  'subprocess': 'rect',
  'timer': 'rect',

  // 逻辑节点
  'decision': 'diamond',
  'parallel': 'diamond',
  'exclusive': 'diamond',
  'event': 'rect',

  // 数据节点
  'data-input': 'rect',
  'data-output': 'rect',
  'database': 'rect',
  'api': 'rect',
  'file': 'rect',
  'text': 'rect',
  'comment': 'rect'
}

// 节点颜色映射 - 作为默认值，而不是强制值
const nodeColorMap = {
  'start': '#67C23A',
  'end': '#F56C6C',
  'process': '#409EFF',
  'subprocess': '#909399',
  'timer': '#E6A23C',
  'decision': '#E6A23C',
  'parallel': '#67C23A',
  'exclusive': '#E6A23C',
  'event': '#F56C6C',
  'data-input': '#409EFF',
  'data-output': '#409EFF',
  'database': '#909399',
  'api': '#409EFF',
  'file': '#909399',
  'text': '#FFFFFF',
  'comment': '#F0F9FF'
}

// 外部拖拽放置事件
const onDrop = (event) => {
  event.preventDefault()
  event.stopPropagation()

  if (!lf.value || props.readOnly) {
    console.warn('LogicFlow 实例尚未初始化或只读模式')
    return
  }

  try {
    const nodeDataStr = event.dataTransfer.getData('nodeData')
    if (!nodeDataStr) return

    const nodeData = JSON.parse(nodeDataStr)

    const rect = container.value.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top
    const position = lf.value.getPointByClient(x, y)

    // 映射节点类型
    const nodeType = nodeTypeMap[nodeData.type] || 'rect'
    const nodeColor = nodeData.properties?.fill || nodeColorMap[nodeData.type] || '#409EFF'

    // 创建节点
    const newNode = {
      id: `node_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type: nodeType,
      x: position.x || x,
      y: position.y || y,
      text: nodeData.text || nodeData.label || '节点',
      style: {
        fill: nodeColor,
        stroke: '#333',
        strokeWidth: 2
      },
      properties: {
        originalType: nodeData.type,
        fill: nodeColor,
        stroke: '#333',
        strokeWidth: 2,
        ...nodeData.properties
      }
    }

    // 为不同类型节点设置特殊属性
    if (nodeType === 'diamond') {
      newNode.style.rx = 30
      newNode.style.ry = 30
      newNode.properties.rx = 30
      newNode.properties.ry = 30
    } else if (nodeType === 'circle') {
      newNode.style.rx = 0
      newNode.style.ry = 0
      newNode.properties.rx = 0
      newNode.properties.ry = 0
    } else {
      newNode.style.rx = 6
      newNode.style.ry = 6
      newNode.properties.rx = 6
      newNode.properties.ry = 6
    }

    // 为文本和注释节点设置特殊大小
    if (nodeData.type === 'text' || nodeData.type === 'comment') {
      newNode.style.width = 200
      newNode.style.height = 80
      newNode.properties.width = 200
      newNode.properties.height = 80
    }

    // 添加节点到画布
    lf.value.addNode(newNode)
    emitChange()

  } catch (error) {
    console.error('处理拖拽节点失败:', error)
    ElMessage.error('添加节点失败')
  }
}

// 初始化 LogicFlow
const initLogicFlow = async () => {
  if (!container.value) return

  await nextTick()
  const rect = container.value.getBoundingClientRect()
  if (rect.width === 0 || rect.height === 0) {
    setTimeout(initLogicFlow, 100)
    return
  }

  try {
    // 注册扩展
    LogicFlow.use(DndPanel)
    LogicFlow.use(SelectionSelect)
    LogicFlow.use(MiniMap)
    LogicFlow.use(Control)
    LogicFlow.use(Menu)

    // 创建实例 - 移除默认蓝色设置
    lf.value = new LogicFlow({
      container: container.value,
      width: rect.width,
      height: rect.height,
      grid: {
        size: 20,
        visible: true,
        type: 'dot'
      },
      background: {
        color: '#fafafa'
      },
      keyboard: { enabled: true },
      snapline: true,
      history: true,
      stopScrollGraph: false,
      stopZoomGraph: false,
      adjustEdge: true,
      adjustNodePosition: true,
      hoverOutline: false,
      edgeTextDraggable: true,
      nodeTextDraggable: true,
      // 允许重复连线 - 关键修复！
      allowRepeatEdge: true,  // 添加这个配置
      // 自定义节点样式 - 移除固定颜色设置
      style: {
        rect: {
          rx: 6,
          ry: 6,
          strokeWidth: 2,
          stroke: '#333',
          fill: 'transparent' // 改为透明，让节点数据决定颜色
        },
        circle: {
          strokeWidth: 2,
          stroke: '#333',
          fill: 'transparent' // 改为透明
        },
        diamond: {
          strokeWidth: 2,
          stroke: '#333',
          fill: 'transparent', // 改为透明
          rx: 30,
          ry: 30
        },
        polyline: {
          strokeWidth: 2,
          stroke: '#409EFF',
          hoverStroke: '#67C23A',
          selectedStroke: '#E6A23C'
        },
        nodeText: {
          fontSize: 14,
          color: '#333',
          background: {
            fill: 'transparent',
            stroke: 'transparent',
            radius: 0
          }
        },
        edgeText: {
          fontSize: 12,
          color: '#666',
          background: {
            fill: 'white',
            stroke: 'white',
            radius: 4
          }
        }
      }
    })

    // 设置只读模式
    if (props.readOnly) {
      lf.value.updateEditConfig({
        isSilentMode: true
      })
    }

    // 渲染
    lf.value.render()

    // 标记为已初始化
    isInitialized.value = true

    // 加载数据
    if (props.flowData && (Object.keys(props.flowData.nodes).length > 0 || Object.keys(props.flowData.edges).length > 0)) {
      loadFlowData(props.flowData)
    }

    // 设置事件监听器
    setupEventListeners()

  } catch (error) {
    console.error('初始化 LogicFlow 失败:', error)
    ElMessage.error('编辑器初始化失败')
  }
}

// 加载流程图数据 - 修复清空画布问题
const loadFlowData = (flowData) => {
  if (!lf.value || !isInitialized.value) return

  try {
    const { nodes, edges } = flowData

    // 检查是否为空数据
    const isEmptyData = !nodes || Object.keys(nodes).length === 0

    if (isEmptyData) {
      // 清空画布
      lf.value.clearData()
      lf.value.render()
      return
    }

    const lfNodes = []
    const lfEdges = []

    // 转换节点数据 - 修复颜色读取逻辑
    Object.values(nodes).forEach(node => {
      if (!node || !node.id) return

      // 映射节点类型
      const nodeType = nodeTypeMap[node.type] || 'rect'

      // 优先使用节点数据中的颜色，否则使用默认颜色
      const nodeColor = node.color || node.properties?.fill || nodeColorMap[node.type] || '#409EFF'

      const lfNode = {
        id: node.id,
        type: nodeType,
        x: node.x || 100,
        y: node.y || 100,
        text: node.text || node.label || node.name || '节点',
        style: {
          fill: nodeColor, // 使用节点自己的颜色
          stroke: node.stroke || '#333',
          strokeWidth: node.strokeWidth || 2
        },
        properties: {
          originalType: node.type,
          fill: nodeColor, // 保存到 properties
          stroke: node.stroke || '#333',
          strokeWidth: node.strokeWidth || 2,
          ...(node.properties || {})
        }
      }

      // 设置特殊属性
      if (nodeType === 'diamond') {
        lfNode.style.rx = 30
        lfNode.style.ry = 30
        lfNode.properties.rx = 30
        lfNode.properties.ry = 30
      } else if (nodeType === 'circle') {
        lfNode.style.rx = 0
        lfNode.style.ry = 0
        lfNode.properties.rx = 0
        lfNode.properties.ry = 0
      } else {
        lfNode.style.rx = 6
        lfNode.style.ry = 6
        lfNode.properties.rx = 6
        lfNode.properties.ry = 6
      }

      lfNodes.push(lfNode)
    })

    // 转换边数据 - 确保边有唯一ID
    Object.values(edges || {}).forEach(edge => {
      if (!edge || !edge.source || !edge.target) return

      lfEdges.push({
        id: edge.id || `edge_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: 'polyline',
        sourceNodeId: edge.source,
        targetNodeId: edge.target,
        text: edge.text || edge.label || '',
        style: {
          stroke: edge.color || edge.properties?.stroke || '#409EFF',
          strokeWidth: edge.width || 2
        },
        properties: edge.properties || {}
      })
    })

    // 清除现有数据并重新渲染
    lf.value.clearData()
    lf.value.render({
      nodes: lfNodes,
      edges: lfEdges
    })
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

// 获取流程图数据 - 修复边数据格式
const getFlowData = () => {
  if (!lf.value) {
    return { nodes: {}, edges: {} }
  }

  try {
    const data = lf.value.getGraphData()
    const flowData = {
      nodes: {},
      edges: {}
    }

    // 转换节点数据
    data.nodes?.forEach(node => {
      const originalType = node.properties?.originalType || node.type

      flowData.nodes[node.id] = {
        id: node.id,
        type: originalType,
        x: node.x,
        y: node.y,
        text: node.text,
        label: node.text,
        name: node.text,
        color: node.style?.fill || node.properties?.fill || '#409EFF',
        stroke: node.style?.stroke || node.properties?.stroke || '#333',
        strokeWidth: node.style?.strokeWidth || node.properties?.strokeWidth || 2,
        properties: node.properties || {}
      }
    })

    // 转换边数据 - 确保格式正确
    data.edges?.forEach(edge => {
      flowData.edges[edge.id] = {
        id: edge.id,
        source: edge.sourceNodeId,
        target: edge.targetNodeId,
        text: edge.text,
        label: edge.text,
        color: edge.style?.stroke || edge.properties?.stroke || '#409EFF',
        width: edge.style?.strokeWidth || edge.properties?.strokeWidth || 2,
        properties: edge.properties || {}
      }
    })

    return flowData
  } catch (error) {
    console.error('获取数据失败:', error)
    return { nodes: {}, edges: {} }
  }
}

// 触发变化事件
const emitChange = () => {
  try {
    const data = getFlowData()
    emit('update:flowData', data)
    emit('change', data)
  } catch (error) {
    console.error('触发变化失败:', error)
  }
}

// 设置事件监听器
const setupEventListeners = () => {
  if (!lf.value) return

  // 节点双击编辑文本
  lf.value.on('node:dblclick', ({ data }) => {
    lf.value.editText(data.id)
  })

  // 边双击编辑文本
  lf.value.on('edge:dblclick', ({ data }) => {
    lf.value.editText(data.id)
  })

  // 文本更新
  lf.value.on('text:update', () => {
    emitChange()
  })

  // 元素变化事件
  const changeEvents = [
    'node:add', 'node:delete', 'node:drag', 'node:drop',
    'edge:add', 'edge:delete', 'edge:drag', 'edge:drop',
    'node:update', 'edge:update', 'node:resize'
  ]

  changeEvents.forEach(event => {
    lf.value.on(event, () => {
      setTimeout(emitChange, 0)
    })
  })

  // 键盘事件
  lf.value.on('keydown:backspace', () => {
    lf.value.deleteSelectedElements()
  })
  lf.value.on('keydown:delete', () => {
    lf.value.deleteSelectedElements()
  })

  // 元素选中事件
  lf.value.on('node:click', ({ data }) => {
    const originalType = data.properties?.originalType || data.type

    const selectedNode = {
      id: data.id,
      type: 'node',
      nodeType: originalType,
      x: data.x,
      y: data.y,
      text: data.text,
      label: data.text,
      name: data.text,
      color: data.style?.fill || data.properties?.fill || '#409EFF',
      stroke: data.style?.stroke || data.properties?.stroke || '#333',
      strokeWidth: data.style?.strokeWidth || data.properties?.strokeWidth || 2,
      properties: data.properties || {}
    }
    emit('element-selected', selectedNode)
  })

  lf.value.on('edge:click', ({ data }) => {
    const selectedEdge = {
      id: data.id,
      type: 'edge',
      source: data.sourceNodeId,
      target: data.targetNodeId,
      text: data.text,
      label: data.text,
      color: data.style?.stroke || data.properties?.stroke || '#409EFF',
      width: data.style?.strokeWidth || data.properties?.strokeWidth || 2,
      properties: data.properties || {}
    }
    emit('element-selected', selectedEdge)
  })
}

// 更新节点类型
const updateNodeType = (nodeId, newType) => {
  if (!lf.value) return

  const node = lf.value.getNodeModelById(nodeId)
  if (node) {
    // 映射新的类型
    const mappedType = nodeTypeMap[newType] || 'rect'
    const currentNode = node.getData()

    // 获取当前颜色或使用新类型的默认颜色
    const currentColor = currentNode.style?.fill || currentNode.properties?.fill
    const defaultColor = nodeColorMap[newType] || '#409EFF'
    const nodeColor = currentColor || defaultColor

    // 更新节点数据，确保样式正确设置
    lf.value.updateNodeData({
      id: nodeId,
      type: mappedType,
      x: currentNode.x,
      y: currentNode.y,
      text: currentNode.text || '',
      style: {
        ...currentNode.style,
        fill: nodeColor
      },
      properties: {
        ...currentNode.properties,
        originalType: newType,
        fill: nodeColor
      }
    })

    // 立即重新渲染
    lf.value.render()
    emitChange()
  }
}

// 更新节点位置
const updateNodePosition = (nodeId, x, y) => {
  if (!lf.value) return

  const node = lf.value.getNodeModelById(nodeId)
  if (node) {
    const currentNode = node.getData()

    lf.value.updateNodeData({
      id: nodeId,
      type: currentNode.type,
      x: x,
      y: y,
      text: currentNode.text || '',
      style: currentNode.style || {},
      properties: currentNode.properties || {}
    })

    emitChange()
  }
}

// 更新节点属性 - 修复方法
const updateNodeProperties = (nodeId, properties) => {
  if (!lf.value) return

  const node = lf.value.getNodeModelById(nodeId)
  if (node) {
    const currentNode = node.getData()

    // 确保颜色优先使用 properties 中的设置
    const fillColor = properties.fill || currentNode.properties?.fill || currentNode.style?.fill || '#409EFF'
    const strokeColor = properties.stroke || currentNode.properties?.stroke || currentNode.style?.stroke || '#333'
    const strokeWidth = properties.strokeWidth || currentNode.properties?.strokeWidth || currentNode.style?.strokeWidth || 2
    const fontSize = properties.fontSize || currentNode.properties?.fontSize || currentNode.style?.fontSize || 14

    // 创建新的节点数据，确保样式正确设置
    const newNodeData = {
      id: nodeId,
      type: currentNode.type,
      x: currentNode.x,
      y: currentNode.y,
      text: currentNode.text || '',
      style: {
        ...(currentNode.style || {}),
        fill: fillColor,
        stroke: strokeColor,
        strokeWidth: strokeWidth,
        fontSize: fontSize
      },
      properties: {
        ...currentNode.properties,
        ...properties,
        fill: fillColor,
        stroke: strokeColor,
        strokeWidth: strokeWidth,
        fontSize: fontSize
      }
    }

    // 使用 updateNodeData 方法更新节点
    lf.value.updateNodeData(newNodeData)

    // 强制重新渲染
    setTimeout(() => {
      lf.value.render()
      emitChange()
    }, 0)
  }
}

// 更新边属性 - 修复方法
const updateEdgeProperties = (edgeId, properties) => {
  if (!lf.value) return

  const edge = lf.value.getEdgeModelById(edgeId)
  if (edge) {
    const currentEdge = edge.getData()

    // 确保颜色优先使用 properties 中的设置
    const strokeColor = properties.stroke || currentEdge.properties?.stroke || currentEdge.style?.stroke || '#409EFF'
    const strokeWidth = properties.strokeWidth || currentEdge.properties?.strokeWidth || currentEdge.style?.strokeWidth || 2

    // 创建新的边数据
    const newEdgeData = {
      id: edgeId,
      type: currentEdge.type,
      sourceNodeId: currentEdge.sourceNodeId,
      targetNodeId: currentEdge.targetNodeId,
      text: currentEdge.text || '',
      style: {
        ...(currentEdge.style || {}),
        stroke: strokeColor,
        strokeWidth: strokeWidth
      },
      properties: {
        ...currentEdge.properties,
        ...properties,
        stroke: strokeColor,
        strokeWidth: strokeWidth
      }
    }

    // 使用 updateEdgeData 方法更新边
    lf.value.updateEdgeData(newEdgeData)

    // 强制重新渲染
    setTimeout(() => {
      lf.value.render()
      emitChange()
    }, 0)
  }
}

// 监听 flowData 变化
watch(() => props.flowData, (newVal) => {
  if (lf.value && isInitialized.value) {
    loadFlowData(newVal)
  }
}, { deep: true })

// 生命周期
onMounted(() => {
  setTimeout(initLogicFlow, 200)
})

onUnmounted(() => {
  if (lf.value) {
    try {
      lf.value.destroy?.()
    } catch (error) {
      console.error('销毁失败:', error)
    }
  }
})

// 清空画布方法
const clearCanvas = () => {
  if (lf.value) {
    lf.value.clearData()
    lf.value.render()
    emitChange()
  }
}

// 暴露方法给父组件
defineExpose({
  getFlowData,
  save: () => {
    const data = getFlowData()
    emit('save', data)
    return data
  },
  exportImage: async (format = 'svg') => {
    if (!lf.value) return ''
    try {
      // 获取LogicFlow的graph容器
      const graphContainer = container.value.querySelector('.lf-canvas-container')
      if (!graphContainer) return ''
      
      if (format === 'svg') {
        // SVG导出逻辑保持不变
        const svgElement = container.value.querySelector('.lf-graph')
        if (!svgElement) return ''
        
        const svgData = new XMLSerializer().serializeToString(svgElement)
        const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
        return URL.createObjectURL(svgBlob)
      } else if (format === 'png') {
        // 使用html2canvas将整个graph容器转换为PNG
        const canvas = await html2canvas(graphContainer, {
          backgroundColor: '#ffffff', // 确保背景是白色
          scale: window.devicePixelRatio, // 提高分辨率
          logging: false,
          useCORS: true, // 允许跨域图片
          width: graphContainer.offsetWidth,
          height: graphContainer.offsetHeight
        })
        
        // 将Canvas转换为PNG Blob
        return new Promise((resolve) => {
          canvas.toBlob((blob) => {
            if (blob) {
              resolve(URL.createObjectURL(blob))
            } else {
              console.error('Canvas toBlob failed')
              resolve('')
            }
          }, 'image/png', 1.0)
        })
      }
      return ''
    } catch (error) {
      console.error('导出图片失败:', error)
      ElMessage.error(`导出${format}失败: ${error.message}`)
      return ''
    }
  },
  zoomIn: () => lf.value?.zoomIn(),
  zoomOut: () => lf.value?.zoomOut(),
  zoomReset: () => lf.value?.zoomTo(1),
  fitView: () => lf.value?.fitView(),
  undo: () => lf.value?.undo(),
  redo: () => lf.value?.redo(),
  // 新增的更新方法
  updateNodeType,
  updateNodePosition,
  updateNodeProperties,
  updateEdgeProperties,
  // 清空画布方法
  clearCanvas,
  getLogicFlowInstance: () => lf.value
})
</script>

<style scoped>
.logic-flow-editor {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  flex-direction: column;
}

#lf-container {
  width: 100%;
  height: 100%;
  min-height: 500px;
  background-color: #fafafa;
  flex: 1;
  position: relative;
}
</style>