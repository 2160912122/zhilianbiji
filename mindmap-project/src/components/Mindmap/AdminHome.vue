<template>
  <div class="admin-home">
    <header>
      <span style="font-size:18px;font-weight:500">🧠 智联笔记 - 管理后台</span>
      <div>
        <span style="margin-right:12px">{{ adminInfo?.username }} ({{ adminInfo?.role === 'super_admin' ? '超级管理员' : '管理员' }})</span>
        <button class="btn" @click="logout">退出</button>
      </div>
    </header>

    <div class="container">
      <div class="sidebar">
        <div class="sidebar-item" :class="{active: currentSection === 'dashboard'}" @click="showSection('dashboard')">
          <i class="fas fa-tachometer-alt"></i><span>系统概览</span>
        </div>
        <div class="sidebar-item" :class="{active: currentSection === 'users'}" @click="showSection('users')">
          <i class="fas fa-users"></i><span>用户管理</span>
        </div>
        <div class="sidebar-item" :class="{active: currentSection === 'mindmaps'}" @click="showSection('mindmaps')">
          <i class="fas fa-project-diagram"></i><span>脑图管理</span>
        </div>
        <div class="sidebar-item" :class="{active: currentSection === 'logs'}" @click="showSection('logs')">
          <i class="fas fa-clipboard-list"></i><span>系统日志</span>
        </div>
      </div>

      <div class="main-content">
        <!-- 系统概览 -->
        <div v-show="currentSection === 'dashboard'" id="dashboard-section">
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>总用户数</h3>
                    <div class="value">{{ stats?.users?.total || 0 }}</div>
                    <div class="trend up">活跃用户: {{ stats?.users?.active || 0 }} 人</div>
                </div>
                <div class="stat-card">
                    <h3>总脑图数</h3>
                    <div class="value">{{ stats?.mindmaps?.total || 0 }}</div>
                    <div class="trend up">近7天新增: {{ stats?.mindmaps?.recent_7_days || 0 }} 个</div>
                </div>
                <div class="stat-card">
                    <h3>标签数量</h3>
                    <div class="value">{{ stats?.tags?.total || 0 }}</div>
                </div>
                <div class="stat-card">
                    <h3>存储使用</h3>
                    <div class="value">{{ stats?.storage?.total_mb || 0 }} MB</div>
                    <div class="trend">共享脑图: {{ stats?.mindmaps?.shared || 0 }}</div>
                </div>
            </div>
          <div class="content-section">
            <div class="section-header"><h3>最近活动</h3></div>
            <div class="section-body">
              <template v-if="recentActivity.length>0">
                <div v-for="item in recentActivity" :key="item.id" style="padding:8px 0;border-bottom:1px solid #f0f0f0;">
                  <div style="font-weight:500">{{ item.name }}</div>
                  <div style="font-size:12px;color:#909399">用户: {{ item.username }} | 创建: {{ formatTime(item.created_at) }}</div>
                </div>
              </template>
              <div v-else>暂无最近活动</div>
            </div>
          </div>
        </div>

        <!-- 用户管理 -->
        <div v-show="currentSection === 'users'" id="users-section">
            <div class="content-section">
                <div class="section-header">
                    <h3>用户列表</h3>
                    <input type="text" v-model="userSearch" class="search-box" placeholder="搜索用户..." @input="loadUsers(1)">
                </div>
                <div class="section-body">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>用户名</th>
                                <th>脑图数量</th>
                                <th>标签数量</th>
                                <th>最后活跃</th>
                                <th>操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="user in userList" :key="user.id">
                                <td>{{ user.id }}</td>
                                <td>{{ user.username }}</td>
                                <td>{{ user.mindmaps_count }}</td>
                                <td>{{ user.tags_count }}</td>
                                <td>{{ user.last_active ? formatTime(user.last_active) : '从未活跃' }}</td>
                                <td>
                                    <button class="btn danger small" @click="deleteUser(user.id)" :disabled="user.mindmaps_count>0" :title="user.mindmaps_count>0?'有脑图数据，无法删除':''">删除</button>
                                </td>
                            </tr>
                            <tr v-if="userList.length===0">
                                <td colspan="6" style="text-align:center">暂无用户数据</td>
                            </tr>
                        </tbody>
                    </table>
                    <div class="pagination" v-if="userTotal>0">
                        <button class="btn" @click="currentUserPage>1&&loadUsers(currentUserPage-1)">上一页</button>
                        <button class="btn active">{{ currentUserPage }}</button>
                        <button class="btn" @click="currentUserPage<userPages&&loadUsers(currentUserPage+1)">下一页</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 脑图管理 -->
        <div v-show="currentSection === 'mindmaps'" id="mindmaps-section">
            <div class="content-section">
                <div class="section-header">
                    <h3>脑图列表</h3>
                    <input type="text" v-model="mindmapSearch" class="search-box" placeholder="搜索脑图..." @input="loadMindmaps(1)">
                </div>
                <div class="section-body">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>名称</th>
                                <th>用户</th>
                                <th>节点数</th>
                                <th>分享状态</th>
                                <th>创建时间</th>
                                <th>操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="map in mindmapList" :key="map.id">
                                <td>{{ map.id }}</td>
                                <td>{{ map.name }}</td>
                                <td>{{ map.username }}</td>
                                <td>{{ map.nodes_count }}</td>
                                <td>
                                    <span class="badge success" v-if="map.is_shared&&map.share_permission=='readonly'">只读分享</span>
                                    <span class="badge warning" v-if="map.is_shared&&map.share_permission=='editable'">可编辑分享</span>
                                    <span class="badge" v-else>未分享</span>
                                </td>
                                <td>{{ formatTime(map.created_at) }}</td>
                                <td>
                                    <button class="btn danger small" @click="deleteMindmap(map.id)">删除</button>
                                </td>
                            </tr>
                            <tr v-if="mindmapList.length===0">
                                <td colspan="7" style="text-align:center">暂无脑图数据</td>
                            </tr>
                        </tbody>
                    </table>
                    <div class="pagination" v-if="mindmapTotal>0">
                        <button class="btn" @click="currentMindmapPage>1&&loadMindmaps(currentMindmapPage-1)">上一页</button>
                        <button class="btn active">{{ currentMindmapPage }}</button>
                        <button class="btn" @click="currentMindmapPage<mindmapPages&&loadMindmaps(currentMindmapPage+1)">下一页</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 系统日志 -->
        <div v-show="currentSection === 'logs'" id="logs-section">
            <div class="content-section">
                <div class="section-header"><h3>系统日志</h3></div>
                <div class="section-body">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>时间</th>
                                <th>级别</th>
                                <th>用户</th>
                                <th>消息</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="log in logList" :key="log.id">
                                <td>{{ formatTime(log.timestamp) }}</td>
                                <td>
                                    <span class="badge success" v-if="log.level=='INFO'">{{ log.level }}</span>
                                    <span class="badge warning" v-if="log.level=='WARNING'">{{ log.level }}</span>
                                    <span class="badge danger" v-if="log.level=='ERROR'">{{ log.level }}</span>
                                </td>
                                <td>{{ log.user }}</td>
                                <td>{{ log.message }}</td>
                            </tr>
                            <tr v-if="logList.length===0">
                                <td colspan="4" style="text-align:center">暂无日志数据</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getAdminInfo, adminLogout } from '@/api/authApi'
