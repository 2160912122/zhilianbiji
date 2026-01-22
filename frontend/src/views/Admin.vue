<template>
  <div class="admin-page">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#409eff"><User /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_users || 0 }}</div>
              <div class="stat-label">总用户数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#67c23a"><Document /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_documents || 0 }}</div>
              <div class="stat-label">总文档数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#e6a23c"><FolderOpened /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_categories || 0 }}</div>
              <div class="stat-label">总分类数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#f56c6c"><PriceTag /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_tags || 0 }}</div>
              <div class="stat-label">总标签数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#409eff"><Document /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_notes || 0 }}</div>
              <div class="stat-label">笔记</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#67c23a"><Connection /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_mindmaps || 0 }}</div>
              <div class="stat-label">脑图</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#e6a23c"><Share /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_flowcharts || 0 }}</div>
              <div class="stat-label">流程图</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#f56c6c"><Grid /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_tables || 0 }}</div>
              <div class="stat-label">表格</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#909399"><EditPen /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_whiteboards || 0 }}</div>
              <div class="stat-label">白板</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#409eff"><Share /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_shares || 0 }}</div>
              <div class="stat-label">分享数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>用户管理</span>
            </div>
          </template>
          
          <el-table :data="users" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="username" label="用户名" min-width="150" />
            <el-table-column prop="email" label="邮箱" min-width="200" />
            <el-table-column prop="is_admin" label="管理员" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_admin ? 'success' : 'info'">
                  {{ row.is_admin ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="note_count" label="笔记数" width="100" />
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button
                  link
                  type="primary"
                  @click="toggleAdmin(row)"
                  :disabled="row.id === 1"
                >
                  {{ row.is_admin ? '取消管理员' : '设为管理员' }}
                </el-button>
                <el-button
                  link
                  type="danger"
                  @click="deleteUser(row.id)"
                  :disabled="row.is_admin"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/api/ai'
import { ElMessage, ElMessageBox } from 'element-plus'

const stats = ref({
  total_users: 0,
  total_notes: 0,
  total_categories: 0,
  total_tags: 0
})

const users = ref([])

async function loadStats() {
  try {
    stats.value = await adminAPI.getStats()
  } catch (error) {
    console.error('Load stats error:', error)
  }
}

async function loadUsers() {
  try {
    users.value = await adminAPI.getUsers()
  } catch (error) {
    console.error('Load users error:', error)
  }
}

async function toggleAdmin(user) {
  try {
    const action = user.is_admin ? '取消管理员' : '设为管理员'
    await ElMessageBox.confirm(`确定要${action}这个用户吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await adminAPI.setAdmin(user.id)
    ElMessage.success('设置成功')
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Toggle admin error:', error)
      ElMessage.error('设置失败')
    }
  }
}

async function deleteUser(userId) {
  try {
    await ElMessageBox.confirm('确定要删除这个用户吗？此操作不可恢复。', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await adminAPI.deleteUser(userId)
    ElMessage.success('删除成功')
    loadUsers()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete user error:', error)
      ElMessage.error('删除失败')
    }
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadStats()
  loadUsers()
})
</script>

<style scoped>
.admin-page {
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
</style>
