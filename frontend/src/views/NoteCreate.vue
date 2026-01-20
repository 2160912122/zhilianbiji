<template>
  <div class="container">
    <h1>创建笔记</h1>
    <div class="actions">
      <router-link to="/notes" class="btn btn-secondary">返回列表</router-link>
    </div>
    
    <div class="note-form">
      <form @submit.prevent="saveNote">
        <div class="form-group">
          <label for="title">标题</label>
          <input 
            type="text" 
            id="title" 
            v-model="note.title" 
            class="form-control"
            placeholder="输入笔记标题（可选，不填将自动生成）"
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
          <button class="btn btn-primary" @click="saveNote" :disabled="isSaving">保存笔记</button>
          <button class="btn btn-outline" @click="generateWithAI">AI生成内容</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { noteService } from '../services/note.js'
import { categoryService } from '../services/category.js'
import { tagService } from '../services/tag.js'
import Quill from 'quill'
import 'quill/dist/quill.snow.css'

const router = useRouter()
const route = useRoute()

// 从路由参数或查询参数获取笔记类型
const noteType = route.params.type || route.query.type || 'markdown'

const note = ref({
  title: '',
  content: '',
  type: noteType,
  category_id: null,
  is_public: false
})
const categories = ref([])
const allTags = ref([])
const selectedTags = ref([])
const newTag = ref('')
const isSaving = ref(false)
const quillEditor = ref(null)
const markdownEditor = ref(null)
let quillInstance = null

// 初始化Quill编辑器
onMounted(() => {
  loadCategories()
  loadTags()
  
  if (note.value.type === 'richtext') {
    initializeQuillEditor()
  }
})

// 监听笔记类型变化，初始化或销毁编辑器
watch(() => note.value.type, (newType) => {
  if (newType === 'richtext') {
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
})

// 初始化Quill编辑器
function initializeQuillEditor() {
  if (!quillInstance && quillEditor.value) {
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
    
    // 如果已有内容，设置到编辑器中
    if (note.value.content) {
      quillInstance.root.innerHTML = note.value.content
    }
    
    // 监听内容变化，同步到note.content
    quillInstance.on('text-change', () => {
      note.value.content = quillInstance.root.innerHTML
    })
  }
}

onMounted(() => {
  loadCategories()
  loadTags()
})

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
    const noteData = {
      ...note.value,
      category_id: note.value.category_id || null
    }
    
    // 分离已存在的标签和新标签
    const existingTags = selectedTags.value.filter(tag => !tag.id.toString().startsWith('temp-'))
    const newTags = selectedTags.value.filter(tag => tag.id.toString().startsWith('temp-'))
    
    if (existingTags.length > 0) {
      noteData.tag_ids = existingTags.map(tag => tag.id)
    }
    
    if (newTags.length > 0) {
      noteData.tags = newTags.map(tag => tag.name)
    }
    
    const response = await noteService.createNote(noteData)
    router.push(`/notes/${response.id}`)
  } catch (error) {
    console.error('创建笔记失败:', error)
    alert('创建笔记失败')
  } finally {
    isSaving.value = false
  }
}

async function generateWithAI() {
  const topic = prompt('请输入你想要生成笔记的主题:')
  if (topic) {
    try {
      const response = await noteService.aiGenerateNote(topic)
      note.value.title = response.suggested_title || topic
      note.value.content = response.content
      
      // 如果生成了标签，添加到选择的标签中
      if (response.tags) {
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
      }
    } catch (error) {
      console.error('AI生成笔记失败:', error)
      alert('AI生成笔记失败')
    }
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
</style>