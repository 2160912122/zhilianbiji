<template>
  <div class="ai-assistant">
    <div class="ai-header">
      <div class="header-left">
        <h3>AI助手</h3>
        <span class="model-tag">Doubao-Seed-2.0-pro</span>
      </div>
      <el-button
        link
        size="small"
        @click="$emit('close')"
      >
        <el-icon><Close /></el-icon>
      </el-button>
    </div>
    <div class="ai-content">
      <div class="ai-messages">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['ai-message', message.type]"
        >
          <div class="message-avatar">
            <el-icon v-if="message.type === 'user'">
              <UserFilled />
            </el-icon>
            <el-icon v-else>
              <ChatDotRound />
            </el-icon>
          </div>
          <div class="message-content">
            {{ message.content }}
            <img v-if="message.image" :src="message.image" class="message-image" alt="Generated image" />
            <div v-if="message.file" class="message-file">
              <el-icon><Document /></el-icon>
              <span>{{ message.file.name }}</span>
            </div>
          </div>
        </div>
      </div>
      <div class="ai-input-area">
        <el-input
          v-model="inputMessage"
          placeholder="请输入您的问题..."
          @keyup.enter="sendMessage"
          clearable
        >
          <template #prefix>
            <div class="upload-dropdown">
              <el-dropdown @command="handleUploadCommand" trigger="click" teleport="body" :popper-options="{ placement: 'bottom-start', modifiers: [{ name: 'preventOverflow', options: { boundary: 'viewport' } }] }">
                <el-button type="default">
                  <el-icon><Upload /></el-icon>
                  <span class="upload-text">上传</span>
                  <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="upload-image">
                      <el-icon><Picture /></el-icon>
                      <span>上传图片</span>
                    </el-dropdown-item>
                    <el-dropdown-item command="upload-file">
                      <el-icon><Document /></el-icon>
                      <span>上传文件</span>
                    </el-dropdown-item>
                    <el-dropdown-item command="upload-video">
                      <el-icon><VideoCamera /></el-icon>
                      <span>上传视频</span>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
          <template #append>
            <el-button
              type="primary"
              @click="sendMessage"
              :disabled="!inputMessage.trim() || isLoading"
              :loading="isLoading"
            >
              发送
            </el-button>
          </template>
        </el-input>
        
        <!-- 文件上传区域 -->
        <div v-if="showFileUpload" class="upload-area">
          <el-upload
            class="file-upload"
            action=""
            :auto-upload="false"
            :on-change="handleFileChange"
            accept=".pdf,.doc,.docx,.txt"
          >
            <el-button type="default">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持上传 PDF、Word、TXT 文件
              </div>
            </template>
          </el-upload>
          <el-button
            v-if="selectedFile"
            type="success"
            @click="analyzeDocument"
            :loading="isLoading"
          >
            分析文档
          </el-button>
        </div>
        

        
        <!-- 图片上传区域 -->
        <div v-if="showImageUpload" class="upload-area">
          <el-upload
            class="file-upload"
            action=""
            :auto-upload="false"
            :on-change="handleImageChange"
            accept=".jpg,.jpeg,.png,.gif,.webp"
          >
            <el-button type="default">选择图片</el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持上传 JPG、JPEG、PNG、GIF、WebP 图片
              </div>
            </template>
          </el-upload>
          <el-button
            v-if="selectedImage"
            type="success"
            @click="analyzeImage"
            :loading="isLoading"
          >
            分析图片
          </el-button>
        </div>
        
        <!-- 视频上传区域 -->
        <div v-if="showVideoUpload" class="upload-area">
          <el-upload
            class="file-upload"
            action=""
            :auto-upload="false"
            :on-change="handleVideoChange"
            accept=".mp4,.mov,.avi,.wmv,.flv,.mkv"
          >
            <el-button type="default">选择视频</el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持上传 MP4、MOV、AVI、WMV、FLV、MKV 视频
              </div>
            </template>
          </el-upload>
          <el-button
            v-if="selectedVideo"
            type="success"
            @click="analyzeVideo"
            :loading="isLoading"
          >
            分析视频
          </el-button>
        </div>
        

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Close, UserFilled, ChatDotRound, Upload, Picture, Document, Camera, VideoCamera } from '@element-plus/icons-vue'
import { aiAPI } from '@/api/ai'
import { ElMessage } from 'element-plus'
import { useAIStore } from '@/store/ai'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  action: {
    type: String,
    default: null
  }
})

