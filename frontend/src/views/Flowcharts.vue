<template>
  <div class="flowcharts-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>流程图列表</span>
          <el-button type="primary" @click="$router.push('/flowcharts/new')">
            <el-icon><Plus /></el-icon>
            新建流程图
          </el-button>
        </div>
      </template>
      
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索流程图标题或描述"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <div class="filter-bar">
        <el-select
          v-model="selectedTags"
          multiple
          collapse-tags
          collapse-tags-tooltip
          placeholder="按标签筛选"
          clearable
          @change="handleFilter"
          style="width: 300px;"
        >
          <el-option
            v-for="tag in availableTags"
            :key="tag.id"
            :label="`${tag.name} (${tag.count})`"
            :value="tag.id"
          />
        </el-select>
      </div>
      
      <el-table :data="flowcharts" style="width: 100%">
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="标签" width="200">
          <template #default="{ row }">
            <el-tag
              v-for="tag in row.tags"
              :key="tag.id"
              size="small"
              type="info"
              style="margin-right: 5px;"
            >
              {{ tag.name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_public" label="公开" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_public ? 'success' : 'info'">
              {{ row.is_public ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="editFlowchart(row.id)">编辑</el-button>
            <el-button link type="success" @click="duplicateFlowchart(row.id)">复制</el-button>
            <el-button link type="warning" @click="shareFlowchart(row.id)">分享</el-button>
            <el-button link type="danger" @click="deleteFlowchart(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="shareDialogVisible" title="分享流程图" width="500px">
      <div v-if="shareUrl" class="share-url-container">
        <p>分享链接已生成：</p>
        <el-input v-model="shareUrl" readonly>
          <template #append>
            <el-button @click="copyShareUrl">复制</el-button>
          </template>
        </el-input>
        <p style="margin-top: 10px; color: #666;">该链接有效期为7天</p>
      </div>
      <div v-else>
        <p>确定要分享这个流程图吗？</p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="shareDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmShare" :loading="sharing">确认分享</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()
const flowcharts = ref([])
const searchQuery = ref('')
const selectedTags = ref([])
const shareDialogVisible = ref(false)
const sharing = ref(false)
const shareUrl = ref('')
const currentFlowchartId = ref(null)

let searchTimer = null

async function loadFlowcharts() {
  try {
    const params = {}
    
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    
    if (selectedTags.value.length > 0) {
      params.tag_ids = selectedTags.value.join(',')
    }

    const response = await request.get('/flowcharts', {
      params
    })
    flowcharts.value = response
  } catch (error) {
    console.error('Load flowcharts error:', error)
    ElMessage.error('加载流程图列表失败')
  }
}

function handleSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    loadFlowcharts()
  }, 300)
}

function handleFilter() {
  loadFlowcharts()
}

function editFlowchart(id) {
  router.push(`/flowcharts/${id}`)
}

async function duplicateFlowchart(id) {
  try {
    await request.post(`/flowcharts/${id}/duplicate`, {})

    ElMessage.success('复制成功')
    loadFlowcharts()
  } catch (error) {
    console.error('Duplicate flowchart error:', error)
    ElMessage.error('复制失败')
  }
}

async function shareFlowchart(id) {
  currentFlowchartId.value = id
  shareDialogVisible.value = true
  shareUrl.value = ''
}

async function confirmShare() {
  if (!currentFlowchartId.value) return

  sharing.value = true
  try {
    const response = await request.post(`/flowcharts/${currentFlowchartId.value}/share`, {
      days: 7
    })

    shareUrl.value = `${window.location.origin}${response.share_url}`
    ElMessage.success('分享链接已生成')
  } catch (error) {
    console.error('分享失败:', error)
    ElMessage.error('分享失败')
  } finally {
    sharing.value = false
  }
}

function copyShareUrl() {
  navigator.clipboard.writeText(shareUrl.value)
  ElMessage.success('链接已复制到剪贴板')
}

async function deleteFlowchart(id) {
  try {
    await ElMessageBox.confirm('确定要删除这个流程图吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await request.delete(`/flowcharts/${id}`)

    ElMessage.success('删除成功')
    loadFlowcharts()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete flowchart error:', error)
      ElMessage.error('删除失败')
    }
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

const availableTags = computed(() => {
  const tagMap = new Map()

  flowcharts.value.forEach(flowchart => {
    if (flowchart.tags && flowchart.tags.length > 0) {
      flowchart.tags.forEach(tag => {
        if (tagMap.has(tag.id)) {
          tagMap.get(tag.id).count++
        } else {
          tagMap.set(tag.id, {
            id: tag.id,
            name: tag.name,
            count: 1
          })
        }
      })
    }
  })

  return Array.from(tagMap.values()).sort((a, b) => b.count - a.count)
})

onMounted(() => {
  loadFlowcharts()
})
</script>

<style scoped>
.flowcharts-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-bar {
  margin-bottom: 20px;
}

.filter-bar {
  margin-bottom: 20px;
}

.share-url-container p {
  margin: 10px 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
