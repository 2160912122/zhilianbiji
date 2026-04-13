<template>
  <div class="profile">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">个人资料</span>
          <el-icon class="card-icon"><User /></el-icon>
        </div>
      </template>
      <div class="profile-content">
        <div class="profile-avatar">
          <div class="avatar-container">
            <el-icon class="avatar-icon"><UserFilled /></el-icon>
          </div>
          <h2 class="profile-name">{{ userStore.user?.username || userStore.user?.email }}</h2>
        </div>
        <el-form :model="userForm" label-width="100px" class="profile-form">
          <el-form-item label="用户名">
            <el-input v-model="userForm.username" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="userForm.email" placeholder="请输入邮箱" />
          </el-form-item>
          <el-form-item label="手机号码">
            <el-input v-model="userForm.phone" placeholder="请输入手机号码" />
          </el-form-item>
          <el-form-item label="角色">
            <el-input v-model="userForm.role" disabled />
          </el-form-item>
          <el-form-item label="注册时间">
            <el-input v-model="userForm.created_at" disabled />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveProfile">保存修改</el-button>
            <el-button @click="cancelEdit">取消</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { User, UserFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const userStore = useUserStore()
const userForm = ref({
  username: '',
  email: '',
  phone: '',
  role: '',
  created_at: ''
})

// 加载用户资料
async function loadUserProfile() {
  try {
    // 调用获取用户资料的API
    const response = await request.get('/api/user/profile')
    if (response.code === 200) {
      const user = response.data
      userForm.value = {
        username: user.username || '',
        email: user.email || '',
        phone: user.phone || '',
        role: user.is_admin ? '管理员' : '普通用户',
        created_at: user.created_at || ''
      }
    }
  } catch (error) {
    console.error('加载用户资料失败:', error)
  }
}

// 保存用户资料
async function saveProfile() {
  try {
    // 调用更新用户资料的API
    const response = await request.put('/api/user/profile', userForm.value)
    if (response.code === 200) {
      ElMessage.success('保存成功')
      // 更新store中的用户信息
      if (userStore.user) {
        userStore.user = response.data
      }
    }
  } catch (error) {
    console.error('保存用户资料失败:', error)
    ElMessage.error('保存失败')
  }
}

// 取消编辑
function cancelEdit() {
  loadUserProfile()
}

// 页面挂载时加载用户资料
onMounted(() => {
  loadUserProfile()
})
</script>

<style scoped>
.profile {
  padding: 20px;
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

.profile-content {
  padding: 20px;
}

.profile-avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
}

.avatar-container {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 48px;
  box-shadow: var(--shadow-md);
  margin-bottom: 16px;
}

.profile-name {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary, #303133);
  margin: 0;
}

.profile-form {
  max-width: 600px;
  margin: 0 auto;
}

.profile-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: var(--text-secondary, #606266);
}

.profile-form :deep(.el-input__wrapper) {
  border-radius: var(--border-radius-md);
}
</style>