<template>
  <div class="voice-recorder">
    <el-button
      :type="isRecording ? 'danger' : 'primary'"
      :icon="isRecording ? Close : Mic"
      @click="toggleRecording"
      :disabled="!supported"
      :loading="isLoading"
      class="recorder-btn"
    >
      {{ isRecording ? '停止' : '语音录入' }}
    </el-button>
    
    <div v-if="isRecording" class="recording-indicator">
      <span class="recording-dot"></span>
      <span class="recording-text">正在录音...</span>
    </div>
    
    <div v-if="transcript" class="transcript-container">
      <div class="transcript-header">
        <span>转写结果</span>
        <el-button link type="danger" @click="clearTranscript">清除</el-button>
      </div>
      <div class="transcript-content">{{ transcript }}</div>
      <div class="transcript-actions">
        <el-button type="primary" @click="insertTranscript">插入到笔记</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Mic, Close } from '@element-plus/icons-vue'

const emit = defineEmits(['insert'])

const isRecording = ref(false)
const isLoading = ref(false)
const transcript = ref('')
const supported = ref(false)
const mediaRecorder = ref(null)
const audioChunks = ref([])

onMounted(() => {
  supported.value = navigator.mediaDevices && navigator.mediaDevices.getUserMedia
})

async function toggleRecording() {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder.value = new MediaRecorder(stream)
    audioChunks.value = []
    
    mediaRecorder.value.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.value.push(event.data)
      }
    }
    
    mediaRecorder.value.onstop = async () => {
      await sendAudioForTranscription()
    }
    
    mediaRecorder.value.start()
    isRecording.value = true
  } catch (error) {
    console.error('录音启动失败:', error)
    ElMessage.error('录音启动失败，请检查麦克风权限')
  }
}

function stopRecording() {
  if (mediaRecorder.value) {
    mediaRecorder.value.stop()
    mediaRecorder.value.stream.getTracks().forEach(track => track.stop())
    isRecording.value = false
  }
}

async function sendAudioForTranscription() {
  isLoading.value = true
  
  try {
    const audioBlob = new Blob(audioChunks.value, { type: 'audio/webm' })
    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.webm')
    
    const response = await fetch('/api/transcribe', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: formData
    })
    
    const result = await response.json()
    
    if (result.code === 200) {
      transcript.value = result.data.text
    } else {
      transcript.value = '转写失败: ' + (result.message || '未知错误')
    }
  } catch (error) {
    console.error('转写请求失败:', error)
    transcript.value = '转写失败: 网络错误'
  } finally {
    isLoading.value = false
  }
}

function clearTranscript() {
  transcript.value = ''
}

function insertTranscript() {
  if (transcript.value) {
    emit('insert', transcript.value)
    clearTranscript()
  }
}

onUnmounted(() => {
  if (mediaRecorder.value && isRecording.value) {
    stopRecording()
  }
})
</script>

<style scoped>
.voice-recorder {
  display: flex;
  align-items: center;
  gap: 15px;
}

.recorder-btn {
  display: flex;
  align-items: center;
  gap: 8px;
}

.recording-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #ff4d4f;
  font-size: 14px;
}

.recording-dot {
  width: 10px;
  height: 10px;
  background: #ff4d4f;
  border-radius: 50%;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.transcript-container {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 10px;
  width: 400px;
  background: white;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.transcript-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  border-bottom: 1px solid #e6e6e6;
  font-weight: 500;
  color: #333;
}

.transcript-content {
  padding: 15px;
  min-height: 80px;
  max-height: 200px;
  overflow-y: auto;
  font-size: 14px;
  line-height: 1.6;
  color: #666;
  white-space: pre-wrap;
}

.transcript-actions {
  display: flex;
  justify-content: flex-end;
  padding: 12px 15px;
  border-top: 1px solid #e6e6e6;
}
</style>
