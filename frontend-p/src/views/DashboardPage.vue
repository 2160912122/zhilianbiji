<template>
  <div class="dashboard-container">
    <!-- 数据卡片区域 -->
    <el-row :gutter="20">
      <!-- 总用户数 -->
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <el-icon class="stat-icon"><User /></el-icon>
            <div>
              <p>总用户数</p>
              <h3>{{ userTotal }}</h3>
            </div>
          </div>
        </el-card>
      </el-col>
      <!-- 今日新增用户 -->
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <el-icon class="stat-icon"><UserFilled /></el-icon>
            <div>
              <p>今日新增用户</p>
              <h3>{{ userToday }}</h3>
            </div>
          </div>
        </el-card>
      </el-col>
      <!-- 总笔记数 -->
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <el-icon class="stat-icon"><Document /></el-icon>
            <div>
              <p>总笔记数</p>
              <h3>{{ totalNote }}</h3>
            </div>
          </div>
        </el-card>
      </el-col>
      <!-- 总访问量 -->
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <el-icon class="stat-icon"><Eye /></el-icon>
            <div>
              <p>总访问量</p>
              <h3>0</h3>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>笔记类型分布</span>
          </template>
          <div style="height: 300px;">
            <div class="empty-chart">图表区域</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>近期用户增长</span>
          </template>
          <!-- ECharts容器 -->
          <div ref="userGrowthChart" id="userGrowthChart" style="width:100%;height:300px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作区域 -->
    <el-row style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>快捷操作</span>
          </template>
          <el-button type="primary" :icon="User" @click="goToUser" style="margin-right: 10px;">用户管理</el-button>
          <el-button type="success" :icon="Document" @click="goToNote" style="margin-right: 10px;">笔记管理</el-button>
          <el-button type="warning" :icon="Download" @click="exportData" style="margin-right: 10px;">导出数据</el-button>
          <el-button type="default" :icon="Refresh" @click="loadAllData">刷新数据</el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage, ElLoading } from 'element-plus'
import { useRouter } from 'vue-router'
import axios from 'axios'
import * as echarts from 'echarts'
// 导入图标
import { User, UserFilled, Document, Eye, Download, Refresh } from '@element-plus/icons-vue'
// 导入Excel导出工具（需先安装：npm install xlsx file-saver）
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'

const router = useRouter()
// 数据初始化
const userTotal = ref(0)
const userToday = ref(0)
const totalNote = ref(0)
const userGrowthChart = ref(null)
let chartInstance = null 
let resizeHandler = null 

// 后端地址
const BACKEND_URL = 'http://127.0.0.1:8000'

// 加载数据
const loadAllData = async () => {
  // 清空旧数据
  userTotal.value = 0
  userToday.value = 0
  totalNote.value = 0
  
  try {
    const today = new Date()
    const todayStr = today.toISOString().split('T')[0]
    console.log('===== 请求开始 =====')

    // 1. 总用户数
    const totalRes = await axios.get(`${BACKEND_URL}/user/count`, {
      headers: { 'Content-Type': 'application/json' },
      withCredentials: true
    })
    userTotal.value = totalRes.data?.total || 0

    // 2. 今日新增用户
    const todayRes = await axios.get(`${BACKEND_URL}/user/count`, {
      params: { date: todayStr },
      headers: { 'Content-Type': 'application/json' },
      withCredentials: true
    })
    userToday.value = todayRes.data?.count || 0

    // 3. 总笔记数
    const noteRes = await axios.get(`${BACKEND_URL}/note/count`, {
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      withCredentials: true
    })
    totalNote.value = noteRes.data?.count || 0 

    // 4. 近7天用户增长数据
    const growthRes = await axios.get(`${BACKEND_URL}/user/growth`, {
      headers: { 'Content-Type': 'application/json' },
      withCredentials: true
    })
    const growthData = growthRes.data || []
    
    // 渲染图表
    await nextTick()
    renderUserGrowthChart(growthData)
    ElMessage.success('数据刷新成功')
  } catch (error) {
    console.error('加载数据失败：', error)
    ElMessage.error(`加载数据失败：${error.message}`)
  }
}