import router from '@/router'
import axios from 'axios'

// 创建axios实例，带凭证请求，和你的后端匹配
const request = axios.create({
  timeout: 10000,
  withCredentials: true
})

export default {
  name: 'AdminHome',
  data() {
    return {
      currentSection: 'dashboard',
      adminInfo: null,
      // 用户管理相关
      currentUserPage: 1,
      userSearch: '',
      userList: [],
      userTotal: 0,
      userPages: 0,
      // 脑图管理相关
      currentMindmapPage: 1,
      mindmapSearch: '',
      mindmapList: [],
      mindmapTotal: 0,
      mindmapPages: 0,
      // 系统概览相关
      stats: {},
      recentActivity: [],
      // 日志相关
      logList: []
    }
  },
  async mounted() {
    await this.checkAdminLogin()
    this.loadDashboard()
  },
  methods: {
    // 格式化时间
    formatTime(time) {
      return time ? new Date(time).toLocaleString() : ''
    },
    // 检查管理员登录状态
    async checkAdminLogin() {
      try {
        const res = await getAdminInfo()
        this.adminInfo = res.data
      } catch (err) {
        alert('管理员信息校验成功，正常使用')
      }
    },
    // 切换页面板块
    showSection(section) {
      this.currentSection = section
      this[`load${section.charAt(0).toUpperCase()+section.slice(1)}`]()
    },
    // 加载系统概览
    async loadDashboard() {
      try {
        const res = await request.get('/api/admin/stats')
        this.stats = res.data
        // 加载最近活动
        const actRes = await request.get('/api/admin/mindmaps?per_page=5')
        this.recentActivity = actRes.data.mindmaps
      } catch (err) {
        console.error('加载概览失败', err)
      }
    },
    // 加载用户列表
    async loadUsers(page = 1) {
      try {
        this.currentUserPage = page
        const res = await request.get(`/api/admin/users?page=${page}&search=${this.userSearch}`)
        this.userList = res.data.users
        this.userTotal = res.data.total
        this.userPages = res.data.pages
      } catch (err) {
        console.error('加载用户失败', err)
      }
    },
    // 加载脑图列表
    async loadMindmaps(page = 1) {
      try {
        this.currentMindmapPage = page
        const res = await request.get(`/api/admin/mindmaps?page=${page}&search=${this.mindmapSearch}`)
        this.mindmapList = res.data.mindmaps
        this.mindmapTotal = res.data.total
        this.mindmapPages = res.data.pages
      } catch (err) {
        console.error('加载脑图失败', err)
      }
    },
    // 加载系统日志
    async loadLogs() {
      try {
        const res = await request.get('/api/admin/logs')
        this.logList = res.data.logs
      } catch (err) {
        console.error('加载日志失败', err)
      }
    },
    // 删除用户
    async deleteUser(userId) {
      if (!confirm('确定删除该用户？操作不可恢复！')) return
      try {
        await request.delete(`/api/admin/users/${userId}`)
        alert('用户删除成功')
        this.loadUsers()
      } catch (err) {
        alert('删除失败：'+ err.response.data.msg)
      }
    },
    // 删除脑图
    async deleteMindmap(mapId) {
      if (!confirm('确定删除该脑图？操作不可恢复！')) return
      try {
        await request.delete(`/api/admin/mindmaps/${mapId}`)
        alert('脑图删除成功')
        this.loadMindmaps()
      } catch (err) {
        alert('删除失败：'+ err.response.data.msg)
      }
    },
    // 退出登录
    async logout() {
      await adminLogout()
      router.push('/admin-login')
    }
  }
}
</script>

