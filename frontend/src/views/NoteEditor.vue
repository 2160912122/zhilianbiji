<template>
  <div class="note-editor">
    <el-card>
      <template #header>
        <div class="editor-header">
          <div class="header-left">
            <el-button link @click="$router.back()">
              <el-icon><Back /></el-icon>
              返回
            </el-button>
            <el-input
              v-model="note.title"
              placeholder="请输入标题"
              style="width: 300px; margin-left: 20px"
              @input="handleAutoSave"
            />
          </div>
          <div class="header-right">
            <el-button @click="handleAIGenerate">
              <el-icon><MagicStick /></el-icon>
              AI生成
            </el-button>
            <el-button @click="handleAISummarize">
              <el-icon><ChatLineSquare /></el-icon>
              AI总结
            </el-button>
            <el-button @click="handleAISuggestTags">
              <el-icon><PriceTag /></el-icon>
              AI推荐标签
            </el-button>
            <el-button @click="handleSave" type="primary">
              <el-icon><Check /></el-icon>
              保存
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="editor-toolbar">
        <el-radio-group v-model="note.type" @change="handleTypeChange">
          <el-radio-button value="richtext">富文本</el-radio-button>
          <el-radio-button value="markdown">Markdown</el-radio-button>
        </el-radio-group>
        
        <el-select
          v-model="note.category_id"
          placeholder="选择分类"
          clearable
          style="width: 150px; margin-left: 20px"
        >
          <el-option
            v-for="cat in categories"
            :key="cat.id"
            :label="cat.name"
            :value="cat.id"
          />
        </el-select>
        
        <el-select
          v-model="selectedTags"
          multiple
          filterable
          allow-create
          placeholder="选择标签"
          style="width: 250px; margin-left: 10px"
        >
          <el-option
            v-for="tag in tags"
            :key="tag.id"
            :label="tag.name"
            :value="tag.name"
          />
        </el-select>
      </div>
      
      <div class="editor-content">
        <QuillEditor
          v-if="note.type === 'richtext'"
          :content="quillContent"
          theme="snow"
          style="height: 500px"
          @ready="onQuillReady"
          @update:content="onQuillUpdate"
        />
        <div v-if="note.type === 'markdown'" class="markdown-editor">
          <textarea
            v-model="note.content"
            class="markdown-textarea"
            placeholder="输入Markdown内容..."
            @input="handleAutoSave"
          />
          <div class="markdown-preview" v-html="renderedMarkdown"></div>
        </div>
      </div>
      
      <div class="editor-footer">
        <span class="save-status">{{ saveStatus }}</span>
        <el-button link @click="showVersions = true">
          <el-icon><Clock /></el-icon>
          版本历史
        </el-button>
        <el-button link @click="handleShare">
          <el-icon><Share /></el-icon>
          分享
        </el-button>
      </div>
    </el-card>
    
    <el-dialog v-model="aiDialogVisible" title="AI生成" width="600px">
      <el-input
        v-model="aiTopic"
        type="textarea"
        :rows="3"
        placeholder="请输入主题，AI将为您生成笔记内容"
      />
      <template #footer>
        <el-button @click="aiDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAIGenerate" :loading="aiLoading">
          生成
        </el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="shareDialogVisible" title="分享笔记" width="700px">
      <el-form label-width="80px">
        <el-form-item label="权限">
          <el-select v-model="shareData.permission">
            <el-option label="只读" value="view" />
            <el-option label="可编辑" value="edit" />
          </el-select>
        </el-form-item>
        <el-form-item label="过期时间">
          <el-select v-model="shareData.expireAt">
            <el-option label="永不过期" value="" />
            <el-option label="1分钟" value="1m" />
            <el-option label="1天" value="1d" />
            <el-option label="7天" value="7d" />
            <el-option label="30天" value="30d" />
          </el-select>
        </el-form-item>
        <el-form-item label="分享链接" v-if="shareUrl">
          <el-input v-model="shareUrl" readonly>
            <template #append>
              <el-button @click="copyShareUrl">复制</el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item v-if="shareUrl">
          <span class="share-info">此链接有效期至: {{ shareExpireDate || '永久' }}</span>
        </el-form-item>
      </el-form>
      
      <div v-if="existingShares.length > 0" class="existing-shares">
        <h4>已存在的分享</h4>
        <el-table :data="existingShares" style="width: 100%">
          <el-table-column prop="share_url" label="链接" min-width="200">
            <template #default="{ row }">
              <el-input :value="row.share_url" readonly size="small" />
            </template>
          </el-table-column>
          <el-table-column prop="permission" label="权限" width="100">
            <template #default="{ row }">
              <el-tag :type="row.permission === 'view' ? 'info' : 'success'">
                {{ row.permission === 'view' ? '只读' : '可编辑' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column prop="expire_at" label="过期时间" width="180">
            <template #default="{ row }">
              {{ row.expire_at ? formatDate(row.expire_at) : '永久' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button link type="danger" @click="deleteShare(row.token)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <template #footer>
        <el-button @click="shareDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="generateShareLink">
          生成链接
        </el-button>
      </template>
    </el-dialog>
    
    <el-drawer v-model="showVersions" title="版本历史" size="40%">
      <el-timeline>
        <el-timeline-item
          v-for="version in versions"
          :key="version.id"
          :timestamp="version.updated_at"
          placement="top"
        >
          <div class="version-item">
            <div class="version-content">{{ version.content_preview }}</div>
            <div class="version-actions">
              <el-button link type="primary" @click="previewVersion(version)">预览</el-button>
              <el-button link type="warning" @click="rollbackVersion(version)">
                回滚
              </el-button>
            </div>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { QuillEditor, Quill } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import { marked } from 'marked'
import { noteAPI } from '@/api/note'
import { categoryAPI, tagAPI } from '@/api/common'
import { aiAPI } from '@/api/ai'
import { ElMessage, ElMessageBox } from 'element-plus'

const Delta = Quill.import('delta')

const props = defineProps({
  isNew: {
    type: Boolean,
    default: false
  }
})

const route = useRoute()
const noteId = route.params.id

const note = ref({
  id: null,
  title: '',
  content: { ops: [] },
  type: 'richtext',
  category_id: null,
  tags: []
})

const categories = ref([])
const tags = ref([])
const selectedTags = ref([])
const versions = ref([])
const saveStatus = ref('未保存')

const aiDialogVisible = ref(false)
const aiTopic = ref('')
const aiLoading = ref(false)

const shareDialogVisible = ref(false)
const shareData = ref({
  permission: 'view',
  expireAt: ''
})
const shareUrl = ref('')
const shareExpireDate = ref('')
const existingShares = ref([])

const showVersions = ref(false)

let autoSaveTimer = null

const renderedMarkdown = computed(() => {
  const content = note.value.content
  if (!content) return ''
  const contentStr = typeof content === 'object' ? JSON.stringify(content) : content
  if (!contentStr || contentStr === '{"ops":[]}') return ''
  return marked(contentStr)
})

const quillContent = computed(() => {
  if (note.value.type !== 'richtext') return null
  const content = note.value.content
  if (!content) return new Delta([])
  if (content instanceof Delta) return content
  if (typeof content === 'object' && content.ops) {
    return new Delta(content.ops)
  }
  if (typeof content === 'string') {
    try {
      const parsed = JSON.parse(content)
      if (parsed.ops) {
        return new Delta(parsed.ops)
      }
      return new Delta([{ insert: parsed }])
    } catch (e) {
      return new Delta([{ insert: content }])
    }
  }
  return new Delta([])
})

let quillInstance = null

function onQuillReady(quill) {
  quillInstance = quill
}

function onQuillUpdate(delta) {
  if (delta instanceof Delta) {
    note.value.content = delta
  } else if (typeof delta === 'object' && delta.ops) {
    note.value.content = new Delta(delta.ops)
  } else {
    note.value.content = new Delta([])
  }
  handleAutoSave()
}

async function loadNote() {
  if (props.isNew) return
  
  try {
    const data = await noteAPI.get(noteId)
    
    if (data.note.type === 'richtext') {
      let content = { ops: [] }
      if (data.note.content) {
        if (typeof data.note.content === 'string') {
          try {
            const parsed = JSON.parse(data.note.content)
            content = parsed.ops ? parsed : { ops: parsed }
          } catch (e) {
            console.warn('Failed to parse richtext content:', e)
            content = { ops: [{ insert: data.note.content }] }
          }
        } else if (typeof data.note.content === 'object' && data.note.content.ops) {
          content = data.note.content
        }
      }
      data.note.content = content
    } else if (data.note.type === 'markdown') {
      if (typeof data.note.content === 'object') {
        data.note.content = JSON.stringify(data.note.content)
      }
    }
    
    note.value = data.note
    selectedTags.value = data.note.tags.map(t => t.name)
  } catch (error) {
    console.error('Load note error:', error)
  }
}

async function loadCategories() {
  try {
    categories.value = await categoryAPI.getList()
  } catch (error) {
    console.error('Load categories error:', error)
  }
}

async function loadTags() {
  try {
    tags.value = await tagAPI.getList()
  } catch (error) {
    console.error('Load tags error:', error)
  }
}

function handleQuillUpdate(content) {
  note.value.content = content
  handleAutoSave()
}

async function loadVersions() {
  if (!note.value.id) return
  
  try {
    versions.value = await noteAPI.getVersions(note.value.id)
  } catch (error) {
    console.error('Load versions error:', error)
  }
}

function handleAutoSave() {
  saveStatus.value = '正在保存...'
  
  if (autoSaveTimer) clearTimeout(autoSaveTimer)
  autoSaveTimer = setTimeout(() => {
    handleSave(true)
  }, 2000)
}

async function handleSave(silent = false) {
  if (autoSaveTimer) clearTimeout(autoSaveTimer)
  
  try {
    const tagObjs = selectedTags.value.map(name => {
      const existing = tags.value.find(t => t.name === name)
      return existing ? { id: existing.id } : { name }
    })
    
    let contentToSend = note.value.content
    if (note.value.type === 'richtext' && typeof note.value.content === 'object') {
      if (!note.value.content.ops || note.value.content.ops.length === 0) {
        contentToSend = ''
      } else {
        contentToSend = JSON.stringify(note.value.content)
      }
    }
    
    const data = {
      title: note.value.title || '未命名笔记',
      content: contentToSend,
      type: note.value.type,
      category_id: note.value.category_id,
      tags: tagObjs
    }
    
    if (note.value.id) {
      await noteAPI.update(note.value.id, data)
    } else {
      const result = await noteAPI.create(data)
      note.value.id = result.note.id
    }
    
    await loadVersions()
    
    saveStatus.value = '已保存'
    if (!silent) ElMessage.success('保存成功')
  } catch (error) {
    console.error('Save note error:', error)
    saveStatus.value = '保存失败'
    if (!silent) ElMessage.error('保存失败')
  }
}

function handleTypeChange() {
  if (autoSaveTimer) clearTimeout(autoSaveTimer)
}

async function handleAIGenerate() {
  aiDialogVisible.value = true
}

async function confirmAIGenerate() {
  if (!aiTopic.value.trim()) {
    ElMessage.warning('请输入主题')
    return
  }
  
  aiLoading.value = true
  
  try {
    const result = await aiAPI.generate(aiTopic.value)
    note.value.content = result.content
    note.value.title = result.suggested_title
    aiDialogVisible.value = false
    aiTopic.value = ''
    ElMessage.success('AI生成成功')
    handleAutoSave()
  } catch (error) {
    console.error('AI generate error:', error)
    ElMessage.error('AI生成失败')
  } finally {
    aiLoading.value = false
  }
}

async function handleAISummarize() {
  if (!note.value.content) {
    ElMessage.warning('请先输入内容')
    return
  }
  
  let content = note.value.content
  if (note.value.type === 'richtext' && typeof content === 'object') {
    content = JSON.stringify(content)
  }
  
  try {
    const result = await aiAPI.summarize(content)
    ElMessageBox.alert(result.summary, 'AI总结', {
      confirmButtonText: '确定'
    })
  } catch (error) {
    console.error('AI summarize error:', error)
    ElMessage.error('AI总结失败')
  }
}

async function handleAISuggestTags() {
  if (!note.value.content) {
    ElMessage.warning('请先输入内容')
    return
  }
  
  let content = note.value.content
  if (note.value.type === 'richtext' && typeof content === 'object') {
    content = JSON.stringify(content)
  }
  
  try {
    const result = await aiAPI.suggestTags(content)
    selectedTags.value = [...new Set([...selectedTags.value, ...result.tags])]
    ElMessage.success('标签推荐成功')
  } catch (error) {
    console.error('AI suggest tags error:', error)
    ElMessage.error('标签推荐失败')
  }
}

async function handleShare() {
  if (!note.value.id) {
    ElMessage.warning('请先保存笔记')
    return
  }
  
  shareDialogVisible.value = true
  shareUrl.value = ''
  await loadExistingShares()
}

async function loadExistingShares() {
  try {
    const shares = await noteAPI.getShares(note.value.id)
    existingShares.value = shares
  } catch (error) {
    console.error('Load shares error:', error)
  }
}

async function generateShareLink() {
  try {
    let expireAt = null
    if (shareData.value.expireAt) {
      const expireDate = new Date()
      if (shareData.value.expireAt === '1m') {
        expireDate.setMinutes(expireDate.getMinutes() + 1)
      } else if (shareData.value.expireAt === '1d') {
        expireDate.setDate(expireDate.getDate() + 1)
      } else if (shareData.value.expireAt === '7d') {
        expireDate.setDate(expireDate.getDate() + 7)
      } else if (shareData.value.expireAt === '30d') {
        expireDate.setDate(expireDate.getDate() + 30)
      }
      expireAt = new Date(expireDate.getTime() - expireDate.getTimezoneOffset() * 60000).toISOString().slice(0, -1)
      shareExpireDate.value = formatDate(expireAt)
    } else {
      shareExpireDate.value = ''
    }

    const result = await noteAPI.share(note.value.id, {
      permission: shareData.value.permission,
      expire_at: expireAt
    })
    shareUrl.value = `${window.location.origin}${result.share_url}`
    ElMessage.success('分享链接生成成功')
    await loadExistingShares()
  } catch (error) {
    console.error('Share note error:', error)
    ElMessage.error('生成分享链接失败')
  }
}

async function deleteShare(token) {
  try {
    await noteAPI.deleteShare(token)
    ElMessage.success('分享已删除')
    await loadExistingShares()
  } catch (error) {
    console.error('Delete share error:', error)
    ElMessage.error('删除分享失败')
  }
}

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

function copyShareUrl() {
  navigator.clipboard.writeText(shareUrl.value)
  ElMessage.success('已复制到剪贴板')
}

function previewVersion(version) {
  ElMessageBox.alert(version.content, '版本预览', {
    confirmButtonText: '关闭'
  })
}

async function rollbackVersion(version) {
  try {
    await ElMessageBox.confirm('确定要回滚到此版本吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await noteAPI.rollbackVersion(note.value.id, version.id)
    note.value.content = version.content
    ElMessage.success('回滚成功')
    loadVersions()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Rollback version error:', error)
      ElMessage.error('回滚失败')
    }
  }
}

watch(() => note.value.type, (newType, oldType) => {
  if (!oldType) return
  
  if (newType === 'richtext') {
    if (typeof note.value.content === 'string') {
      note.value.content = { ops: [{ insert: note.value.content }] }
    } else if (!note.value.content || !note.value.content.ops) {
      note.value.content = { ops: [] }
    }
  } else if (newType === 'markdown') {
    if (typeof note.value.content === 'object') {
      const contentStr = note.value.content.ops 
        ? note.value.content.ops.map(op => op.insert || '').join('') 
        : JSON.stringify(note.value.content)
      note.value.content = contentStr
    }
  }
})

onMounted(async () => {
  if (props.isNew) {
    if (note.value.type === 'richtext' && (!note.value.content || typeof note.value.content !== 'object')) {
      note.value.content = { ops: [] }
    }
  }
  await loadNote()
  loadCategories()
  loadTags()
  loadVersions()
})

onUnmounted(() => {
  if (autoSaveTimer) clearTimeout(autoSaveTimer)
})
</script>

<style scoped>
.note-editor {
  padding: 20px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e6e6e6;
}

.editor-content {
  min-height: 500px;
}

.markdown-editor {
  display: flex;
  gap: 20px;
  height: 500px;
}

.markdown-textarea {
  flex: 1;
  padding: 15px;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  resize: none;
}

.markdown-preview {
  flex: 1;
  padding: 15px;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  overflow-y: auto;
}

.markdown-preview :deep(h1),
.markdown-preview :deep(h2),
.markdown-preview :deep(h3) {
  margin-top: 0;
}

.editor-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #e6e6e6;
}

.existing-shares {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e6e6e6;
}

.existing-shares h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #333;
}

.share-info {
  color: #409eff;
  font-size: 14px;
}

.save-status {
  font-size: 12px;
  color: #999;
}

.version-item {
  margin-bottom: 10px;
}

.version-content {
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
  margin-bottom: 5px;
  font-size: 12px;
  color: #666;
}

.version-actions {
  display: flex;
  gap: 10px;
}
</style>
