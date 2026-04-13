<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="handleClose"
    :title="title"
    width="550px"
    :close-on-click-modal="false"
  >
    <div class="share-content">
      <h4 class="share-title">创建分享链接</h4>
      
      <el-form :model="shareForm" label-width="80px">
        <el-form-item label="权限" required>
          <el-select v-model="shareForm.permission" style="width: 200px;">
            <el-option label="只读" value="view" />
            <el-option label="可编辑" value="edit" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="过期时间">
          <el-select v-model="shareForm.expireDays" style="width: 200px;">
            <el-option label="永不过期" :value="0" />
            <el-option label="1天" :value="1" />
            <el-option label="7天" :value="7" />
            <el-option label="30天" :value="30" />
          </el-select>
        </el-form-item>
        
        <el-form-item v-if="shareForm.permission === 'edit'" label="实时协作">
          <el-tag type="success">已启用</el-tag>
          <span class="collab-tip">可编辑权限默认开启实时协作，多人可同时编辑</span>
        </el-form-item>
      </el-form>
      
      <div v-if="shareUrl" class="share-url-section">
        <el-form-item label="分享链接">
          <el-input :value="shareUrl" readonly>
            <template #append>
              <el-button @click="copyShareUrl">复制</el-button>
            </template>
          </el-input>
        </el-form-item>
        <div class="share-info">
          <span>此链接有效期至: {{ expireDateText }}</span>
        </div>
      </div>
      
      <div v-if="existingShares.length > 0" class="existing-shares">
        <h4>已存在的分享</h4>
        <el-table :data="existingShares" style="width: 100%" size="small">
          <el-table-column prop="permission" label="权限" width="100">
            <template #default="{ row }">
              <el-tag :type="row.permission === 'view' ? 'info' : 'success'">
                {{ row.permission === 'view' ? '只读' : '可编辑' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="expireAt" label="过期时间" width="150">
            <template #default="{ row }">
              {{ row.expireAt || '永久' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button link type="primary" @click="copyLink(row.url)">复制</el-button>
              <el-button link type="danger" @click="deleteShare(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
    
    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
      <el-button type="primary" @click="generateShareLink" :loading="loading">
        {{ shareUrl ? '重新生成' : '生成链接' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>import { ref, computed, watch } from 'vue';
import { ElMessage } from 'element-plus';
import request from '@/utils/request';
const props = defineProps({
 visible: Boolean,
 resourceId: {
 type: Number,
 required: true
 },
 resourceType: {
 type: String,
 required: true
 },
 resourceName: {
 type: String,
 default: ''
 }
});
const emit = defineEmits(['update:visible']);
const title = computed(() => {
 const typeNames = {
 note: '分享笔记',
 flowchart: '分享流程图',
 mindmap: '分享脑图',
 table_document: '分享表格',
 whiteboard: '分享白板',
 knowledge_graph: '分享知识图谱'
 };
 return typeNames[props.resourceType] || '分享';
});
const loading = ref(false);
const shareUrl = ref('');
const shareForm = ref({
 permission: 'view',
 expireDays: 7,
 isCollaborative: false
});

watch(() => shareForm.value.permission, (newPermission) => {
 if (newPermission === 'edit') {
 shareForm.value.isCollaborative = true;
 } else {
 shareForm.value.isCollaborative = false;
 }
});
const existingShares = ref([]);
const expireDateText = computed(() => {
 if (!shareUrl.value)
 return '';
 if (shareForm.value.expireDays === 0)
 return '永久';
 const expireDate = new Date();
 expireDate.setDate(expireDate.getDate() + shareForm.value.expireDays);
 return expireDate.toLocaleString('zh-CN');
});
watch(() => props.visible, (val) => {
 if (val) {
 shareUrl.value = '';
 shareForm.value = {
 permission: 'view',
 expireDays: 7,
 isCollaborative: false
 };
 loadExistingShares();
 }
});
async function loadExistingShares() {
 try {
 const response = await request.post('/api/shares/list', {
 resource_id: props.resourceId,
 resource_type: props.resourceType
 });
 if (response.code === 200) {
 existingShares.value = response.data.map(item => ({
 id: item.id,
 permission: item.permission,
 expireAt: item.expire_at ? formatDate(item.expire_at) : '永久',
 url: `${window.location.origin}/share/${item.token}`
 }));
 }
 else {
 existingShares.value = [];
 }
 }
 catch (error) {
 console.error('加载分享列表失败:', error);
 existingShares.value = [];
 }
}
function formatDate(dateStr) {
 const date = new Date(dateStr);
 return date.toLocaleDateString('zh-CN');
}
async function generateShareLink() {
 loading.value = true;
 try {
 const response = await request.post('/api/shares', {
 resource_id: props.resourceId,
 resource_type: props.resourceType,
 permission: shareForm.value.permission,
 expire_days: shareForm.value.expireDays,
 is_collaborative: shareForm.value.isCollaborative
 });
 if (response.code === 201) {
 shareUrl.value = `${window.location.origin}/share/${response.data.token}`;
 ElMessage.success('分享链接已生成');
 loadExistingShares();
 }
 else {
 ElMessage.error(response.message || '生成失败');
 }
 }
 catch (error) {
 console.error('生成分享链接失败:', error);
 const message = error.response?.data?.message || error.message || '生成失败';
 ElMessage.error(message);
 }
 finally {
 loading.value = false;
 }
}
function copyShareUrl() {
 navigator.clipboard.writeText(shareUrl.value);
 ElMessage.success('链接已复制到剪贴板');
}
function copyLink(url) {
 navigator.clipboard.writeText(url);
 ElMessage.success('链接已复制到剪贴板');
}
async function deleteShare(shareId) {
 try {
 await request.delete(`/api/shares/${shareId}`);
 ElMessage.success('删除成功');
 loadExistingShares();
 }
 catch (error) {
 console.error('删除分享链接失败:', error);
 ElMessage.error('删除失败');
 }
}
function handleClose(val) {
 emit('update:visible', val);
}
</script>

<style scoped>
.share-content {
  padding: 10px 0;
}

.share-title {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #303133;
}

.collab-tip {
  margin-left: 10px;
  font-size: 12px;
  color: #909399;
}

.share-url-section {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #EBEEF5;
}

.share-info {
  font-size: 12px;
  color: #606266;
  margin-top: 8px;
}

.existing-shares {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #EBEEF5;
}

.existing-shares h4 {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #303133;
}
</style>