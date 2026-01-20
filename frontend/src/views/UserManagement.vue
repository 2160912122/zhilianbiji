<template>
  <div class="user-container">
    <el-card class="user-card">
      <h2 class="user-title">用户管理</h2>
      
      <!-- 多条件搜索表单 -->
      <el-form :model="searchForm" inline style="margin-bottom: 20px;">
        <el-form-item label="用户名">
          <el-input v-model="searchForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="注册时间">
          <el-date-picker 
            v-model="searchForm.registerTime" 
            type="daterange" 
            range-separator="至" 
            start-placeholder="开始日期" 
            end-placeholder="结束日期"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态">
            <el-option label="启用" value="1"></el-option>
            <el-option label="禁用" value="0"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearchForm">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 用户列表（修复标签闭合问题） -->
      <el-table :data="userList" border stripe>
        <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>
        <el-table-column prop="username" label="用户名" width="150" align="center"></el-table-column>
        <el-table-column prop="register_time" label="注册时间" width="200" align="center">
          <template #default="scope">
            {{ scope.row.register_time ? new Date(scope.row.register_time).toLocaleString() : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="scope">
            <span style="margin-right: 8px;">
              {{ scope.row.status === '1' ? '启用' : '禁用' }}
            </span>
            <el-switch
              v-model="scope.row.status"
              active-value="1"
              inactive-value="0"
              @change="handleStatusChange(scope.row)"
            ></el-switch>
          </template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="80" align="center">
          <template #default="scope">
            {{ scope.row.role === '1' ? '普通用户' : '管理员' }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import service from '@/utils/request'

// 用户列表
const userList = ref([])

// 搜索表单
const searchForm = reactive({
  username: '',
  registerTime: [],
  status: ''
})

// 页面挂载时加载全部用户
onMounted(() => {
  loadUserList()
})

// 加载用户列表
const loadUserList = async () => {
  try {
    const params = {}
    if (searchForm.username) params.username = searchForm.username
    if (searchForm.status) params.status = Number(searchForm.status)
    if (searchForm.registerTime.length === 2) {
      params.startTime = searchForm.registerTime[0].format('YYYY-MM-DD')
      params.endTime = searchForm.registerTime[1].format('YYYY-MM-DD')
    }

    const res = await service.get('/user/list', { params })
    userList.value = res.data || res
  } catch (error) {
    console.error('加载用户列表失败：', error)
    ElMessage.error('加载用户列表失败！')
  }
}

// 搜索
const handleSearch = () => {
  loadUserList()
}

// 重置搜索表单
const resetSearchForm = () => {
  searchForm.username = ''
  searchForm.registerTime = []
  searchForm.status = ''
  loadUserList()
}

// 修改用户状态
const handleStatusChange = async (user) => {
  try {
    await service.put(`/user/update-status/${user.id}`, { status: user.status })
    ElMessage.success('状态修改成功！')
  } catch (error) {
    console.error('修改状态失败：', error)
    ElMessage.error('修改状态失败！')
    user.status = user.status === '1' ? '0' : '1'
  }
}
</script>

<style scoped>
.user-container {
  padding: 20px;
}
.user-card {
  padding: 20px;
}
.user-title {
  margin: 0 0 20px 0;
  color: #1989fa;
  font-size: 18px;
}
</style>