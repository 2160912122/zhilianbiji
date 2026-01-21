<template>
  <div class="note-container">
    <el-card class="note-card">
      <h2 class="note-title">笔记管理</h2>
      
      <!-- 新增/编辑笔记表单 -->
      <el-form :model="noteForm" :rules="noteRules" ref="noteFormRef" inline style="margin-bottom: 20px;">
        <el-form-item label="标题" prop="title">
          <el-input v-model="noteForm.title" placeholder="请输入笔记标题" style="width: 300px;"></el-input>
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="noteForm.type" placeholder="请选择笔记类型">
            <el-option label="技术笔记" value="技术笔记"></el-option>
            <el-option label="生活记录" value="生活记录"></el-option>
            <el-option label="学习总结" value="学习总结"></el-option>
            <el-option label="其他" value="其他"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="noteForm.content" type="textarea" placeholder="请输入笔记内容" :rows="3"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSaveNote">保存笔记</el-button>
          <el-button @click="resetNoteForm">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 笔记列表 -->
      <el-table :data="noteList" border stripe style="width: 100%;">
        <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>
        <el-table-column prop="title" label="标题" min-width="200"></el-table-column>
        <el-table-column prop="type" label="类型" width="120" align="center"></el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="200" align="center"></el-table-column>
        <el-table-column prop="viewCount" label="访问量" width="100" align="center"></el-table-column>
        <el-table-column label="操作" width="180" align="center">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleEditNote(scope.row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDeleteNote(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

// 笔记列表
const noteList = ref([])
// 笔记表单
const noteForm = reactive({
  id: '', // 编辑时赋值
  title: '',
  type: '',
  content: ''
})
// 表单校验规则
const noteRules = reactive({
  title: [{ required: true, message: '请输入笔记标题', trigger: 'blur' }],
  type: [{ required: true, message: '请选择笔记类型', trigger: 'change' }],
  content: [{ required: true, message: '请输入笔记内容', trigger: 'blur' }]
})
const noteFormRef = ref(null)
const isEdit = ref(false) // 是否为编辑状态

// 加载笔记列表
const loadNoteList = async () => {
  try {
    const res = await request.get('/api/notes')
    noteList.value = res.data
  } catch (error) {
    ElMessage.error('加载笔记列表失败！')
  }
}

// 页面挂载时加载列表
onMounted(() => {
  loadNoteList()
})

// 保存笔记（新增/编辑）
const handleSaveNote = async () => {
  const valid = await noteFormRef.value.validate()
  if (!valid) return

  try {
    if (isEdit.value) {
      // 编辑笔记
      await request.put(`/api/notes/${noteForm.id}`, noteForm)
      ElMessage.success('笔记编辑成功！')
    } else {
      // 新增笔记
      await request.post('/api/notes', noteForm)
      ElMessage.success('笔记新增成功！')
    }
    resetNoteForm()
    loadNoteList()
  } catch (error) {
    ElMessage.error(isEdit.value ? '编辑笔记失败！' : '新增笔记失败！')
  }
}

// 编辑笔记
const handleEditNote = (row) => {
  isEdit.value = true
  // 赋值到表单
  noteForm.id = row.id
  noteForm.title = row.title
  noteForm.type = row.type
  noteForm.content = row.content
}

// 删除笔记
const handleDeleteNote = async (id) => {
  try {
    await request.delete(`/api/notes/${id}`)
    ElMessage.success('笔记删除成功！')
    loadNoteList()
  } catch (error) {
    ElMessage.error('删除笔记失败！')
  }
}

// 重置表单
const resetNoteForm = () => {
  noteForm.id = ''
  noteForm.title = ''
  noteForm.type = ''
  noteForm.content = ''
  isEdit.value = false
  if (noteFormRef.value) {
    noteFormRef.value.clearValidate()
  }
}
</script>

<style scoped>
.note-container {
  padding: 20px;
}
.note-card {
  padding: 20px;
}
.note-title {
  margin: 0 0 20px 0;
  color: #1989fa;
  font-size: 18px;
}
</style>