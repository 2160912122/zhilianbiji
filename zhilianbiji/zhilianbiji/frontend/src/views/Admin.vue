<template>
  <div class="admin-page">
    <!-- 页面标题和装饰 -->
    <div class="page-header">
      <h2 class="page-title">管理控制台</h2>
      <div class="tech-decoration">
        <div class="tech-line"></div>
        <div class="tech-dot"></div>
        <div class="tech-dot"></div>
        <div class="tech-dot"></div>
      </div>
    </div>
    
    <!-- 顶部统计卡片 -->
    <el-row :gutter="24" style="margin-bottom: 24px">
      <el-col :span="6">
        <el-card class="stat-card" hover>
          <div class="stat-content">
            <div class="stat-icon"><el-icon><User /></el-icon></div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_users || 0 }}</div>
              <div class="stat-label">总用户数</div>
              <div class="stat-trend positive">
                <el-icon><CaretTop /></el-icon>
                <span>+{{ (stats.today_new_users || 0) }} 今日</span>
              </div>
            </div>
            <div class="stat-glow"></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" hover>
          <div class="stat-content">
            <div class="stat-icon"><el-icon><UserFilled /></el-icon></div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.today_new_users || 0 }}</div>
              <div class="stat-label">今日新增用户</div>
              <div class="stat-trend positive">
                <el-icon><CaretTop /></el-icon>
                <span>较昨日</span>
              </div>
            </div>
            <div class="stat-glow"></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" hover>
          <div class="stat-content">
            <div class="stat-icon"><el-icon><Document /></el-icon></div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_notes || 0 }}</div>
              <div class="stat-label">总内容数</div>
              <div class="stat-trend positive">
                <el-icon><CaretTop /></el-icon>
                <span>全部类型</span>
              </div>
            </div>
            <div class="stat-glow"></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" hover>
          <div class="stat-content">
            <div class="stat-icon"><el-icon><View /></el-icon></div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_views || 0 }}</div>
              <div class="stat-label">总访问量</div>
              <div class="stat-trend positive">
                <el-icon><CaretTop /></el-icon>
                <span>本月</span>
              </div>
            </div>
            <div class="stat-glow"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 图表区域 -->
    <el-row :gutter="24" style="margin-bottom: 24px">
      <el-col :span="12">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">内容类型分布</span>
              <el-icon class="card-icon"><DataAnalysis /></el-icon>
            </div>
          </template>
          <div class="chart-area">
            <div ref="noteTypeChart" class="chart-container"></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">近期用户增长</span>
              <el-icon class="card-icon"><TrendCharts /></el-icon>
            </div>
          </template>
          <div class="chart-area">
            <div ref="userGrowthChart" class="chart-container"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 快速操作 -->
    <el-row :gutter="24">
      <el-col :span="24">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">管理操作</span>
              <el-icon class="card-icon"><Setting /></el-icon>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="handleUserManage" class="action-btn">
              <el-icon><User /></el-icon>
              <span>用户管理</span>
            </el-button>
            <el-button type="success" @click="handleNoteManage" class="action-btn">
              <el-icon><Document /></el-icon>
              <span>内容管理</span>
            </el-button>
            <el-button type="info" @click="handleExportData" class="action-btn">
              <el-icon><Download /></el-icon>
              <span>导出数据</span>
            </el-button>
            <el-button type="warning" @click="loadStats" class="action-btn">
              <el-icon><Refresh /></el-icon>
              <span>刷新数据</span>
            </el-button>
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
import * as XLSX from 'xlsx'
import {
  User, UserFilled, Document, View, DataAnalysis, TrendCharts, Setting, Download, Refresh, CaretTop
} from '@element-plus/icons-vue'

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
      // 生成最近7天的日期
      const dates = []
      const today = new Date()
      for (let i = 6; i >= 0; i--) {
        const date = new Date(today)
        date.setDate(today.getDate() - i)
        dates.push(`${date.getMonth() + 1}/${date.getDate()}`)
      }
      
      // 使用完整的图表配置，确保所有必要的组件都被定义
      userGrowthChartInstance.value.setOption({
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
          type: 'value',
          minInterval: 1, // 确保纵坐标显示为整数
          axisLabel: {
            formatter: '{value}'
          }
        },
        series: [{
          data: statsData.recentUserGrowth,
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
  // 跳转到内容管理页面
  ElMessage.info('正在跳转到内容管理')
  proxy.$router.push('/admin/note-manage')
}

// 处理导出数据
async function handleExportData() {
  try {
    ElMessage.info('正在导出数据，请稍候...')
    
    // 调用后端导出API
    console.log('开始调用导出API...')
    const res = await request.get('/api/admin/export')
    console.log('导出API返回结果:', res)
    
    if (res.code === 200 && res.data) {
      const exportData = res.data
      console.log('导出数据:', exportData)
      
      try {
        // 使用导入的xlsx库
        console.log('开始使用xlsx库...')
        console.log('xlsx库导入成功')
        
        // 创建工作簿
        console.log('开始创建工作簿...')
        const wb = XLSX.utils.book_new()
        console.log('工作簿创建成功')
        
        // 处理用户数据
        const usersData = exportData.users.data
        const usersSummary = exportData.users.summary
        console.log('用户数据:', usersData)
        console.log('用户统计:', usersSummary)
        
        // 准备用户表格数据
        const usersWorksheetData = [
          ['用户ID', '用户名', '邮箱', '是否管理员', '创建时间', '最后登录时间'],
          ...usersData.map(user => [
            user.id,
            user.username,
            user.email,
            user.is_admin ? '是' : '否',
            user.created_at,
            user.last_login
          ]),
          [], // 空行
          ['统计信息', '', '', '', '', ''],
          ['总用户数', usersSummary.total_users, '', '', '', ''],
          ['今日新增用户', usersSummary.today_users, '', '', '', ''],
          ['近日新增用户（7天）', usersSummary.recent_users, '', '', '', '']
        ]
        
        // 创建用户工作表
        console.log('开始创建用户工作表...')
        const usersWorksheet = XLSX.utils.aoa_to_sheet(usersWorksheetData)
        XLSX.utils.book_append_sheet(wb, usersWorksheet, '用户数据')
        console.log('用户工作表创建成功')
        
        // 处理内容数据
        const contentData = exportData.content.data
        const contentSummary = exportData.content.summary
        console.log('内容数据:', contentData)
        console.log('内容统计:', contentSummary)
        
        // 准备内容表格数据
        const contentWorksheetData = [
          ['内容ID', '标题', '类型', '创建者', '创建时间', '更新时间'],
          ...contentData.map(content => [
            content.id,
            content.title,
            content.type,
            content.creator,
            content.created_at,
            content.updated_at
          ]),
          [], // 空行
          ['统计信息', '', '', '', '', ''],
          ['总内容数', contentSummary.total_content, '', '', '', ''],
          ['笔记数', contentSummary.notes, '', '', '', ''],
          ['表格数', contentSummary.tables, '', '', '', ''],
          ['白板数', contentSummary.whiteboards, '', '', '', ''],
          ['脑图数', contentSummary.mindmaps, '', '', '', ''],
          ['流程图数', contentSummary.flowcharts, '', '', '', '']
        ]
        
        // 创建内容工作表
        console.log('开始创建内容工作表...')
        const contentWorksheet = XLSX.utils.aoa_to_sheet(contentWorksheetData)
        XLSX.utils.book_append_sheet(wb, contentWorksheet, '内容数据')
        console.log('内容工作表创建成功')
        
        // 生成Excel文件并下载
        console.log('开始生成Excel文件...')
        const fileName = `智联笔记管理数据_${new Date().toISOString().slice(0, 10)}.xlsx`
        console.log('文件名:', fileName)
        XLSX.writeFile(wb, fileName)
        console.log('Excel文件生成成功')
        
        ElMessage.success('数据导出成功')
      } catch (excelError) {
        console.error('Excel生成错误:', excelError)
        ElMessage.error('Excel文件生成失败，请重试')
      }
    } else {
      ElMessage.error('导出数据失败，请重试')
    }
  } catch (error) {
    console.error('Export data error:', error)
    ElMessage.error('导出数据失败，请重试')
  }
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
      type: 'value',
      minInterval: 1, // 确保纵坐标显示为整数
      axisLabel: {
        formatter: '{value}'
      }
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

/* 统计卡片样式 */
.stat-card {
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 200px;
  height: auto;
  border-radius: var(--border-radius-lg, 12px);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.stat-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  border-color: #409eff;
}

.stat-content {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  width: 100%;
  min-height: 160px;
  padding: 24px;
  box-sizing: border-box;
  position: relative;
  overflow: hidden;
}

.stat-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #409eff, #667eea);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  background: linear-gradient(135deg, #409eff, #66b1ff);
  color: white;
  box-shadow: 0 4px 15px rgba(64, 158, 255, 0.4);
  position: relative;
  z-index: 1;
}

.stat-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
  z-index: 1;
  min-width: 0;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: var(--text-primary, #303133);
  margin: 0;
  line-height: 1.2;
  background: linear-gradient(135deg, #303133, #606266);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  word-break: break-all;
}

.stat-label {
  font-size: 16px;
  color: var(--text-secondary, #606266);
  margin: 0;
  font-weight: 500;
  word-break: break-all;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 600;
  animation: fadeIn 0.5s ease-in-out;
  word-break: break-all;
}

.stat-trend.positive {
  color: var(--success-color, #67c23a);
}

.stat-trend.negative {
  color: var(--danger-color, #f56c6c);
}

.stat-glow {
  position: absolute;
  top: 0;
  right: 0;
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(64, 158, 255, 0.1) 0%, transparent 70%);
  z-index: 0;
}

/* 仪表盘卡片 */
.dashboard-card {
  border-radius: var(--border-radius-lg, 12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.dashboard-card:hover {
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  border-color: #409eff;
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

.card-icon {
  font-size: 20px;
  color: var(--text-light, #909399);
  transition: all 0.3s ease;
}

.dashboard-card:hover .card-icon {
  color: #409eff;
  transform: rotate(15deg);
}

/* 图表区域 */
.chart-area {
  height: 350px;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: var(--border-radius-md, 8px);
  overflow: hidden;
  position: relative;
}

.chart-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #409eff, #667eea);
}

.chart-container {
  width: 100%;
  height: 100%;
}

/* 快速操作 */
.quick-actions {
  display: flex;
  gap: 16px;
  padding: 20px;
  flex-wrap: wrap;
}

.action-btn {
  flex: 1;
  min-width: 150px;
  height: 60px;
  border-radius: var(--border-radius-lg, 12px);
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary, #303133);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.action-btn:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  border-color: #409eff;
  background: rgba(64, 158, 255, 0.1);
  color: #409eff;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .tech-decoration {
    display: none;
  }
  
  .stat-card {
    height: 160px;
  }
  
  .stat-content {
    padding: 20px;
    gap: 16px;
  }
  
  .stat-icon {
    width: 50px;
    height: 50px;
    font-size: 24px;
  }
  
  .stat-value {
    font-size: 32px;
  }
  
  .chart-area {
    height: 300px;
  }
}

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
  
  .stat-card {
    height: 140px;
  }
  
  .stat-content {
    padding: 16px;
    gap: 12px;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
  
  .stat-value {
    font-size: 28px;
  }
  
  .chart-area {
    height: 250px;
  }
  
  .action-btn {
    min-width: 120px;
    height: 50px;
    font-size: 14px;
  }
}
</style>