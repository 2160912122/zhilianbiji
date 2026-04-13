<template>
  <div class="settings">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">设置</span>
          <el-icon class="card-icon"><Setting /></el-icon>
        </div>
      </template>
      <div class="settings-content">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="账户设置" name="account">
            <el-form :model="accountForm" label-width="120px" class="settings-form">
              <el-form-item label="修改密码">
                <el-button type="primary" @click="openPasswordDialog">修改密码</el-button>
              </el-form-item>
              <el-form-item label="通知设置">
                <el-switch v-model="accountForm.notifications" />
              </el-form-item>
              <el-form-item label="邮件提醒">
                <el-switch v-model="accountForm.emailNotifications" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveAccountSettings">保存设置</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
          <el-tab-pane label="界面设置" name="interface">
            <el-form :model="interfaceForm" label-width="120px" class="settings-form">
              <el-form-item label="主题">
                <el-select v-model="interfaceForm.theme" placeholder="选择主题">
                  <el-option label="浅色" value="light" />
                  <el-option label="深色" value="dark" />
                </el-select>
              </el-form-item>
              <el-form-item label="语言">
                <el-select v-model="interfaceForm.language" placeholder="选择语言">
                  <el-option label="中文" value="zh-CN" />
                  <el-option label="英文" value="en-US" />
                </el-select>
              </el-form-item>
              <el-form-item label="字体大小">
                <el-slider v-model="interfaceForm.fontSize" :min="12" :max="18" :step="1" />
                <span class="font-size-value">{{ interfaceForm.fontSize }}px</span>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveInterfaceSettings">保存设置</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
          <el-tab-pane label="数据设置" name="data">
            <el-form label-width="120px" class="settings-form">
              <el-form-item label="导出数据">
                <el-button type="primary" @click="exportData">导出数据</el-button>
              </el-form-item>
              <el-form-item label="导入数据">
                <el-upload
                  class="upload-demo"
                  action="#"
                  :on-change="handleFileChange"
                  :auto-upload="false"
                >
                  <el-button type="primary">选择文件</el-button>
                  <template #tip>
                    <div class="el-upload__tip">
                      请选择要导入的数据文件
                    </div>
                  </template>
                </el-upload>
              </el-form-item>
              <el-form-item label="清空数据">
                <el-button type="danger" @click="clearData">清空数据</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="修改密码"
      width="500px"
    >
      <el-form :model="passwordForm" label-width="120px" class="password-form">
        <el-form-item label="当前密码">
          <el-input v-model="passwordForm.currentPassword" type="password" placeholder="请输入当前密码" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请确认新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="passwordDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="changePassword">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Setting } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const activeTab = ref('account')
const passwordDialogVisible = ref(false)

// 账户设置表单
const accountForm = ref({
  notifications: true,
  emailNotifications: true
})

// 界面设置表单
const interfaceForm = ref({
  theme: 'light',
  language: 'zh-CN',
  fontSize: 14
})

// 密码修改表单
const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 加载设置
function loadSettings() {
  // 这里应该从localStorage或API加载设置
  const savedSettings = localStorage.getItem('userSettings')
  if (savedSettings) {
    const settings = JSON.parse(savedSettings)
    accountForm.value = { ...accountForm.value, ...settings.account }
    interfaceForm.value = { ...interfaceForm.value, ...settings.interface }
  }
}

// 保存账户设置
function saveAccountSettings() {
  try {
    // 这里应该调用保存设置的API
    console.log('保存账户设置:', accountForm.value)
    saveSettingsToLocalStorage()
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存账户设置失败:', error)
    ElMessage.error('保存失败')
  }
}

// 保存界面设置
function saveInterfaceSettings() {
  try {
    // 这里应该调用保存设置的API
    console.log('保存界面设置:', interfaceForm.value)
    saveSettingsToLocalStorage()
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存界面设置失败:', error)
    ElMessage.error('保存失败')
  }
}

// 保存设置到本地存储
function saveSettingsToLocalStorage() {
  const settings = {
    account: accountForm.value,
    interface: interfaceForm.value
  }
  localStorage.setItem('userSettings', JSON.stringify(settings))
}

// 打开修改密码对话框
function openPasswordDialog() {
  passwordDialogVisible.value = true
}

// 修改密码
async function changePassword() {
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }
  
  try {
    // 调用修改密码的API
    const response = await request.post('/api/user/change-password', {
      current_password: passwordForm.value.currentPassword,
      new_password: passwordForm.value.newPassword,
      confirm_password: passwordForm.value.confirmPassword
    })
    if (response.code === 200) {
      ElMessage.success('密码修改成功')
      passwordDialogVisible.value = false
    }
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error('修改密码失败')
  }
}

// 导出数据
async function exportData() {
  try {
    const response = await request.get('/api/user/export-data')
    if (response.code === 200) {
      // 创建下载文件
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `notes_backup_${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      ElMessage.success('数据导出成功')
    }
  } catch (error) {
    console.error('导出数据失败:', error)
    ElMessage.error('导出数据失败')
  }
}

// 处理文件上传（导入数据）
async function handleFileChange(file) {
  const fileObj = file.raw
  if (!fileObj) {
    ElMessage.error('请选择有效文件')
    return
  }
  
  const reader = new FileReader()
  reader.onload = async (e) => {
    try {
      const data = JSON.parse(e.target.result)
      const response = await request.post('/api/user/import-data', data)
      if (response.code === 200) {
        ElMessage.success(`数据导入成功！共导入 ${response.data.notes + response.data.flowcharts + response.data.tables + response.data.whiteboards + response.data.mindmaps} 条数据`)
      }
    } catch (error) {
      console.error('导入数据失败:', error)
      ElMessage.error('导入数据失败，请确保文件格式正确')
    }
  }
  reader.readAsText(fileObj)
}

// 清空数据
async function clearData() {
  try {
    await ElMessageBox.confirm('确定要清空所有数据吗？此操作不可恢复！', '警告', {
      confirmButtonText: '确定清空',
      cancelButtonText: '取消',
      type: 'warning',
      dangerMode: true
    })
    
    const response = await request.delete('/api/user/clear-data')
    if (response.code === 200) {
      ElMessage.success('数据清空成功')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空数据失败:', error)
      ElMessage.error('清空数据失败')
    }
  }
}

// 页面挂载时加载设置
onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.settings {
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

.settings-content {
  padding: 20px;
}

.settings-form {
  max-width: 600px;
  margin: 0 auto;
}

.settings-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: var(--text-secondary, #606266);
}

.settings-form :deep(.el-input__wrapper) {
  border-radius: var(--border-radius-md);
}

.font-size-value {
  margin-left: 12px;
  font-size: 14px;
  color: var(--text-secondary, #606266);
}

.password-form {
  max-width: 400px;
}

.dialog-footer {
  text-align: right;
}
</style>