// 初始化AI store
const aiStore = useAIStore()
const emit = defineEmits(['close', 'action-completed'])

const messages = ref([
  {
    type: 'ai',
    content: '您好！我是基于Doubao-Seed-2.0-pro模型的AI助手，有什么可以帮助您的吗？'
  }
])

// 定义响应式变量
const inputMessage = ref('')
const isLoading = ref(false)
const showFileUpload = ref(false)
const showImageUpload = ref(false)
const showVideoUpload = ref(false)
const selectedFile = ref(null)
const selectedImage = ref(null)
const selectedVideo = ref(null)

// 监听action属性变化
watch(() => props.action, (newAction) => {
  try {
    // 处理undefined和null的情况
    if (newAction) {
      // 重置所有功能区域状态
      showFileUpload.value = false
      showImageUpload.value = false
      selectedFile.value = null
      selectedImage.value = null
      
      // 根据action打开相应的功能区域
      if (newAction === 'upload-file') {
        showFileUpload.value = true
      } else if (newAction === 'upload-image') {
        showImageUpload.value = true
      } else if (newAction === 'upload-video') {
        showVideoUpload.value = true
      }
      
      // 触发action完成事件
      setTimeout(() => {
        emit('action-completed')
      }, 500)
    }
  } catch (error) {
    console.error('Error in action watcher:', error)
  }
})

const sendMessage = async () => {
    if (!inputMessage.value.trim()) return
    
    // 添加用户消息
    messages.value.push({
      type: 'user',
      content: inputMessage.value
    })
    
    const userMessage = inputMessage.value
    inputMessage.value = ''
    
    // 调用AI接口获取回复
    isLoading.value = true
    try {
      // 转换消息格式为AI API要求的格式
      const aiMessages = messages.value.map(msg => ({
        role: msg.type === 'user' ? 'user' : 'assistant',
        content: msg.content
      }))
      
      console.log('发送Doubao AI请求:', aiMessages)
      const response = await aiAPI.chatDoubao(aiMessages)
      console.log('收到Doubao AI响应:', response)
      
      if (response.code === 200) {
        // 添加AI回复
        messages.value.push({
          type: 'ai',
          content: response.data.content
        })
        
        // 将AI生成的内容设置到store中，以便NoteEditor可以使用
        aiStore.setGeneratedContent(response.data.content)
      } else {
        ElMessage.error(response.message || 'AI回复失败')
      }
    } catch (error) {
      console.error('AI请求错误:', error)
      ElMessage.error('服务器错误，请稍后重试')
    } finally {
      isLoading.value = false
    }
  }

const toggleFileUpload = () => {
  showFileUpload.value = !showFileUpload.value
  // 切换时重置状态
  if (!showFileUpload.value) {
    selectedFile.value = null
  }
  console.log('文件上传区域状态:', showFileUpload.value)
}



const toggleImageUpload = () => {
  showImageUpload.value = !showImageUpload.value
  // 切换时重置状态
  if (!showImageUpload.value) {
    selectedImage.value = null
  }
  // 确保文件上传区域关闭
  showFileUpload.value = false
  selectedFile.value = null
  console.log('图片上传区域状态:', showImageUpload.value)
}

const handleUploadCommand = (command) => {
  // 重置所有上传区域状态
  showFileUpload.value = false
  showImageUpload.value = false
  showVideoUpload.value = false
  selectedFile.value = null
  selectedImage.value = null
  selectedVideo.value = null
  
  // 根据命令打开相应的上传区域
  if (command === 'upload-image') {
    showImageUpload.value = true
  } else if (command === 'upload-file') {
    showFileUpload.value = true
  } else if (command === 'upload-video') {
    showVideoUpload.value = true
  }
  
  console.log('处理上传命令:', command)
}

const handleImageChange = (file) => {
  selectedImage.value = file.raw
  ElMessage.success(`已选择图片: ${file.name}`)
  console.log('选择的图片:', selectedImage.value)
}

