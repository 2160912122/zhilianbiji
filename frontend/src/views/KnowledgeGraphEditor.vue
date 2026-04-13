<template>
  <div class="knowledge-graph-editor">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isNew ? '新建知识图谱' : '编辑知识图谱' }}</span>
          <div class="header-buttons">
            <el-button type="primary" @click="saveGraph">保存</el-button>
            <el-button @click="$router.push('/knowledge-graphs')">返回</el-button>
          </div>
        </div>
      </template>
      
      <div class="graph-form">
        <el-form :model="graphForm" label-width="80px">
          <el-form-item label="图谱名称">
            <el-input v-model="graphForm.name" placeholder="请输入图谱名称" />
          </el-form-item>
          <el-form-item label="图谱描述">
            <el-input v-model="graphForm.description" type="textarea" placeholder="请输入图谱描述" />
          </el-form-item>
        </el-form>
      </div>
      
      <div class="graph-editor-container">
        <div class="editor-sidebar">
          <div class="sidebar-section">
            <h3>节点管理</h3>
            <el-button type="primary" @click="showAddNodeDialog">添加节点</el-button>
            <el-tree
              :data="nodesTree"
              :props="treeProps"
              @node-click="handleNodeClick"
              class="nodes-tree"
            />
          </div>
          
          <div class="sidebar-section">
            <h3>关系管理</h3>
            <el-button type="primary" @click="showAddRelationDialog">
              添加关系
            </el-button>
            <el-card v-if="selectedNode" class="relations-card">
              <template #header>
                <div class="card-header">
                  <span>相关关系</span>
                </div>
              </template>
              <div v-for="relation in getNodeRelations(selectedNode.id)" :key="relation.id" class="relation-item">
                <span>{{ relation.label || relation.type }}</span>
                <el-button link type="danger" @click.stop="deleteRelation(relation.id)">删除</el-button>
              </div>
            </el-card>
          </div>
        </div>
        
        <div class="graph-canvas">
          <div ref="graphContainer" class="graph-container"></div>
        </div>
      </div>
    </el-card>
    
    <!-- 添加节点对话框 -->
    <el-dialog
      v-model="addNodeDialogVisible"
      title="添加节点"
      width="500px"
    >
      <el-form :model="nodeForm" label-width="80px">
        <el-form-item label="节点类型">
          <el-select v-model="nodeForm.type" placeholder="请选择节点类型">
            <el-option label="概念" value="concept" />
            <el-option label="原理" value="principle" />
            <el-option label="应用" value="application" />
          </el-select>
        </el-form-item>
        <el-form-item label="节点名称">
          <el-input v-model="nodeForm.name" placeholder="请输入节点名称" />
        </el-form-item>
        <el-form-item label="节点内容">
          <el-input v-model="nodeForm.content" type="textarea" placeholder="请输入节点内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addNodeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="addNode">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 添加关系对话框 -->
    <el-dialog
      v-model="addRelationDialogVisible"
      title="添加关系"
      width="500px"
    >
      <el-form :model="relationForm" label-width="80px">
        <el-form-item label="源节点">
          <el-select v-model="relationForm.source_id" placeholder="请选择源节点">
            <el-option v-for="node in nodes" :key="node.id" :label="node.name" :value="node.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="目标节点">
          <el-select v-model="relationForm.target_id" placeholder="请选择目标节点">
            <el-option v-for="node in nodes" :key="node.id" :label="node.name" :value="node.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="关系类型">
          <el-select v-model="relationForm.type" placeholder="请选择关系类型">
            <el-option label="相关" value="related" />
            <el-option label="包含" value="contains" />
            <el-option label="继承" value="inherits" />
            <el-option label="因果" value="causes" />
          </el-select>
        </el-form-item>
        <el-form-item label="关系标签">
          <el-input v-model="relationForm.label" placeholder="请输入关系标签" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addRelationDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="addRelation">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const router = useRouter()
const route = useRoute()

const graphId = route.params.id
const isNew = !graphId

const graphForm = ref({
  name: '',
  description: ''
})

const nodes = ref([])
const relations = ref([])
const selectedNode = ref(null)
const selectedSourceNode = ref(null)
const selectedTargetNode = ref(null)

const addNodeDialogVisible = ref(false)
const addRelationDialogVisible = ref(false)

const nodeForm = ref({
  type: 'concept',
  name: '',
  content: ''
})

const relationForm = ref({
  source_id: '',
  target_id: '',
  type: 'related',
  label: ''
})

