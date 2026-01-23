<template>
  <div class="admin-page">
    <h2 class="page-title">工作台</h2>
    
    <!-- 顶部统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ stats.total_users || 0 }}</div>
            <div class="stat-label">总用户数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ stats.today_new_users || 0 }}</div>
            <div class="stat-label">今日新增用户</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ stats.total_notes || 0 }}</div>
            <div class="stat-label">总笔记数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ stats.total_views || 0 }}</div>
            <div class="stat-label">总访问量</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>笔记类型分布</span>
            </div>
          </template>
          <div class="chart-area">
            <div ref="noteTypeChart" class="chart-container"></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>近期用户增长</span>
            </div>
          </template>
          <div class="chart-area">
            <div ref="userGrowthChart" class="chart-container"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 快速操作 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快速操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="handleUserManage">用户管理</el-button>
            <el-button type="success" @click="handleNoteManage">笔记管理</el-button>
            <el-button type="info" @click="handleExportData">导出数据</el-button>
            <el-button type="warning" @click="loadStats">刷新数据</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, getCurrentInstance, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// 全局挂载的request请求工具
const { proxy } = getCurrentInstance()
const request = proxy.$request

// 初始化统计数据
const stats = ref({
  total_users: 0,
  today_new_users: 0,
  total_notes: 0,
  total_views: 0
})

// 图表引用
const noteTypeChart = ref(null)
const userGrowthChart = ref(null)
const noteTypeChartInstance = ref(null)
const userGrowthChartInstance = ref(null)

// 加载统计数据
async function loadStats() {
  try {
    const res = await request.get('/api/admin/dashboard/stats')
    // 处理后端返回的数据格式
    let statsData = res
    if (res.code === 200 && res.data) {
      statsData = res.data
    }
    console.log('统计数据:', statsData)
    stats.value = {
      total_users: statsData.userCount || 0,
      today_new_users: statsData.todayUsers || 0,
      total_notes: statsData.totalNotes || 0,
      total_views: 0
    }
    
    // 更新笔记类型分布图表
    if (noteTypeChartInstance.value) {
      const noteTypeData = [
        { value: statsData.normalNotes || 0, name: '普通笔记' },
        { value: statsData.totalTables || 0, name: '表格' },
        { value: statsData.totalWhiteboards || 0, name: '白板' },
        { value: statsData.totalMindmaps || 0, name: '脑图' },
        { value: statsData.totalFlowcharts || 0, name: '流程图' }
      ]
      noteTypeChartInstance.value.setOption({
        series: [{
          name: '笔记类型',
          type: 'pie',
          radius: '70%',
          data: noteTypeData,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      })
    }
    
    // 更新用户增长图表
    if (userGrowthChartInstance.value && statsData.recentUserGrowth) {
      userGrowthChartInstance.value.setOption({
        series: [{
          data: statsData.recentUserGrowth
        }]
      })
    }
  } catch (error) {
    console.error('Load stats error:', error)
    ElMessage.error('加载统计数据失败，请重试')
  }
}

// 处理用户管理
function handleUserManage() {
  // 跳转到用户管理页面
  proxy.$router.push('/admin/user-manage')
}

// 处理笔记管理
function handleNoteManage() {
  // 跳转到笔记管理页面
  proxy.$router.push('/notes')
}

// 处理导出数据
function handleExportData() {
  ElMessage.info('导出数据功能开发中')
}

// 初始化笔记类型分布图表
function initNoteTypeChart() {
  if (!noteTypeChart.value) return
  
  noteTypeChartInstance.value = echarts.init(noteTypeChart.value)
  
  const option = {
    title: {
      text: '笔记类型分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '笔记类型',
        type: 'pie',
        radius: '70%',
        data: [
          { value: 0, name: '普通笔记' },
          { value: 0, name: '表格' },
          { value: 0, name: '白板' },
          { value: 0, name: '脑图' },
          { value: 0, name: '流程图' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  
  noteTypeChartInstance.value.setOption(option)
}

// 初始化用户增长图表
function initUserGrowthChart() {
  if (!userGrowthChart.value) return
  
  userGrowthChartInstance.value = echarts.init(userGrowthChart.value)
  
  // 生成最近7天的日期
  const dates = []
  const today = new Date()
  for (let i = 6; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(today.getDate() - i)
    dates.push(`${date.getMonth() + 1}/${date.getDate()}`)
  }
  
  const option = {
    title: {
      text: '近期用户增长',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        data: [0, 0, 0, 0, 0, 0, 0],
        type: 'line',
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {
              offset: 0,
              color: 'rgba(64, 158, 255, 0.5)'
            },
            {
              offset: 1,
              color: 'rgba(64, 158, 255, 0.1)'
            }
          ])
        }
      }
    ]
  }
  
  userGrowthChartInstance.value.setOption(option)
}

// 页面挂载时加载数据
onMounted(async () => {
  // 二次校验：确保只有管理员能访问此页面
  let isAdmin = false
  try {
    // 从localStorage检查，支持多种格式
    const storedIsAdmin = localStorage.getItem('is_admin')
    isAdmin = storedIsAdmin === '1' || storedIsAdmin === 1 || storedIsAdmin === true
    
    // 额外从user对象检查
    const userStr = localStorage.getItem('user')
    if (userStr) {
      const user = JSON.parse(userStr)
      if (user.is_admin === 1 || user.is_admin === true) {
        isAdmin = true
      }
    }
  } catch (e) {
    isAdmin = false
  }
  
  if (!isAdmin) {
    ElMessage.error('无管理员权限，即将返回登录页')
    setTimeout(() => {
      window.location.href = '/login'
    }, 1500)
    return
  }

  // 初始化图表
  await nextTick()
  initNoteTypeChart()
  initUserGrowthChart()
  
  // 加载数据
  await loadStats()
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    noteTypeChartInstance.value?.resize()
    userGrowthChartInstance.value?.resize()
  })
})
</script>

<style scoped>
.admin-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #303133;
}

.stat-card {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-content {
  text-align: center;
  padding: 20px 0;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 500;
}

.chart-area {
  height: 300px;
  background-color: #fafafa;
  border-radius: 4px;
  overflow: hidden;
}

.chart-container {
  width: 100%;
  height: 100%;
}

.chart-placeholder {
  color: #909399;
  font-size: 16px;
}

.quick-actions {
  display: flex;
  gap: 10px;
  padding: 10px 0;
}
</style>