const analyzeImage = async () => {
  if (!selectedImage.value) {
    ElMessage.warning('请先选择图片')
    return
  }
  
  console.log('开始分析图片:', selectedImage.value)
  
  // 添加用户消息
  messages.value.push({
    type: 'user',
    content: `请分析以下图片: ${selectedImage.value.name}`,
    image: URL.createObjectURL(selectedImage.value)
  })
  
  isLoading.value = true
  try {
    console.log('开始上传图片:', selectedImage.value.name)
    // 先上传图片
    const uploadResponse = await aiAPI.uploadFile(selectedImage.value)
    console.log('图片上传响应:', uploadResponse)
    
    if (uploadResponse.code === 200) {
      console.log('图片上传成功，开始分析:', uploadResponse.data.file_path)
      // 然后调用图片分析接口
      const analyzeResponse = await aiAPI.analyzeImage(uploadResponse.data.file_path)
      console.log('图片分析响应:', analyzeResponse)
      
      if (analyzeResponse.code === 200) {
        console.log('图片分析成功，添加回复')
        messages.value.push({
          type: 'ai',
          content: analyzeResponse.data.content
        })
      } else {
        console.log('图片分析失败:', analyzeResponse.message)
        ElMessage.error(analyzeResponse.message || '图片分析失败')
      }
    } else {
      console.log('图片上传失败:', uploadResponse.message)
      ElMessage.error(uploadResponse.message || '图片上传失败')
    }
  } catch (error) {
    console.error('图片分析错误:', error)
    ElMessage.error('服务器错误，请稍后重试')
  } finally {
    console.log('图片分析完成，重置状态')
    isLoading.value = false
    showImageUpload.value = false
    selectedImage.value = null
  }
}

const handleFileChange = (file) => {
  selectedFile.value = file.raw
  ElMessage.success(`已选择文件: ${file.name}`)
  console.log('选择的文件:', selectedFile.value)
}

const analyzeDocument = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  console.log('开始分析文档:', selectedFile.value)
  
  // 添加用户消息
  messages.value.push({
    type: 'user',
    content: `请分析以下文档: ${selectedFile.value.name}`,
    file: {
      name: selectedFile.value.name
    }
  })
  
  isLoading.value = true
  try {
    console.log('开始上传文件:', selectedFile.value.name)
    // 先上传文件
    const uploadResponse = await aiAPI.uploadFile(selectedFile.value)
    console.log('文件上传响应:', uploadResponse)
    
    if (uploadResponse.code === 200) {
      console.log('文件上传成功，开始分析:', uploadResponse.data.file_path)
      // 然后调用文档分析接口
      const analyzeResponse = await aiAPI.analyzeDocument(uploadResponse.data.file_path)
      console.log('文档分析响应:', analyzeResponse)
      
      if (analyzeResponse.code === 200) {
        console.log('文档分析成功，添加回复')
        messages.value.push({
          type: 'ai',
          content: analyzeResponse.data.content
        })
      } else {
        console.log('文档分析失败:', analyzeResponse.message)
        ElMessage.error(analyzeResponse.message || '文档分析失败')
      }
    } else {
      console.log('文件上传失败:', uploadResponse.message)
      ElMessage.error(uploadResponse.message || '文件上传失败')
    }
  } catch (error) {
    console.error('文档分析错误:', error)
    ElMessage.error('服务器错误，请稍后重试')
  } finally {
    console.log('文档分析完成，重置状态')
    isLoading.value = false
    showFileUpload.value = false
    selectedFile.value = null
  }
}

const handleVideoChange = (file) => {
  selectedVideo.value = file.raw
  ElMessage.success(`已选择视频: ${file.name}`)
  console.log('选择的视频:', selectedVideo.value)
}

const analyzeVideo = async () => {
  if (!selectedVideo.value) {
    ElMessage.warning('请先选择视频')
    return
  }
  
  console.log('开始分析视频:', selectedVideo.value)
  
  // 添加用户消息
  messages.value.push({
    type: 'user',
    content: `请分析以下视频: ${selectedVideo.value.name}`,
    file: {
      name: selectedVideo.value.name
    }
  })
  
  isLoading.value = true
  try {
    console.log('开始上传视频:', selectedVideo.value.name)
    // 先上传视频
    const uploadResponse = await aiAPI.uploadFile(selectedVideo.value)
    console.log('视频上传响应:', uploadResponse)
    
    if (uploadResponse.code === 200) {
      console.log('视频上传成功，开始分析:', uploadResponse.data.file_path)
      // 然后调用视频分析接口
      const analyzeResponse = await aiAPI.analyzeVideo(uploadResponse.data.file_path)
      console.log('视频分析响应:', analyzeResponse)
      
      if (analyzeResponse.code === 200) {
        console.log('视频分析成功，添加回复')
        const analysisContent = analyzeResponse.data.content
        messages.value.push({
          type: 'ai',
          content: analysisContent
        })
      } else {
        console.log('视频分析失败:', analyzeResponse.message)
        ElMessage.error(analyzeResponse.message || '视频分析失败')
      }
    } else {
      console.log('视频上传失败:', uploadResponse.message)
      ElMessage.error(uploadResponse.message || '视频上传失败')
    }
  } catch (error) {
    console.error('视频分析错误:', error)
    ElMessage.error('服务器错误，请稍后重试')
  } finally {
    console.log('视频分析完成，重置状态')
    isLoading.value = false
    showVideoUpload.value = false
    selectedVideo.value = null
  }
}


