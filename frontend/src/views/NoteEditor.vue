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
            <AIModuleButton />
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAIStore } from '@/store/ai'
import AIModuleButton from '@/components/AIModuleButton.vue'

const Delta = Quill.import('delta')

const props = defineProps({
  isNew: {
    type: Boolean,
    default: false
  },
  'note-id': {
    type: [String, Number],
    default: null
  },
  'is-shared': {
    type: Boolean,
    default: false
  },
  'share-permission': {
    type: String,
    default: 'view'
  },
  'shared-note': {
    type: Object,
    default: null
  }
})

const route = useRoute()
const noteId = props['note-id'] || route.params.id

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
const showVersions = ref(false)
const selectedVersion = ref(null)
const versions = ref([])
const shareDialogVisible = ref(false)
const shareData = ref({ permission: 'view', expireAt: '' })
const shareUrl = ref('')
const shareExpireDate = ref('')
const existingShares = ref([])
const saveStatus = ref('')

// 初始化AI store
const aiStore = useAIStore()

// 监听AI生成的内容
watch(() => aiStore.hasNewContent, (hasNewContent) => {
  if (hasNewContent) {
    // 调用insertAiContent函数将AI生成的内容插入到笔记中
    insertAiContent(aiStore.generatedContent)
    // 重置AI store状态
    aiStore.resetGeneratedContent()
  }
})

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
    if (Array.isArray(content.ops)) {
      return new Delta(content.ops)
    } else {
      return new Delta([])
    }
  }
  if (typeof content === 'string') {
    try {
      const parsed = JSON.parse(content)
      if (parsed.ops && Array.isArray(parsed.ops)) {
        return new Delta(parsed.ops)
      } else if (Array.isArray(parsed)) {
        return new Delta(parsed)
      } else {
        return new Delta([{ insert: JSON.stringify(parsed) }])
      }
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
  try {
    if (delta instanceof Delta) {
      note.value.content = delta
    } else if (typeof delta === 'object') {
      if (delta.ops && Array.isArray(delta.ops)) {
        note.value.content = new Delta(delta.ops)
      } else {
        note.value.content = new Delta([])
      }
    } else {
      note.value.content = new Delta([])
    }
    handleAutoSave()
  } catch (error) {
    console.error('Quill update error:', error)
    note.value.content = new Delta([])
    handleAutoSave()
  }
}

async function loadNote() {
  if (props.isNew) return
  
  // 共享模式：使用传入的 shared-note
  if (props['is-shared'] && props['shared-note']) {
    const noteData = props['shared-note']
    
    if (noteData.type === 'richtext') {
          let content = { ops: [] }
          if (noteData.content) {
            if (typeof noteData.content === 'string') {
              try {
                const parsed = JSON.parse(noteData.content)
                if (parsed.ops && Array.isArray(parsed.ops)) {
                  content = parsed
                } else if (Array.isArray(parsed)) {
                  content = { ops: parsed }
                } else {
                  content = { ops: [{ insert: JSON.stringify(parsed) }] }
                }
              } catch (e) {
                console.warn('Failed to parse richtext content:', e)
                content = { ops: [{ insert: noteData.content }] }
              }
            } else if (typeof noteData.content === 'object') {
              if (noteData.content.ops && Array.isArray(noteData.content.ops)) {
                content = noteData.content
              } else {
                content = { ops: [{ insert: JSON.stringify(noteData.content) }] }
              }
            }
          }
          noteData.content = content
    } else if (noteData.type === 'markdown') {
      if (typeof noteData.content === 'object') {
        noteData.content = JSON.stringify(noteData.content)
      }
    }
    
    note.value = noteData
    
    // 处理标签
    if (Array.isArray(noteData.tags)) {
      selectedTags.value = noteData.tags.map(t => t.name)
    } else if (Array.isArray(noteData.tag_ids) && !props['is-shared']) {
      // 共享模式下跳过标签 API 调用
      // 如果返回的是tag_ids而不是tags，需要加载标签名称
      try {
        const tagNames = await Promise.all(
          noteData.tag_ids.map(async (tagId) => {
            const tag = await tagAPI.get(tagId)
            return tag.name
          })
        )
        selectedTags.value = tagNames
      } catch (error) {
        console.error('Load tags error:', error)
        selectedTags.value = []
      }
    } else {
      selectedTags.value = []
    }
    return
  }
  
  // 正常模式：从API加载
  try {
    const response = await noteAPI.get(noteId)
    
    // 使用response.data作为笔记对象
    const noteData = response.data
    
    if (noteData.type === 'richtext') {
          let content = { ops: [] }
          if (noteData.content) {
            if (typeof noteData.content === 'string') {
              try {
                const parsed = JSON.parse(noteData.content)
                if (parsed.ops && Array.isArray(parsed.ops)) {
                  content = parsed
                } else if (Array.isArray(parsed)) {
                  content = { ops: parsed }
                } else {
                  content = { ops: [{ insert: JSON.stringify(parsed) }] }
                }
              } catch (e) {
                console.warn('Failed to parse richtext content:', e)
                content = { ops: [{ insert: noteData.content }] }
              }
            } else if (typeof noteData.content === 'object') {
              if (noteData.content.ops && Array.isArray(noteData.content.ops)) {
                content = noteData.content
              } else {
                content = { ops: [{ insert: JSON.stringify(noteData.content) }] }
              }
            }
          }
          noteData.content = content
    } else if (noteData.type === 'markdown') {
      if (typeof noteData.content === 'object') {
        noteData.content = JSON.stringify(noteData.content)
      }
    }
    
    note.value = noteData
    
    // 处理标签
    if (Array.isArray(noteData.tags)) {
      selectedTags.value = noteData.tags.map(t => t.name)
    } else if (Array.isArray(noteData.tag_ids)) {
      // 如果返回的是tag_ids而不是tags，需要加载标签名称
      const tagNames = await Promise.all(
        noteData.tag_ids.map(async (tagId) => {
          const tag = await tagAPI.get(tagId)
          return tag.name
        })
      )
      selectedTags.value = tagNames
    } else {
      selectedTags.value = []
    }
  } catch (error) {
    console.error('Load note error:', error)
  }
}

async function loadCategories() {
  try {
    const response = await categoryAPI.getList()
    categories.value = Array.isArray(response.data) ? response.data : []
  } catch (error) {
    console.error('Load categories error:', error)
    categories.value = []
  }
}

async function loadTags() {
  try {
    const response = await tagAPI.getList()
    tags.value = Array.isArray(response.data) ? response.data : []
  } catch (error) {
    console.error('Load tags error:', error)
    tags.value = []
  }
}

function handleQuillUpdate(content) {
  note.value.content = content
  handleAutoSave()
}

async function loadVersions() {
  if (!note.value.id || props['is-shared']) return
  
  try {
    const response = await noteAPI.getVersions(note.value.id)
    versions.value = response.data || []
  } catch (error) {
    console.error('Load versions error:', error)
    versions.value = []
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
  if (props['is-shared']) {
    if (!silent) ElMessage.warning('共享模式下不能保存')
    return
  }
  
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
    
    // 生成唯一的默认标题
    let title = note.value.title
    if (!title) {
      const timestamp = new Date().getTime()
      title = `未命名笔记_${timestamp}`
    }
    
    const data = {
      title: title,
      content: contentToSend,
      type: note.value.type,
      category_id: note.value.category_id,
      tags: tagObjs
    }
    
    if (note.value.id) {
      await noteAPI.update(note.value.id, data)
    } else {
      const result = await noteAPI.create(data)
      note.value.id = result.data.id
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
    const response = await noteAPI.getShares(note.value.id)
    const shares = response.data || []
    existingShares.value = shares.map(share => ({
      ...share,
      share_url: `${window.location.origin}/share/${share.token}`
    }))
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
    shareUrl.value = `${window.location.origin}/share/${result.data.share_token}`
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

// 添加AI内容到笔记
function insertAiContent(content) {
  if (!content) return
  
  if (note.value.type === 'richtext') {
    if (!note.value.content || !note.value.content.ops) {
      note.value.content = { ops: [] }
    }
    // 确保content是字符串
    const contentStr = typeof content === 'string' ? content : JSON.stringify(content)
    // 插入新内容（添加换行符分隔）
    note.value.content.ops.push({ insert: '\n' })
    note.value.content.ops.push({ insert: contentStr })
    note.value.content.ops.push({ insert: '\n' })
  } else if (note.value.type === 'markdown') {
    // 确保content是字符串
    const contentStr = typeof content === 'string' ? content : JSON.stringify(content)
    // 添加新内容（添加换行符分隔）
    note.value.content = (note.value.content || '') + '\n\n' + contentStr + '\n\n'
  }
  
  // 自动保存
  handleAutoSave()
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
  
  // 共享模式下跳过不需要的函数调用
  if (!props['is-shared']) {
    loadCategories()
    loadTags()
    loadVersions()
  }
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