// 渲染图表
const renderUserGrowthChart = (data) => {
  if (chartInstance) {
    echarts.dispose(chartInstance)
    chartInstance = null
  }

  if (!data || data.length === 0) {
    console.warn('增长数据为空，不渲染图表')
    return
  }

  const chartDom = userGrowthChart.value || document.getElementById('userGrowthChart')
  if (!chartDom) return

  chartInstance = echarts.init(chartDom)

  const dates = data.map(item => item.date)
  const counts = data.map(item => item.count)

  const option = {
    tooltip: { trigger: 'axis', formatter: '{b}：{c}人' },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { rotate: 45, fontSize: 12 }
    },
    yAxis: { type: 'value', min: 0, interval: 1 },
    series: [
      {
        name: '新增用户',
        type: 'line',
        data: counts,
        smooth: true,
        itemStyle: { color: '#1890ff' },
        lineStyle: { width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
            { offset: 1, color: 'rgba(24, 144, 255, 0)' }
          ])
        },
        symbol: 'circle',
        symbolSize: 8
      }
    ]
  }

  chartInstance.setOption(option, true)

  if (resizeHandler) window.removeEventListener('resize', resizeHandler)
  resizeHandler = () => chartInstance?.resize()
  window.addEventListener('resize', resizeHandler)
}

// 页面挂载
onMounted(async () => {
  await nextTick()
  loadAllData()
})

// 页面卸载
onUnmounted(() => {
  if (resizeHandler) window.removeEventListener('resize', resizeHandler)
  if (chartInstance) echarts.dispose(chartInstance)
})

// 跳转用户管理
const goToUser = () => {
  router.push('/user').catch(err => {
    console.error('跳转失败：', err)
    ElMessage.error('用户管理页面不存在')
  })
}

// 跳转笔记管理
const goToNote = () => {
  router.push('/note').catch(err => {
    console.error('跳转失败：', err)
    ElMessage.error('笔记管理页面不存在')
  })
}

// 完善：导出数据功能（导出为Excel）
const exportData = async () => {
  // 显示加载中
  const loading = ElLoading.service({
    lock: true,
    text: '正在导出数据...',
    background: 'rgba(255, 255, 255, 0.7)'
  })

  try {
    // 1. 构造导出数据（包含统计数据+用户增长数据）
    const today = new Date().toLocaleDateString()
    const statData = [
      ['统计项', '数值'],
      ['总用户数', userTotal.value],
      ['今日新增用户', userToday.value],
      ['总笔记数', totalNote.value],
      ['总访问量', 0],
      ['导出日期', today]
    ]

    // 2. 获取用户增长数据（复用现有接口）
    const growthRes = await axios.get(`${BACKEND_URL}/user/growth`, {
      headers: { 'Content-Type': 'application/json' },
      withCredentials: true
    })
    const growthData = growthRes.data || []
    const growthSheetData = [
      ['日期', '新增用户数'],
      ...growthData.map(item => [item.date, item.count])
    ]

    // 3. 创建Excel工作簿
    const wb = XLSX.utils.book_new()
    // 添加“统计数据”工作表
    const statWs = XLSX.utils.aoa_to_sheet(statData)
    XLSX.utils.book_append_sheet(wb, statWs, '统计数据')
    // 添加“用户增长数据”工作表
    const growthWs = XLSX.utils.aoa_to_sheet(growthSheetData)
    XLSX.utils.book_append_sheet(wb, growthWs, '用户增长数据')

    // 4. 导出Excel文件
    const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
    saveAs(new Blob([wbout], { type: 'application/octet-stream' }), `知行织网-数据统计-${today}.xlsx`)

    ElMessage.success('数据导出成功！')
  } catch (error) {
    console.error('导出失败：', error)
    ElMessage.error(`导出失败：${error.message}`)
  } finally {
    // 关闭加载
    loading.close()
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}
.stat-card {
  height: 120px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  border: none;
}
.stat-item {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 10px;
}
.stat-icon {
  font-size: 36px;
  color: #1890ff;
  margin-right: 15px;
}
.stat-item p {
  color: #666;
  margin: 0;
  font-size: 14px;
}
.stat-item h3 {
  font-size: 24px;
  margin: 5px 0 0 0;
  color: #333;
  font-weight: 600;
}
.chart-card {
  height: 350px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  border: none;
}
.empty-chart {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 16px;
  border: 1px dashed #e6e6e6;
  border-radius: 4px;
}
#userGrowthChart {
  width: 100% !important;
  height: 300px !important;
}
/* 按钮图标垂直居中 */
:deep(.el-button) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
</style>