const graphContainer = ref(null)
let graphChart = null

const nodesTree = computed(() => {
  return nodes.value.map(node => ({
    id: node.id,
    label: node.name,
    type: node.type
  }))
})

const treeProps = {
  label: 'label',
  children: 'children'
}

async function loadGraph() {
  if (!isNew) {
    try {
      const response = await fetch(`/api/knowledge-graphs/${graphId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      })
      const result = await response.json()
      
      if (result.code === 200) {
        graphForm.value = result.data.graph
        nodes.value = result.data.nodes
        relations.value = result.data.relations
        initGraph()
      } else {
        ElMessage.error(result.message || '加载图谱失败')
      }
    } catch (error) {
      console.error('Load graph error:', error)
      ElMessage.error('加载图谱失败')
    }
  }
}

async function saveGraph() {
  try {
    if (!graphForm.value.name) {
      ElMessage.error('图谱名称不能为空')
      return
    }
    
    let response
    if (isNew) {
      response = await fetch('/api/knowledge-graphs', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(graphForm.value)
      })
    } else {
      response = await fetch(`/api/knowledge-graphs/${graphId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(graphForm.value)
      })
    }
    
    const result = await response.json()
    if (result.code === 200) {
      ElMessage.success('保存成功')
      if (isNew) {
        router.push(`/knowledge-graphs/${result.data.id}`)
      }
    } else {
      ElMessage.error(result.message || '保存失败')
    }
  } catch (error) {
    console.error('Save graph error:', error)
    ElMessage.error('保存失败')
  }
}

function showAddNodeDialog() {
  nodeForm.value = {
    type: 'concept',
    name: '',
    content: ''
  }
  addNodeDialogVisible.value = true
}

async function addNode() {
  try {
    if (!nodeForm.value.name) {
      ElMessage.error('节点名称不能为空')
      return
    }
    
    let currentGraphId = graphId
    if (isNew) {
      // 先保存图谱获取ID
      const saveResponse = await fetch('/api/knowledge-graphs', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(graphForm.value)
      })
      
      const saveResult = await saveResponse.json()
      if (saveResult.code === 200) {
        currentGraphId = saveResult.data.id
        // 保存节点
        const nodeResponse = await fetch(`/api/knowledge-graphs/${currentGraphId}/nodes`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(nodeForm.value)
        })
        
        const nodeResult = await nodeResponse.json()
        if (nodeResult.code === 200) {
          // 跳转到新创建的图谱编辑页面
          router.push(`/knowledge-graphs/${currentGraphId}`)
          ElMessage.success('图谱和节点保存成功')
          addNodeDialogVisible.value = false
          return
        } else {
          ElMessage.error('保存节点失败')
          return
        }
      } else {
        ElMessage.error('保存图谱失败，请先填写图谱基本信息')
        return
      }
    }
    
    const response = await fetch(`/api/knowledge-graphs/${currentGraphId}/nodes`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(nodeForm.value)
    })
    
    const result = await response.json()
    if (result.code === 200) {
      nodes.value.push(result.data)
      initGraph()
      addNodeDialogVisible.value = false
      ElMessage.success('添加节点成功')
    } else {
      ElMessage.error(result.message || '添加节点失败')
    }
  } catch (error) {
    console.error('Add node error:', error)
    ElMessage.error('添加节点失败')
  }
}

function showAddRelationDialog() {
  relationForm.value = {
    source_id: selectedSourceNode.value?.id || '',
    target_id: selectedTargetNode.value?.id || '',
    type: 'related',
    label: ''
  }
  addRelationDialogVisible.value = true
}

async function addRelation() {
  try {
    if (!relationForm.value.source_id || !relationForm.value.target_id) {
      ElMessage.error('源节点和目标节点不能为空')
      return
    }
    
    const response = await fetch(`/api/knowledge-graphs/${graphId}/relations`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(relationForm.value)
    })
    
    const result = await response.json()
    if (result.code === 200) {
      relations.value.push(result.data)
      initGraph()
      addRelationDialogVisible.value = false
      ElMessage.success('添加关系成功')
    } else {
      ElMessage.error(result.message || '添加关系失败')
    }
  } catch (error) {
    console.error('Add relation error:', error)
    ElMessage.error('添加关系失败')
  }
}

