<template>
  <div class="ai-module-container">
    <!-- AI功能下拉菜单 -->
    <div
      v-if="showMenu"
      class="ai-function-menu"
      :class="{ 'show': showMenu }"
    >
      <div class="menu-title">AI功能</div>
      <div v-for="(func, index) in aiFunctions" :key="index" class="menu-item" @click="handleFunctionSelect(func)">
        <el-icon class="item-icon"><component :is="func.icon" /></el-icon>
        <span class="item-text">{{ func.label }}</span>
      </div>
    </div>

    <!-- AI聊天面板 -->
    <div
      v-if="showChatPanel"
      class="ai-chat-panel"
      :class="{ 'show': showChatPanel }"
    >
      <AIAssistant @close="showChatPanel = false" />
    </div>
    
    <!-- AI模块按钮 -->
    <el-button
      class="ai-module-btn"
      type="primary"
      @click="toggleMenu"
      :icon="ChatDotRound"
    >
      AI助手
    </el-button>
  </div>
</template>

<script setup>
import { ref, markRaw } from 'vue'
import { 
  ChatDotRound, 
  Document, 
  CollectionTag, 
  Grid, 
  DataAnalysis, 
  Connection, 
  DocumentCopy, 
  Link 
} from '@element-plus/icons-vue'
import AIAssistant from './AIAssistant.vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { useRouter } from 'vue-router'
import { useAIStore } from '@/store/ai'
import { aiAPI } from '@/api/ai'

const router = useRouter()
const aiStore = useAIStore()

const showMenu = ref(false)
const showChatPanel = ref(false)

// AI功能列表
const aiFunctions = ref([
  { label: '生成笔记', icon: markRaw(Document), type: 'note' },
  { label: '生成白板', icon: markRaw(CollectionTag), type: 'whiteboard' },
  { label: '生成表格', icon: markRaw(Grid), type: 'table' },
  { label: '生成脑图', icon: markRaw(DataAnalysis), type: 'mindmap' },
  { label: '生成流程图', icon: markRaw(Connection), type: 'flowchart' },
  { label: '总结', icon: markRaw(DocumentCopy), type: 'summary' },
  { label: '翻译', icon: markRaw(Link), type: 'translate' },
  { label: 'AI聊天', icon: markRaw(ChatDotRound), type: 'chat' }
])

const toggleMenu = () => {
  showMenu.value = !showMenu.value
  // 如果菜单打开，关闭聊天面板
  if (showMenu.value) {
    showChatPanel.value = false
  }
}

