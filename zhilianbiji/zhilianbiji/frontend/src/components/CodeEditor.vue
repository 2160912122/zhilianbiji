<template>
  <div class="code-editor-container">
    <div class="editor-header">
      <el-select
        v-model="selectedLanguage"
        class="language-select"
        placeholder="选择语言"
        @change="updateLanguage"
      >
        <el-option label="Python" value="python" />
        <el-option label="JavaScript" value="javascript" />
        <el-option label="Java" value="java" />
        <el-option label="C++" value="cpp" />
        <el-option label="Go" value="go" />
        <el-option label="Rust" value="rust" />
        <el-option label="SQL" value="sql" />
        <el-option label="Plain Text" value="text" />
      </el-select>
      <div class="editor-actions">
        <el-button size="small" @click="copyCode">
          <CopyDocument />
        </el-button>
        <el-button size="small" @click="clearCode">
          <Refresh />
        </el-button>
      </div>
    </div>
    <div ref="editorContainer" class="editor-wrapper"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { EditorState } from '@codemirror/state'
import { EditorView, keymap, lineNumbers, highlightActiveLine, highlightActiveLineGutter } from '@codemirror/view'
import { defaultKeymap, history, historyKeymap } from '@codemirror/commands'
import { python } from '@codemirror/lang-python'
import { javascript } from '@codemirror/lang-javascript'
import { java } from '@codemirror/lang-java'
import { cpp } from '@codemirror/lang-cpp'
import { go } from '@codemirror/lang-go'
import { rust } from '@codemirror/lang-rust'
import { sql } from '@codemirror/lang-sql'
import { oneDark } from '@codemirror/theme-one-dark'
import { syntaxHighlighting, HighlightStyle } from '@codemirror/language'
import { tags } from '@lezer/highlight'
import { CopyDocument, Refresh } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  language: {
    type: String,
    default: 'python'
  }
})

const emit = defineEmits(['update:modelValue'])

const editorContainer = ref(null)
const selectedLanguage = ref(props.language)
let editorView = null

const customHighlightStyle = HighlightStyle.define([
  { tag: tags.keyword, color: '#c678dd' },
  { tag: tags.operator, color: '#56b6c2' },
  { tag: tags.string, color: '#98c379' },
  { tag: tags.number, color: '#d19a66' },
  { tag: tags.boolean, color: '#d19a66' },
  { tag: tags.function(tags.variableName), color: '#61afef' },
  { tag: tags.function(tags.propertyName), color: '#61afef' },
  { tag: tags.className, color: '#e6c07b' },
  { tag: tags.definition(tags.typeName), color: '#e6c07b' },
  { tag: tags.comment, color: '#5c6370', fontStyle: 'italic' },
  { tag: tags.meta, color: '#646695' },
  { tag: tags.invalid, color: '#e06c75' }
])

const getLanguageExtension = (lang) => {
  const languages = {
    python: python(),
    javascript: javascript(),
    java: java(),
    cpp: cpp(),
    go: go(),
    rust: rust(),
    sql: sql()
  }
  return languages[lang] || []
}

const createEditor = () => {
  if (!editorContainer.value) return

  const extensions = [
    lineNumbers(),
    highlightActiveLine(),
    highlightActiveLineGutter(),
    history(),
    getLanguageExtension(selectedLanguage.value),
    syntaxHighlighting(customHighlightStyle, { fallback: true }),
    oneDark,
    keymap.of([...defaultKeymap, ...historyKeymap]),
    EditorView.updateListener.of((update) => {
      if (update.docChanged) {
        emit('update:modelValue', update.state.doc.toString())
      }
    }),
    EditorView.theme({
      '&': { height: '100%', fontSize: '14px' },
      '.cm-content': { padding: '10px' },
      '.cm-line': { padding: '0 4px' },
      '.cm-gutters': { backgroundColor: '#21252b', borderRight: '1px solid #3b3f4c' },
      '.cm-activeLine': { backgroundColor: '#2c313a' },
      '.cm-activeLineGutter': { backgroundColor: '#2c313a' },
      '.cm-cursor': { borderLeftColor: '#56b6c2' }
    })
  ]

  const state = EditorState.create({
    doc: props.modelValue,
    extensions
  })

  editorView = new EditorView({
    state,
    parent: editorContainer.value
  })
}

const updateLanguage = () => {
  if (!editorView) return

  const newExtensions = [
    lineNumbers(),
    highlightActiveLine(),
    highlightActiveLineGutter(),
    history(),
    getLanguageExtension(selectedLanguage.value),
    syntaxHighlighting(customHighlightStyle, { fallback: true }),
    oneDark,
    keymap.of([...defaultKeymap, ...historyKeymap]),
    EditorView.updateListener.of((update) => {
      if (update.docChanged) {
        emit('update:modelValue', update.state.doc.toString())
      }
    }),
    EditorView.theme({
      '&': { height: '100%', fontSize: '14px' },
      '.cm-content': { padding: '10px' },
      '.cm-line': { padding: '0 4px' },
      '.cm-gutters': { backgroundColor: '#21252b', borderRight: '1px solid #3b3f4c' },
      '.cm-activeLine': { backgroundColor: '#2c313a' },
      '.cm-activeLineGutter': { backgroundColor: '#2c313a' },
      '.cm-cursor': { borderLeftColor: '#56b6c2' }
    })
  ]

  const newState = EditorState.create({
    doc: editorView.state.doc.toString(),
    extensions: newExtensions
  })

  editorView.dispatch({
    state: newState
  })
}

const copyCode = async () => {
  if (editorView) {
    const code = editorView.state.doc.toString()
    try {
      await navigator.clipboard.writeText(code)
      ElMessage.success('代码已复制')
    } catch (err) {
      ElMessage.error('复制失败')
    }
  }
}

const clearCode = () => {
  if (editorView) {
    editorView.dispatch({
      changes: {
        from: 0,
        to: editorView.state.doc.length,
        insert: ''
      }
    })
  }
}

watch(() => props.modelValue, (newValue) => {
  if (editorView && newValue !== editorView.state.doc.toString()) {
    editorView.dispatch({
      changes: {
        from: 0,
        to: editorView.state.doc.length,
        insert: newValue
      }
    })
  }
})

watch(() => props.language, (newLang) => {
  selectedLanguage.value = newLang
  updateLanguage()
})

onMounted(() => {
  createEditor()
})
</script>

<style scoped>
.code-editor-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  overflow: hidden;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #21252b;
  border-bottom: 1px solid #3b3f4c;
}

.language-select {
  width: 120px;
}

.editor-actions {
  display: flex;
  gap: 8px;
}

.editor-wrapper {
  flex: 1;
  min-height: 300px;
}
</style>