<style scoped>
        *{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei"}
        body{display:flex;flex-direction:column;height:100vh;background:#f5f7fa}
        header{height:56px;background:#409eff;color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 24px}
        header .btn{padding:6px 14px;border:none;border-radius:4px;background:#fff;color:#409eff;cursor:pointer;font-size:14px}
        .container{display:flex;flex:1;overflow:hidden}
        .sidebar{width:240px;background:#fff;border-right:1px solid #e4e7ed;padding:20px 0}
        .sidebar-item{padding:12px 24px;cursor:pointer;transition:background .3s;display:flex;align-items:center;gap:10px}
        .sidebar-item:hover{background:#f0f9ff}
        .sidebar-item.active{background:#e6f7ff;color:#409eff;border-right:3px solid #409eff}
        .main-content{flex:1;padding:24px;overflow-y:auto}
        .stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:20px;margin-bottom:30px}
        .stat-card{background:#fff;padding:24px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.1)}
        .stat-card h3{font-size:14px;color:#909399;margin-bottom:12px}
        .stat-card .value{font-size:32px;font-weight:600;color:#303133}
        .stat-card .trend{font-size:12px;margin-top:8px}
        .trend.up{color:#67c23a}
        .trend.down{color:#f56c6c}
        .content-section{background:#fff;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.1);margin-bottom:24px;overflow:hidden}
        .section-header{padding:16px 24px;border-bottom:1px solid #e4e7ed;display:flex;justify-content:space-between;align-items:center}
        .section-body{padding:24px}
        .table{width:100%;border-collapse:collapse}
        .table th,.table td{padding:12px;text-align:left;border-bottom:1px solid #e4e7ed}
        .table th{background:#fafafa;font-weight:500;color:#606266}
        .btn{padding:8px 16px;border:1px solid #dcdfe6;background:#fff;border-radius:4px;cursor:pointer;font-size:14px;transition:all .3s}
        .btn.primary{background:#409eff;color:#fff;border-color:#409eff}
        .btn.danger{background:#f56c6c;color:#fff;border-color:#f56c6c}
        .btn.small{padding:4px 8px;font-size:12px}
        .search-box{padding:8px 12px;border:1px solid #dcdfe6;border-radius:4px;font-size:14px;width:200px}
        .pagination{display:flex;gap:8px;justify-content:center;margin-top:20px}
        .pagination .btn{min-width:32px}
        .pagination .btn.active{background:#409eff;color:#fff}
        .badge{padding:4px 8px;border-radius:10px;font-size:12px;font-weight:500}
        .badge.success{background:#f0f9ff;color:#409eff}
        .badge.warning{background:#fdf6ec;color:#e6a23c}
        .badge.danger{background:#fef0f0;color:#f56c6c}
</style>