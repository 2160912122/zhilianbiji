<template>
  <div class="user-manage-page">
    <h2 class="page-title">用户管理</h2>
    
    <!-- 搜索和筛选 -->
    <el-card style="margin-bottom: 20px">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-input v-model="searchUsername" placeholder="搜索用户名" clearable>
            <template #append>
              <el-button @click="handleSearch"><el-icon><Search /></el-icon></el-button>
            </template>
          </el-input>
        </el-col>
        <el-col :span="8">
          <el-input v-model="searchEmail" placeholder="搜索邮箱" clearable>
            <template #append>
              <el-button @click="handleSearch"><el-icon><Search /></el-icon></el-button>
            </template>
          </el-input>
        </el-col>
        <el-col :span="8">
          <el-select v-model="searchStatus" placeholder="用户状态" clearable>
            <el-option label="启用" value="1"></el-option>
            <el-option label="禁用" value="0"></el-option>
          </el-select>
        </el-col>
      </el-row>
      <el-row :gutter="20" style="margin-top: 10px">
        <el-col :span="24" style="text-align: right">
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button type="info" @click="resetFilters">重置筛选</el-button>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 用户列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户列表</span>
          <el-button type="success" @click="handleAddUser">新增用户</el-button>
        </div>
      </template>
      <el-table :data="users" style="width: 100%">
        <el-table-column prop="id" label="用户ID" width="80" />
        <el-table-column prop="username" label="用户名" width="180" />
        <el-table-column prop="email" label="邮箱" width="250" />
        <el-table-column prop="is_admin" label="用户状态" width="120">
          <template #default="{ row }">
            <el-tag :type="(row.is_admin === true || row.is_admin === 1) ? 'success' : 'danger'">
              {{ (row.is_admin === true || row.is_admin === 1) ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="200" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handleEditUser(row)">编辑</el-button>
            <el-button 
              size="small" 
              :type="(row.is_admin === true || row.is_admin === 1) ? 'warning' : 'success'"
              @click="handleToggleStatus(row)"
            >
              {{ (row.is_admin === true || row.is_admin === 1) ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination" style="margin-top: 20px">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 用户编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
    >
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="formData.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码" v-if="!formData.id">
          <el-input v-model="formData.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="用户类型" prop="is_admin">
          <el-select v-model="formData.is_admin" placeholder="请选择用户类型">
            <el-option label="普通用户" value="0"></el-option>
            <el-option label="管理员" value="1"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveUser">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, getCurrentInstance } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

// 全局挂载的request请求工具
const { proxy } = getCurrentInstance()
const request = proxy.$request

// 表格数据
const users = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// 搜索和筛选
const searchUsername = ref('')
const searchEmail = ref('')
const searchStatus = ref('')

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('新增用户')
const formData = ref({})
const formRef = ref(null)

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3-20之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  is_admin: [
    { required: true, message: '请选择用户类型', trigger: 'change' }
  ]
}

// 加载用户列表
async function loadUsers() {
  try {
    const res = await request.get('/api/admin/users')
    
    // 处理后端返回的数据格式
    let filteredUsers = []
    if (Array.isArray(res)) {
      filteredUsers = res
    } else if (res.code === 200 && Array.isArray(res.data)) {
      filteredUsers = res.data
    }
    
    // 调试：查看用户数据
    console.log('用户数据:', filteredUsers)
    
    // 处理搜索和筛选
    if (searchUsername.value) {
      const username = searchUsername.value.toLowerCase()
      filteredUsers = filteredUsers.filter(user => 
        user.username.toLowerCase().includes(username)
      )
    }
    if (searchEmail.value) {
      const email = searchEmail.value.toLowerCase()
      filteredUsers = filteredUsers.filter(user => 
        user.email.toLowerCase().includes(email)
      )
    }
    if (searchStatus.value) {
      // 这里暂时使用is_admin作为状态，后续可根据实际状态字段修改
      const status = parseInt(searchStatus.value)
      filteredUsers = filteredUsers.filter(user => 
        (user.is_admin === true || user.is_admin === 1) ? 1 : 0 === status
      )
    }
    
    // 处理分页
    total.value = filteredUsers.length
    const startIndex = (currentPage.value - 1) * pageSize.value
    const endIndex = startIndex + pageSize.value
    users.value = filteredUsers.slice(startIndex, endIndex)
  } catch (error) {
    console.error('Load users error:', error)
    ElMessage.error('加载用户列表失败，请重试')
  }
}

// 搜索用户
function handleSearch() {
  currentPage.value = 1
  loadUsers()
}

// 重置筛选
function resetFilters() {
  searchUsername.value = ''
  searchEmail.value = ''
  searchStatus.value = ''
  currentPage.value = 1
  loadUsers()
}

// 分页处理
function handleSizeChange(size) {
  pageSize.value = size
  currentPage.value = 1
  loadUsers()
}

function handleCurrentChange(page) {
  currentPage.value = page
  loadUsers()
}

// 新增用户
function handleAddUser() {
  dialogTitle.value = '新增用户'
  formData.value = {
    username: '',
    email: '',
    password: '',
    is_admin: '0'
  }
  dialogVisible.value = true
}

// 编辑用户
function handleEditUser(user) {
  dialogTitle.value = '编辑用户'
  formData.value = {
    id: user.id,
    username: user.username,
    email: user.email,
    is_admin: user.is_admin.toString()
  }
  dialogVisible.value = true
}

// 保存用户
async function handleSaveUser() {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    if (formData.value.id) {
      // 编辑用户角色
      const res = await request.put(`/api/admin/users/${formData.value.id}`, {
        is_admin: parseInt(formData.value.is_admin)
      })
      
      if (res.code === 200) {
        ElMessage.success('编辑用户角色成功')
        dialogVisible.value = false
        loadUsers()
      } else {
        ElMessage.error('操作失败：' + res.msg)
      }
    } else {
      // 新增用户功能暂不可用，后端未提供API
      ElMessage.info('新增用户功能暂不可用')
      dialogVisible.value = false
    }
  } catch (error) {
    console.error('Save user error:', error)
    ElMessage.error('操作失败，请重试')
  }
}

// 切换用户状态
async function handleToggleStatus(user) {
  try {
    const res = await request.put(`/api/admin/users/${user.id}`, {
      is_admin: user.is_admin ? 0 : 1
    })
    
    if (res.code === 200) {
      ElMessage.success(`用户已${user.is_admin ? '禁用' : '启用'}`)
      loadUsers()
    } else {
      ElMessage.error('操作失败：' + res.msg)
    }
  } catch (error) {
    console.error('Toggle user status error:', error)
    ElMessage.error('操作失败，请重试')
  }
}

// 删除用户
async function handleDeleteUser(userId) {
  // 删除用户功能已替换为状态切换
  ElMessage.info('删除用户功能已替换为状态切换')
}

// 页面挂载时加载数据
onMounted(() => {
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

  // 加载数据
  loadUsers()
})
</script>

<style scoped>
.user-manage-page {
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 500;
}

.pagination {
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>