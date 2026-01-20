<template>
  <div class="container">
    <h1>编辑笔记</h1>
    <div class="actions">
      <router-link :to="`/notes/${note.id}`" class="btn btn-secondary" v-if="note">返回详情</router-link>
      <router-link :to="'/'" class="btn btn-secondary" v-else>返回笔记列表</router-link>
    </div>
    
    <div v-if="isLoading" class="loading">
      <p>正在加载笔记...</p>
    </div>
    
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>
    
    <div class="note-form" v-else-if="note">
      <div class="form-group">
        <label for="title">标题</label>
        <input 
          type="text" 
          id="title" 
          v-model="note.title" 
          class="form-control"
          placeholder="输入笔记标题"
        />
      </div>
      
      <div class="form-group">
        <label for="category">分类</label>
        <select v-model="note.category_id" id="category" class="form-control">
          <option value="">选择分类</option>
          <option v-for="category in categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
      </div>
      
      <div class="form-group">
        <label for="content">内容</label>
        <!-- Markdown编辑器 -->
        <div v-if="note.type === 'markdown'" class="markdown-editor-container">
          <!-- Markdown工具栏 -->
          <div class="markdown-toolbar">
            <button @click="insertMarkdown('**', '**')" title="加粗"><strong>B</strong></button>
            <button @click="insertMarkdown('*', '*')" title="斜体"><em>I</em></button>
            <button @click="insertMarkdown('__', '__')" title="下划线"><u>U</u></button>
            <button @click="insertMarkdown('~~', '~~')" title="删除线">S</button>
            <div class="toolbar-divider"></div>
            <button @click="insertMarkdown('# ', '')" title="一级标题">H1</button>
            <button @click="insertMarkdown('## ', '')" title="二级标题">H2</button>
            <button @click="insertMarkdown('### ', '')" title="三级标题">H3</button>
            <div class="toolbar-divider"></div>
            <button @click="insertMarkdown('- ', '')" title="无序列表">• 列表</button>
            <button @click="insertMarkdown('1. ', '')" title="有序列表">1. 列表</button>
            <div class="toolbar-divider"></div>
            <button @click="insertMarkdown('```\n', '\n```')" title="代码块">{ }</button>
            <button @click="insertMarkdown('`', '`')" title="行内代码">`</button>
            <div class="toolbar-divider"></div>
            <button @click="insertMarkdown('> ', '')" title="引用">"</button>
            <button @click="insertMarkdown('![alt text](', ')')" title="图片">🖼️</button>
            <button @click="insertMarkdown('[', '](url)')" title="链接">🔗</button>
          </div>
          <!-- Markdown编辑区域 -->
          <textarea 
            id="content" 
            v-model="note.content" 
            placeholder="输入笔记内容（支持Markdown格式）" 
            class="form-control content-editor markdown-editor" 
            rows="15"
            ref="markdownEditor"
          ></textarea>
        </div>
        
        <!-- 富文本编辑器 -->
        <div v-else>
          <div ref="quillEditor" class="form-control content-editor richtext-editor"></div>
        </div>
      </div>
      
      <div class="form-group">
        <label>标签</label>
        <div class="tags-input">
          <input 
            type="text" 
            v-model="newTag" 
            class="form-control"
            placeholder="输入标签并按Enter"
            @keyup.enter="addTag"
          />
        </div>
        <div class="selected-tags">
          <span 
            v-for="tag in selectedTags" 
            :key="tag.id || tag.name" 
            class="tag"
          >
            {{ tag.name }}
            <button class="tag-remove" @click="removeTag(tag)">&times;</button>
          </span>
        </div>
      </div>
      
      <div class="form-group">
        <label for="is_public">公开笔记</label>
        <input 
          type="checkbox" 
          id="is_public" 
          v-model="note.is_public"
        />
        <span class="checkbox-label">允许其他人查看此笔记</span>
      </div>
      
      <div class="form-actions">
        <button class="btn btn-primary" @click="saveNote" :disabled="isSaving">保存修改</button>
        <button class="btn btn-outline" @click="aiGenerateContent">AI生成</button>
        <button class="btn btn-outline" @click="summarizeContent">AI总结</button>
        <button class="btn btn-outline" @click="suggestTags">AI推荐标签</button>
        <button class="btn btn-outline" @click="exportNote('markdown')">导出Markdown</button>
        <button class="btn btn-outline" @click="exportNote('html')">导出HTML</button>
      </div>
    </div>
    
    <!-- AI生成内容弹窗 -->
    <div v-if="showAiGenerateModal" class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h3>AI生成笔记内容</h3>
          <button class="close-btn" @click="showAiGenerateModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="ai-topic">笔记主题</label>
            <input 
              type="text" 
              id="ai-topic" 
              v-model="aiTopic" 
              class="form-control" 
              placeholder="请输入笔记主题"
              autofocus
            />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showAiGenerateModal = false">取消</button>
          <button class="btn btn-primary" @click="generateAiContent" :disabled="isGenerating">
            {{ isGenerating ? '生成中...' : '生成内容' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { noteService } from '../services/note.js'
import { categoryService } from '../services/category.js'
import { tagService } from '../services/tag.js'
import Quill from 'quill'
import 'quill/dist/quill.snow.css'

const route = useRoute()
const router = useRouter()
const note = ref(null)
const categories = ref([])
const allTags = ref([])
const selectedTags = ref([])
const newTag = ref('')
const isSaving = ref(false)
const isLoading = ref(true)
const error = ref(null)
const quillEditor = ref(null)
const markdownEditor = ref(null)
let quillInstance = null

// AI生成相关变量
const showAiGenerateModal = ref(false)
const aiTopic = ref('')
const isGenerating = ref(false)

onMounted(() => {
  loadNote()
  loadCategories()
  loadTags()
})

// 监听笔记加载完成，初始化编辑器
watch(
  () => note.value,
  (newNote) => {
    if (newNote && newNote.type === 'richtext') {
      // 延迟初始化，确保DOM已更新
      setTimeout(() => {
        initializeQuillEditor()
      }, 0)
    } else {
      // 销毁Quill实例
      if (quillInstance) {
        quillInstance = null
      }
    }
  },
  { deep: true }
)

// 初始化Quill编辑器
function initializeQuillEditor() {
  if (!quillInstance && quillEditor.value && note.value) {
    // 定义Quill工具栏配置
    const toolbarOptions = [
      ['bold', 'italic', 'underline', 'strike'],        // 文本格式
      ['blockquote', 'code-block'],                     // 块格式
      [{ 'header': 1 }, { 'header': 2 }],               // 标题
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],     // 列表
      [{ 'script': 'sub'}, { 'script': 'super' }],      // 上标/下标
      [{ 'indent': '-1'}, { 'indent': '+1' }],          // 缩进
      [{ 'direction': 'rtl' }],                         // 文本方向
      [{ 'size': ['small', false, 'large', 'huge'] }],  // 字体大小
      [{ 'header': [1, 2, 3, 4, 5, 6, false] }],        // 标题级别
      [{ 'color': [] }, { 'background': [] }],          // 文本颜色和背景色
      [{ 'font': [] }],                                 // 字体
      [{ 'align': [] }],                                // 对齐方式
      ['clean']                                         // 清除格式
    ];
    
    // 初始化Quill编辑器
    quillInstance = new Quill(quillEditor.value, {
      theme: 'snow',
      modules: {
        toolbar: toolbarOptions
      },
      placeholder: '开始编写笔记...'
    })
    
    // 设置初始内容
    quillInstance.root.innerHTML = note.value.content || ''
    
    // 监听内容变化，同步到note.content
    quillInstance.on('text-change', () => {
      note.value.content = quillInstance.root.innerHTML
    })
  }
}

async function loadNote() {
  isLoading.value = true
  error.value = null
  try {
    const noteId = route.params.id
    note.value = await noteService.getNote(noteId)
    // 初始化选择的标签
    selectedTags.value = note.value.tags || []
  } catch (error) {
    console.error('加载笔记失败:', error)
    error.value = '加载笔记失败，请检查网络连接或笔记是否存在'
  } finally {
    isLoading.value = false
  }
}

async function loadCategories() {
  try {
    categories.value = await categoryService.getCategories()
  } catch (error) {
    console.error('加载分类失败:', error)
  }
}

async function loadTags() {
  try {
    allTags.value = await tagService.getTags()
  } catch (error) {
    console.error('加载标签失败:', error)
  }
}

function addTag() {
  if (newTag.value.trim()) {
    // 检查是否已存在相同名称的标签
    const existingTag = allTags.value.find(tag => tag.name.toLowerCase() === newTag.value.toLowerCase())
    if (existingTag) {
      // 如果标签已存在，直接使用现有标签
      if (!selectedTags.value.find(tag => tag.id === existingTag.id)) {
        selectedTags.value.push(existingTag)
      }
    } else {
      // 否则添加为新标签（临时ID，后端会生成实际ID）
      selectedTags.value.push({ id: `temp-${Date.now()}`, name: newTag.value.trim() })
    }
    newTag.value = ''
  }
}

function removeTag(tag) {
  selectedTags.value = selectedTags.value.filter(t => t.id !== tag.id)
}

async function saveNote() {
  if (!note.value.content.trim()) {
    alert('内容不能为空')
    return
  }
  
  isSaving.value = true
  try {
    // 分离现有标签ID和新标签名称
    const existingTags = selectedTags.value.filter(tag => tag.id && !tag.id.startsWith('temp-'))
    const newTagNames = selectedTags.value
      .filter(tag => !tag.id || tag.id.startsWith('temp-'))
      .map(tag => tag.name)
      .filter((name, index, self) => self.indexOf(name) === index) // 去重
    
    const noteData = {
      ...note.value,
      tag_ids: existingTags.map(tag => tag.id),
      tags: newTagNames,
      category_id: note.value.category_id || null
    }
    
    await noteService.updateNote(note.value.id, noteData)
    router.push(`/notes/${note.value.id}`)
  } catch (error) {
    console.error('更新笔记失败:', error)
    alert('更新笔记失败')
  } finally {
    isSaving.value = false
  }
}

async function summarizeContent() {
  if (!note.value.content.trim()) {
    alert('请先输入笔记内容')
    return
  }
  
  try {
    const response = await noteService.aiSummarize(note.value.content)
    alert('总结内容: ' + response.summary)
  } catch (error) {
    console.error('AI总结失败:', error)
    alert('AI总结失败')
  }
}

async function suggestTags() {
  if (!note.value.content.trim()) {
    alert('请先输入笔记内容')
    return
  }
  
  try {
    const response = await noteService.aiSuggestTags(note.value.content)
    response.tags.forEach(tagName => {
      const existingTag = allTags.value.find(tag => tag.name === tagName)
      if (existingTag) {
        if (!selectedTags.value.find(tag => tag.id === existingTag.id)) {
          selectedTags.value.push(existingTag)
        }
      } else {
        selectedTags.value.push({ id: `temp-${Date.now()}`, name: tagName })
      }
    })
  } catch (error) {
    console.error('AI推荐标签失败:', error)
    alert('AI推荐标签失败')
  }
}

// 打开AI生成弹窗
function aiGenerateContent() {
  showAiGenerateModal.value = true
  aiTopic.value = ''
}

// 导出笔记
async function exportNote(format) {
  try {
    const response = await noteService.exportNote(note.value.id, format)
    
    // 处理响应数据，创建下载链接
    const blob = new Blob([response.data], { type: response.headers['content-type'] })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${note.value.title || 'untitled'}.${format}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('导出笔记失败:', error)
    alert('导出笔记失败，请重试')
  }
}

// 调用AI生成内容
async function generateAiContent() {
  if (!aiTopic.value.trim()) {
    alert('请输入笔记主题')
    return
  }
  
  isGenerating.value = true
  try {
    const response = await noteService.aiGenerateNote(aiTopic.value)
    
    // 根据当前编辑器类型设置内容
    if (note.value.type === 'richtext') {
      // 富文本编辑器
      if (quillInstance) {
        quillInstance.root.innerHTML = response.content
        note.value.content = response.content
      }
    } else {
      // Markdown编辑器
      note.value.content = response.content
    }
    
    // 如果当前笔记没有标题，使用AI推荐的标题
    if (!note.value.title.trim()) {
      note.value.title = response.suggested_title
    }
    
    showAiGenerateModal.value = false
  } catch (error) {
    console.error('AI生成内容失败:', error)
    alert('AI生成内容失败，请重试')
  } finally {
    isGenerating.value = false
  }
}

// Markdown编辑器工具栏功能
function insertMarkdown(prefix, suffix) {
  const textarea = markdownEditor.value
  if (!textarea) return
  
  const startPos = textarea.selectionStart
  const endPos = textarea.selectionEnd
  const selectedText = textarea.value.substring(startPos, endPos)
  const newText = prefix + selectedText + suffix
  
  note.value.content = textarea.value.substring(0, startPos) + newText + textarea.value.substring(endPos)
  
  // 重新设置焦点并调整光标位置
  setTimeout(() => {
    textarea.focus()
    const newCursorPos = startPos + prefix.length + selectedText.length
    textarea.setSelectionRange(newCursorPos, newCursorPos)
  }, 0)
}
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.actions {
  margin-bottom: 20px;
}

.note-form {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.content-editor {
  resize: vertical;
}

/* Markdown编辑器样式 */
.markdown-editor-container {
  display: flex;
  flex-direction: column;
}

.markdown-toolbar {
  display: flex;
  align-items: center;
  padding: 8px;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-bottom: none;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}

.markdown-toolbar button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  margin: 0 2px;
  padding: 0;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.markdown-toolbar button:hover {
  background-color: #e3f2fd;
  border-color: #2196f3;
}

.toolbar-divider {
  width: 1px;
  height: 20px;
  background-color: #ddd;
  margin: 0 5px;
}

.content-editor.markdown-editor {
  font-family: monospace;
  min-height: 300px;
  border-top-left-radius: 0;
  border-top-right-radius: 0;
}

/* 富文本编辑器容器样式 */
.richtext-editor-container {
  margin-top: 10px;
}

.content-editor.richtext-editor {
  min-height: 300px;
  padding: 0;
  border: none;
}

/* 富文本编辑器样式覆盖 */
.content-editor.richtext-editor .ql-container {
  font-size: 16px;
  min-height: 250px;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  border: 1px solid #ddd;
  border-top: none;
}

.content-editor.richtext-editor .ql-toolbar {
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
  border: 1px solid #ddd;
}

.selected-tags {
  margin-top: 10px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag {
  background-color: #e3f2fd;
  color: #1565c0;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.tag-remove {
  background: none;
  border: none;
  color: #1565c0;
  cursor: pointer;
  font-size: 16px;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.checkbox-label {
  margin-left: 8px;
}

.form-actions {
  margin-top: 30px;
}

.btn {
    margin-right: 10px;
  }
  
  .loading {
    text-align: center;
    padding: 50px 0;
    font-size: 18px;
    color: #666;
  }
  
  .error {
    text-align: center;
    padding: 50px 0;
    font-size: 18px;
    color: #d32f2f;
  }
  
  /* 模态框样式 */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }
  
  .modal {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 20px rgba(0, 0, 0, 0.15);
    width: 90%;
    max-width: 500px;
    max-height: 90vh;
    overflow: hidden;
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    border-bottom: 1px solid #eee;
  }
  
  .modal-header h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
  }
  
  .close-btn {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #999;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: background-color 0.2s;
  }
  
  .close-btn:hover {
    background-color: #f5f5f5;
    color: #333;
  }
  
  .modal-body {
    padding: 20px;
  }
  
  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    padding: 15px 20px;
    border-top: 1px solid #eee;
  }
</style>