</script>

<style scoped>
.ai-assistant {
  width: 100%;
  height: 100%;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.ai-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
  font-size: 16px;
  font-weight: 600;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.model-tag {
  font-size: 12px;
  padding: 2px 8px;
  background-color: #ecf5ff;
  color: #409eff;
  border-radius: 10px;
  font-weight: normal;
}

.ai-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: 16px;
  overflow: visible !important;

}

.ai-messages {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 800px; /* 增大聊天记录区域的高度 */
}

.ai-message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.ai-message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ai-message.ai .message-avatar {
  background-color: #ecf5ff;
  color: #409eff;
}

.ai-message.user .message-avatar {
  background-color: #f0f9eb;
  color: #67c23a;
}

.message-content {
  max-width: 90%; /* 增大消息内容的最大宽度 */
  padding: 16px 20px; /* 增大消息内容的内边距 */
  border-radius: 12px;
  line-height: 1.6;
  font-size: 16px; /* 增大字体大小 */
}

.ai-message.ai .message-content {
  background-color: #ecf5ff;
  color: #333;
  border-radius: 0 12px 12px 12px;
}

.ai-message.user .message-content {
  background-color: #f0f9eb;
  color: #333;
  border-radius: 12px 0 12px 12px;
}

.ai-input-area {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;

}

.ai-input-area .el-input {
  border-radius: 20px;
  border: 1px solid #dee2e6;
  transition: all 0.3s ease;
  background-color: #ffffff;
}

.ai-input-area .el-input:hover:not(:focus) {
  border-color: #ced4da;
  box-shadow: none;
}

.ai-input-area .el-input:focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.ai-input-area .el-input__prefix {
  padding-left: 12px;
}

.ai-input-area .el-input__suffix {
  padding-right: 8px;
}

.ai-input-area .el-button {
  border-radius: 20px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.ai-input-area .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

/* 修复下拉菜单被挡住的问题 */
.upload-dropdown {
  position: relative;
  z-index: 9999;
  display: inline-block;
}

/* 确保下拉菜单显示在最上层 */
.el-dropdown-menu {
  border-radius: 12px !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
  border: none !important;
  overflow: hidden !important;
  z-index: 9999 !important;
  margin-top: 8px !important;
  background-color: #ffffff !important;
  min-width: 150px !important;
}

/* 确保AI助手容器不会创建新的层叠上下文 */
.ai-assistant {
  position: relative;
  z-index: auto;
}

/* 确保输入框区域不会限制下拉菜单显示 */
.ai-input-area {
  position: relative;
  z-index: 1;
  overflow: visible !important;
}

.ai-input-area .el-dropdown-item {
  padding: 8px 16px;
  transition: all 0.2s ease;
  height: 36px;
  line-height: 18px;
}

.ai-input-area .el-dropdown-item:hover {
  background-color: #ecf5ff;
  color: #409eff;
}

.ai-input-area .el-dropdown-item i {
  margin-right: 8px;
  font-size: 16px;
}

.upload-text {
  margin-left: 4px;
  font-size: 14px;
}

.upload-area {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 6px;
}

.file-upload {
  flex: 1;
}

.image-generation-area {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 6px;
}

.image-generation-area .el-input {
  flex: 1;
}

.message-image {
  max-width: 100%;
  max-height: 400px; /* 增大图像的最大高度 */
  border-radius: 8px;
  margin-top: 12px;
}

.message-file {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding: 6px 12px;
  background-color: #f0f9eb;
  border-radius: 6px;
  font-size: 14px;
  color: #67c23a;
}
</style>
