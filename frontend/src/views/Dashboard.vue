<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#409eff"><Document /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.notes || 0 }}</div>
              <div class="stat-label">笔记总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#67c23a"><Grid /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.tables || 0 }}</div>
              <div class="stat-label">表格总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#e6a23c"><EditPen /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.whiteboards || 0 }}</div>
              <div class="stat-label">白板总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#f56c6c"><Connection /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.mindmaps || 0 }}</div>
              <div class="stat-label">脑图总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#909399"><Share /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.flowcharts || 0 }}</div>
              <div class="stat-label">流程图总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快速创建</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/notes/new')" class="quick-action-btn">
              <el-icon><Document /></el-icon>
              新建笔记
            </el-button>
            <el-button type="success" @click="$router.push('/tables/new')" class="quick-action-btn">
              <el-icon><Grid /></el-icon>
              新建表格
            </el-button>
            <el-button type="warning" @click="$router.push('/whiteboards/new')" class="quick-action-btn">
              <el-icon><EditPen /></el-icon>
              新建白板
            </el-button>
            <el-button type="danger" @click="$router.push('/mindmaps/new')" class="quick-action-btn">
              <el-icon><Connection /></el-icon>
              新建脑图
            </el-button>
            <el-button type="info" @click="$router.push('/flowcharts/new')" class="quick-action-btn">
              <el-icon><Share /></el-icon>
              新建流程图
            </el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近更新</span>
            </div>
          </template>
          <el-empty v-if="recentItems.length === 0" description="暂无内容" />
          <el-timeline v-else>
            <el-timeline-item
              v-for="item in recentItems"
              :key="item.id"
              :timestamp="item.updated_at"
              placement="top"
            >
              <el-link :href="getLink(item)" type="primary">{{ item.title }}</el-link>
              <el-tag size="small" style="margin-left: 10px">{{ getTypeLabel(item.type) }}</el-tag>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { noteAPI } from '@/api/note'
import { tableAPI, whiteboardAPI, mindmapAPI, flowchartAPI } from '@/api/editor'

const stats = ref({
  notes: 0,
  tables: 0,
  whiteboards: 0,
  mindmaps: 0,
  flowcharts: 0
})

const recentItems = ref([])

async function loadStats() {
  try {
    const [notes, tables, whiteboards, mindmaps, flowcharts] = await Promise.all([
      noteAPI.getList(),
      tableAPI.getList(),
      whiteboardAPI.getList(),
      mindmapAPI.getList(),
      flowchartAPI.getList()
    ])
    
    stats.value = {
      notes: notes.length,
      tables: tables.length,
      whiteboards: whiteboards.length,
      mindmaps: mindmaps.length,
      flowcharts: flowcharts.length
    }
    
    recentItems.value = [
      ...notes.slice(0, 2).map(n => ({ ...n, type: 'note' })),
      ...tables.slice(0, 2).map(t => ({ ...t, type: 'table' })),
      ...whiteboards.slice(0, 2).map(w => ({ ...w, type: 'whiteboard' })),
      ...mindmaps.slice(0, 2).map(m => ({ ...m, type: 'mindmap' })),
      ...flowcharts.slice(0, 2).map(f => ({ ...f, type: 'flowchart' }))
    ].sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at)).slice(0, 5)
  } catch (error) {
    console.error('Load stats error:', error)
  }
}

function getLink(item) {
  const links = {
    note: `/notes/${item.id}`,
    table: `/tables/${item.id}`,
    whiteboard: `/whiteboards/${item.id}`,
    mindmap: `/mindmaps/${item.id}`,
    flowchart: `/flowcharts/${item.id}`
  }
  return links[item.type] || '#'
}

function getTypeLabel(type) {
  const labels = {
    note: '笔记',
    table: '表格',
    whiteboard: '白板',
    mindmap: '脑图',
    flowchart: '流程图'
  }
  return labels[type] || type
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  font-size: 48px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 5px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.quick-action-btn {
  width: 100%;
  justify-content: flex-start;
  gap: 10px;
}
</style>