async function deleteRelation(relationId) {
  try {
    const response = await fetch(`/api/knowledge-graphs/${graphId}/relations/${relationId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      }
    })
    
    const result = await response.json()
    if (result.code === 200) {
      relations.value = relations.value.filter(r => r.id !== relationId)
      initGraph()
      ElMessage.success('删除关系成功')
    } else {
      ElMessage.error(result.message || '删除关系失败')
    }
  } catch (error) {
    console.error('Delete relation error:', error)
    ElMessage.error('删除关系失败')
  }
}

function handleNodeClick(node) {
  selectedNode.value = nodes.value.find(n => n.id === node.id)
}

function getNodeRelations(nodeId) {
  return relations.value.filter(r => r.source_id === nodeId || r.target_id === nodeId)
}

function initGraph() {
  if (!graphContainer.value) return
  
  if (graphChart) {
    graphChart.dispose()
  }
  
  graphChart = echarts.init(graphContainer.value)
  
  const nodesData = nodes.value.map(node => ({
    id: node.id.toString(),
    name: node.name,
    symbolSize: 50,
    itemStyle: {
      color: node.type === 'concept' ? '#5470c6' : node.type === 'principle' ? '#91cc75' : '#fac858'
    },
    // 添加节点详细信息，用于tooltip显示
    content: node.content,
    type: node.type
  }))
  
  const linksData = relations.value.map(relation => ({
    source: relation.source_id.toString(),
    target: relation.target_id.toString(),
    label: {
      show: !!relation.label,
      formatter: relation.label || relation.type,
      position: 'middle',
      distance: 10
    }
  }))
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        if (params.dataType === 'node') {
          return `
            <div style="font-weight:bold;margin-bottom:5px">${params.data.name}</div>
            <div>类型: ${params.data.type === 'concept' ? '概念' : params.data.type === 'principle' ? '原理' : '应用'}</div>
            <div style="margin-top:5px">内容:</div>
            <div style="white-space:pre-wrap;word-break:break-all">${params.data.content || '无'}</div>
          `
        } else if (params.dataType === 'edge') {
          return `
            <div style="font-weight:bold">关系</div>
            <div>类型: ${params.data.label || params.data.type}</div>
          `
        }
        return ''
      }
    },
    animationDurationUpdate: 1500,
    animationEasingUpdate: 'quinticInOut',
    series: [
      {
        type: 'graph',
        layout: 'force',
        force: {
          repulsion: 200,
          edgeLength: [100, 200],
          gravity: 0.1
        },
        roam: true,
        label: {
          show: true,
          position: 'right',
          formatter: '{b}'
        },
        data: nodesData,
        links: linksData,
        lineStyle: {
          opacity: 0.9,
          width: 2,
          curveness: 0.1,
          type: 'solid'
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 4
          }
        }
      }
    ]
  }
  
  graphChart.setOption(option)
  
  graphChart.on('click', (params) => {
    if (params.dataType === 'node') {
      const clickedNode = nodes.value.find(n => n.id === params.data.id)
      selectedNode.value = clickedNode
      
      // 实现源节点和目标节点的选择逻辑
      if (!selectedSourceNode.value) {
        selectedSourceNode.value = clickedNode
        ElMessage.info('已选择源节点: ' + clickedNode.name)
      } else if (!selectedTargetNode.value) {
        selectedTargetNode.value = clickedNode
        ElMessage.info('已选择目标节点: ' + clickedNode.name)
      } else {
        // 重置选择
        selectedSourceNode.value = clickedNode
        selectedTargetNode.value = null
        ElMessage.info('已重置选择，当前选择源节点: ' + clickedNode.name)
      }
    }
  })
  
  window.addEventListener('resize', () => {
    graphChart.resize()
  })
}

onMounted(() => {
  loadGraph()
  if (isNew) {
    initGraph()
  }
})
</script>

<style scoped>
.knowledge-graph-editor {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-buttons {
  display: flex;
  gap: 10px;
  align-items: center;
}

.graph-form {
  margin-bottom: 20px;
}

.graph-editor-container {
  display: flex;
  gap: 20px;
  height: 600px;
}

.editor-sidebar {
  width: 300px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
  overflow-y: auto;
}

.sidebar-section {
  margin-bottom: 20px;
}

.sidebar-section h3 {
  margin: 0 0 10px 0;
  font-size: 14px;
  font-weight: 600;
}

.nodes-tree {
  margin-top: 10px;
  max-height: 200px;
  overflow-y: auto;
}

.graph-canvas {
  flex: 1;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.graph-container {
  width: 100%;
  height: 100%;
}

.relation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 0;
}

.dialog-footer {
  text-align: right;
}
</style>