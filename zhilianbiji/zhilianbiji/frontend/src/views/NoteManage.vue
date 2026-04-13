<template>
  <div class="note-manage-page">
    <!-- 页面标题和装饰 -->
    <div class="page-header">
      <h2 class="page-title">内容管理</h2>
      <div class="tech-decoration">
        <div class="tech-line"></div>
        <div class="tech-dot"></div>
        <div class="tech-dot"></div>
        <div class="tech-dot"></div>
      </div>
    </div>
    
    <!-- 搜索和筛选 -->
    <div class="search-filter">
      <el-input
        v-model="searchQuery"
        placeholder="搜索内容"
        clearable
        class="search-input"
        @keyup.enter="loadContent"
      >
        <template #prefix>
          <el-icon class="el-input__icon"><Search /></el-icon>
        </template>
      </el-input>
      <el-select
        v-model="contentType"
        placeholder="内容类型"
        class="filter-select"
        @change="loadContent"
      >
        <el-option label="全部" value="all"></el-option>
        <el-option label="笔记" value="notes"></el-option>
        <el-option label="表格" value="tables"></el-option>
        <el-option label="白板" value="whiteboards"></el-option>
        <el-option label="脑图" value="mindmaps"></el-option>
        <el-option label="流程图" value="flowcharts"></el-option>
      </el-select>
      <el-select
        v-model="sortBy"
        placeholder="排序方式"
        class="filter-select"
        @change="loadContent"
      >
        <el-option label="创建时间" value="created_at"></el-option>
        <el-option label="更新时间" value="updated_at"></el-option>
        <el-option label="标题" value="title"></el-option>
      </el-select>
      <el-button type="primary" @click="loadContent" class="refresh-btn">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>
    
    <!-- 内容列表 -->
    <el-card class="content-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">内容列表</span>
          <el-badge :value="totalContent" type="primary" class="content-count"></el-badge>
        </div>
      </template>
      <div class="content-list">
        <el-table
          :data="contentList"
          style="width: 100%"
          stripe
          border
        >
          <el-table-column prop="id" label="ID" width="80"></el-table-column>
          <el-table-column prop="title" label="标题" min-width="200">
            <template #default="scope">
              <span class="content-title">{{ scope.row.title }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="type" label="类型" width="100">
            <template #default="scope">
              <el-tag :type="getTypeTagType(scope.row.type)">{{ scope.row.type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="creator" label="创建者" width="100"></el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180"></el-table-column>
          <el-table-column prop="updated_at" label="更新时间" width="180"></el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="scope">
              <div class="action-buttons">
                <el-button 
                  size="small" 
                  type="primary" 
                  :icon="View" 
                  @click="viewContent(scope.row)"
                  class="action-btn view-btn"
                >
                  查看
                </el-button>
                <el-button 
                  size="small" 
                  type="danger" 
                  :icon="Delete" 
                  @click="deleteContent(scope.row)"
                  class="action-btn delete-btn"
                >
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalContent"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, getCurrentInstance } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, View, Delete } from '@element-plus/icons-vue'

// 全局挂载的request请求工具
const { proxy } = getCurrentInstance()
const request = proxy.$request

// 搜索和筛选参数
const searchQuery = ref('')
const contentType = ref('all')
const sortBy = ref('created_at')

// 分页参数
const currentPage = ref(1)
const pageSize = ref(10)
const totalContent = ref(0)

// 内容列表
const contentList = ref([])

// 加载内容数据
async function loadContent() {
  try {
    const res = await request.get('/api/admin/content', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
        search: searchQuery.value,
        type: contentType.value,
        sort_by: sortBy.value
      }
    })
    
    if (res.code === 200 && res.data) {
      contentList.value = res.data.items || []
      totalContent.value = res.data.total || 0
    }
  } catch (error) {
    console.error('Load content error:', error)
    ElMessage.error('加载内容数据失败，请重试')
  }
}

// 处理分页大小变化
function handleSizeChange(size) {
  pageSize.value = size
  loadContent()
}

// 处理页码变化
function handleCurrentChange(page) {
  currentPage.value = page
  loadContent()
}

// 获取类型标签样式
function getTypeTagType(type) {
  const typeMap = {
    '笔记': 'primary',
    '表格': 'success',
    '白板': 'info',
    '脑图': 'warning',
    '流程图': 'danger'
  }
  return typeMap[type] || 'default'
}

// 查看内容
function viewContent(content) {
  // 根据内容类型跳转到相应的编辑页面
  let route = ''
  switch (content.type) {
    case '笔记':
      route = `/notes/${content.id}`
      break
    case '表格':
      route = `/tables/${content.id}`
      break
    case '白板':
      route = `/whiteboards/${content.id}`
      break
    case '脑图':
      route = `/mindmaps/${content.id}`
      break
    case '流程图':
      route = `/flowcharts/${content.id}`
      break
    default:
      ElMessage.warning('未知内容类型')
      return
  }
  proxy.$router.push(route)
}

// 删除内容
function deleteContent(content) {
  ElMessageBox.confirm(
    `确定要删除内容 "${content.title}" 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const res = await request.delete(`/api/admin/content/${content.id}`)
      if (res.code === 200) {
        ElMessage.success('删除成功')
        loadContent()
      }
    } catch (error) {
      console.error('Delete content error:', error)
      ElMessage.error('删除失败，请重试')
    }
  }).catch(() => {
    // 取消删除
  })
}

// 页面挂载时加载数据
onMounted(() => {
  loadContent()
})
</script>

<style scoped>
.note-manage-page {
  padding: 20px;
  background-color: var(--background-color, #f0f2f5);
  min-height: 100vh;
}

/* 页面标题和装饰 */
.page-header {
  margin-bottom: 24px;
  padding: 30px;
  background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
  border-radius: var(--border-radius-lg, 12px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  color: white;
  position: relative;
  overflow: hidden;
}

.page-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(64, 158, 255, 0.1), rgba(102, 126, 234, 0.1));
  z-index: 1;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 12px 0;
  color: white;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  position: relative;
  z-index: 2;
}

/* 科技感装饰元素 */
.tech-decoration {
  position: absolute;
  bottom: 20px;
  right: 40px;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.tech-line {
  width: 100px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #409eff);
}

.tech-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #409eff;
  box-shadow: 0 0 10px #409eff;
  animation: pulse 2s infinite;
}

.tech-dot:nth-child(2) {
  animation-delay: 0.3s;
}

.tech-dot:nth-child(3) {
  animation-delay: 0.6s;
}

.tech-dot:nth-child(4) {
  animation-delay: 0.9s;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}

/* 搜索和筛选 */
.search-filter {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 300px;
}

.filter-select {
  width: 150px;
}

.refresh-btn {
  white-space: nowrap;
}

/* 内容卡片 */
.content-card {
  border-radius: var(--border-radius-lg, 12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 64px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.5);
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #303133);
  background: linear-gradient(135deg, #303133, #606266);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.content-count {
  margin-left: 10px;
}

/* 内容列表 */
.content-list {
  margin-bottom: 20px;
}

.content-title {
  font-weight: 500;
  color: var(--text-primary, #303133);
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

/* 操作按钮样式 */
.action-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: flex-start;
  padding: 4px 0;
}

.action-btn {
  border-radius: var(--border-radius-md, 8px);
  transition: all 0.3s ease;
  font-size: 12px;
  height: 32px;
  line-height: 32px;
  padding: 0 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  min-width: 60px;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.view-btn {
  background: linear-gradient(135deg, #409eff, #66b1ff);
  border: none;
  color: white;
}

.view-btn:hover {
  background: linear-gradient(135deg, #66b1ff, #91caff);
  color: white;
}

.delete-btn {
  background: linear-gradient(135deg, #f56c6c, #f78989);
  border: none;
  color: white;
}

.delete-btn:hover {
  background: linear-gradient(135deg, #f78989, #fab6b6);
  color: white;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    padding: 20px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .tech-decoration {
    display: none;
  }
  
  .search-filter {
    flex-direction: column;
  }
  
  .search-input {
    width: 100%;
  }
  
  .filter-select {
    width: 100%;
  }
  
  .refresh-btn {
    width: 100%;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: stretch;
  }
  
  .action-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>