const handleFunctionSelect = (func) => {
  showMenu.value = false
  
  switch (func.type) {
    case 'note':
      ElMessageBox.prompt('请输入笔记主题', '生成笔记', {
        confirmButtonText: '生成',
        cancelButtonText: '取消',
        inputPattern: /^[\s\S]{1,100}$/,
        inputErrorMessage: '主题长度不能超过100个字符'
      }).then(async ({ value }) => {
        // 显示全屏加载指示器
        const loadingInstance = ElLoading.service({
          lock: true,
          text: '正在生成笔记内容，请稍候...',
          background: 'rgba(0, 0, 0, 0.7)'
        })
        
        try {
          // 调用AI API生成内容
          const aiMessages = [
            { role: 'system', content: '请根据用户提供的主题生成一篇详细的笔记内容，内容要丰富、结构清晰。' },
            { role: 'user', content: value }
          ]
          const response = await aiAPI.chat(aiMessages)
          
          if (response.code === 200) {
            // 先设置AI生成的内容
            aiStore.setGeneratedContent(response.data.content)
            
            // 然后导航到新页面
            ElMessage.success('笔记内容生成成功，正在进入编辑器...')
            router.push('/notes/new')
          } else {
            ElMessage.error(response.message || '生成内容失败')
          }
        } catch (error) {
          console.error('AI生成内容失败:', error)
          ElMessage.error('AI生成内容失败，请稍后重试')
        } finally {
          // 无论成功失败，都要关闭加载指示器
          loadingInstance.close()
        }
      }).catch(() => {
        // 用户取消输入
      })
      break
    case 'whiteboard':
      ElMessageBox.prompt('请输入白板主题', '生成白板', {
        confirmButtonText: '生成',
        cancelButtonText: '取消',
        inputPattern: /^[\s\S]{1,100}$/,
        inputErrorMessage: '主题长度不能超过100个字符'
      }).then(async ({ value }) => {
        // 显示全屏加载指示器
        const loadingInstance = ElLoading.service({
          lock: true,
          text: '正在生成白板内容，请稍候...',
          background: 'rgba(0, 0, 0, 0.7)'
        })
        
        try {
          // 调用AI API生成内容
          const aiMessages = [
            { role: 'system', content: '请根据用户提供的主题生成适合白板展示的内容，包括大纲、要点、图表建议等，内容要清晰简洁。' },
            { role: 'user', content: value }
          ]
          const response = await aiAPI.chat(aiMessages)
          
          if (response.code === 200) {
            // 先设置AI生成的内容
            aiStore.setGeneratedContent(response.data.content)
            
            // 然后导航到新页面
            ElMessage.success('白板内容生成成功，正在进入编辑器...')
            router.push('/whiteboards/new')
          } else {
            ElMessage.error(response.message || '生成内容失败')
          }
        } catch (error) {
          console.error('AI生成内容失败:', error)
          ElMessage.error('AI生成内容失败，请稍后重试')
        } finally {
          // 无论成功失败，都要关闭加载指示器
          loadingInstance.close()
        }
      }).catch(() => {
        // 用户取消输入
      })
      break
    case 'table':
      ElMessageBox.prompt('请输入表格主题', '生成表格', {
        confirmButtonText: '生成',
        cancelButtonText: '取消',
        inputPattern: /^[\s\S]{1,100}$/,
        inputErrorMessage: '主题长度不能超过100个字符'
      }).then(async ({ value }) => {
        // 显示全屏加载指示器
        const loadingInstance = ElLoading.service({
          lock: true,
          text: '正在生成表格内容，请稍候...',
          background: 'rgba(0, 0, 0, 0.7)'
        })
        
        try {
          // 调用AI API生成内容
          const aiMessages = [
            { role: 'system', content: '请根据用户提供的主题生成表格内容，返回JSON格式，包含columns和rows字段。columns字段是列标题数组，rows字段是数据行数组。' },
            { role: 'user', content: value }
          ]
          const response = await aiAPI.chat(aiMessages)
          
          if (response.code === 200) {
            // 先设置AI生成的内容
            aiStore.setGeneratedContent(response.data.content)
            
            // 然后导航到新页面
            ElMessage.success('表格内容生成成功，正在进入编辑器...')
            router.push('/tables/new')
          } else {
            ElMessage.error(response.message || '生成内容失败')
          }
        } catch (error) {
          console.error('AI生成内容失败:', error)
          ElMessage.error('AI生成内容失败，请稍后重试')
        } finally {
          // 无论成功失败，都要关闭加载指示器
          loadingInstance.close()
        }
      }).catch(() => {
        // 用户取消输入
      })
      break
    case 'mindmap':
      ElMessageBox.prompt('请输入脑图主题', '生成脑图', {
        confirmButtonText: '生成',
        cancelButtonText: '取消',
        inputPattern: /^[\s\S]{1,100}$/,
        inputErrorMessage: '主题长度不能超过100个字符'
      }).then(async ({ value }) => {
        // 显示全屏加载指示器
        const loadingInstance = ElLoading.service({
          lock: true,
          text: '正在生成脑图内容，请稍候...',
          background: 'rgba(0, 0, 0, 0.7)'
        })
        
        try {
          // 调用AI API生成内容
          const aiMessages = [
            { role: 'system', content: '请根据用户提供的主题生成脑图内容，返回JSON格式，包含nodes和edges字段。nodes字段是节点数组，每个节点包含id、label和position属性；edges字段是边数组，每个边包含from和to属性。' },
            { role: 'user', content: value }
          ]
          const response = await aiAPI.chat(aiMessages)
          
          if (response.code === 200) {
            // 先设置AI生成的内容
            aiStore.setGeneratedContent(response.data.content)
            
            // 然后导航到新页面
            ElMessage.success('脑图内容生成成功，正在进入编辑器...')
            router.push('/mindmaps/new')
          } else {
            ElMessage.error(response.message || '生成内容失败')
          }
        } catch (error) {
          console.error('AI生成内容失败:', error)
          ElMessage.error('AI生成内容失败，请稍后重试')
        } finally {
          // 无论成功失败，都要关闭加载指示器
          loadingInstance.close()
        }
      }).catch(() => {
        // 用户取消输入
      })
      break
    case 'flowchart':
      ElMessageBox.prompt('请输入流程图主题', '生成流程图', {
        confirmButtonText: '生成',
        cancelButtonText: '取消',
        inputPattern: /^[\s\S]{1,100}$/,
        inputErrorMessage: '主题长度不能超过100个字符'
      }).then(async ({ value }) => {
        // 显示全屏加载指示器
        const loadingInstance = ElLoading.service({
          lock: true,
          text: '正在生成流程图内容，请稍候...',
          background: 'rgba(0, 0, 0, 0.7)'
        })
        
        try {
          // 调用AI API生成内容
          const aiMessages = [
            { role: 'system', content: '请根据用户提供的主题生成流程图内容，返回JSON格式，包含nodes和edges字段。nodes字段是对象，键为节点ID，值为节点对象，每个节点对象包含id、text、type、x和y属性，其中type属性表示节点类型（circle表示开始/结束节点，rect表示处理节点，diamond表示判断节点）；edges字段是对象，键为边ID，值为边对象，每个边对象包含id、source、target、type和text属性，其中text属性表示边的标签（如"是"、"否"）。请确保生成有意义的节点文本、正确的节点类型和合理的连接线，逻辑顺序正确。' },
            { role: 'user', content: value }
          ]
          const response = await aiAPI.chat(aiMessages)
          
          if (response.code === 200) {
            // 先设置AI生成的内容
            aiStore.setGeneratedContent(response.data.content)
            
            // 然后导航到新页面
            ElMessage.success('流程图内容生成成功，正在进入编辑器...')
            router.push('/flowcharts/new')
          } else {
            ElMessage.error(response.message || '生成内容失败')
          }
        } catch (error) {
          console.error('AI生成内容失败:', error)
          ElMessage.error('AI生成内容失败，请稍后重试')
        } finally {
          // 无论成功失败，都要关闭加载指示器
          loadingInstance.close()
        }
      }).catch(() => {
        // 用户取消输入
      })
      break
    case 'summary':
    case 'translate':
      // 对于总结和翻译功能，直接打开聊天面板
      showChatPanel.value = true
      // 可以在这里设置初始提示，根据功能类型
      break
    case 'chat':
      showChatPanel.value = true
      break
    default:
      ElMessage.warning('功能开发中')
  }
}
</script>

<style scoped>
.ai-module-container {
  position: relative;
  display: inline-block;
}

.ai-function-menu {
  position: absolute;
  top: 100%;
  right: 0;
  width: 220px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-top: 5px;
  z-index: 1000;
  transform: translateY(-10px);
  opacity: 0;
  transition: all 0.3s ease;
  overflow: hidden;
}

.ai-function-menu.show {
  transform: translateY(0);
  opacity: 1;
}

.menu-title {
  padding: 12px 16px;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #ebeef5;
  background-color: #f5f7fa;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.menu-item:hover {
  background-color: #f5f7fa;
}

.item-icon {
  margin-right: 12px;
  color: #606266;
  font-size: 18px;
}

.item-text {
  font-size: 14px;
  color: #303133;
}

.ai-chat-panel {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 360px;
  height: 500px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  transform: translateY(100%);
  opacity: 0;
  transition: all 0.3s ease;
  overflow: hidden;
  z-index: 9999;
}

.ai-chat-panel.show {
  transform: translateY(0);
  opacity: 1;
}

.ai-module-btn {
  display: flex;
  align-items: center;
  gap: 5px;
}
</style>