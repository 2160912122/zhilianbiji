// WebSocket服务
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { io } from 'socket.io-client'

class SocketService {
  constructor() {
    this.socket = null
    this.url = 'http://localhost:5000'
    this.isConnected = false
    this.roomId = null
    this.userInfo = null
  }

  // 初始化Socket.io连接
  init(userInfo = {}) {
    this.userInfo = userInfo
    this.connect()
  }

  // 连接到Socket.io服务器
  connect() {
    try {
      this.socket = io(this.url, {
        transports: ['websocket'],
        cors: {
          origin: '*',
        },
      })
      
      this.socket.on('connect', () => {
        console.log('Socket.io连接已建立')
        this.isConnected = true
      })

      this.socket.on('disconnect', () => {
        console.log('Socket.io连接已关闭')
        this.isConnected = false
      })

      this.socket.on('connect_error', (error) => {
        console.error('Socket.io连接错误:', error)
      })
    } catch (error) {
      console.error('Socket.io连接建立失败:', error)
    }
  }

  // 发送消息
  emit(event, data) {
    if (this.isConnected && this.socket) {
      this.socket.emit(event, data)
    } else {
      console.error('Socket.io连接未建立，无法发送消息')
    }
  }

  // 注册消息处理器
  on(event, handler) {
    if (this.socket) {
      this.socket.on(event, handler)
    }
  }

  // 取消注册消息处理器
  off(event, handler) {
    if (this.socket) {
      this.socket.off(event, handler)
    }
  }

  // 加入房间
  joinRoom(roomId) {
    this.roomId = roomId
    this.emit('join_room', {
      room_id: roomId,
      user_info: this.userInfo
    })
  }

  // 离开房间
  leaveRoom() {
    if (this.roomId) {
      this.emit('leave_room', {
        room_id: this.roomId
      })
      this.roomId = null
    }
  }

  // 同步文档
  syncDocument(docId, docType, content, version) {
    if (this.roomId) {
      this.emit('sync_document', {
        room_id: this.roomId,
        doc_id: docId,
        doc_type: docType,
        content: content,
        version: version
      })
    }
  }

  // 获取文档状态
  getDocumentState(docId, docType) {
    this.emit('get_document_state', {
      doc_id: docId,
      doc_type: docType
    })
  }

  // 发送消息
  sendMessage(message) {
    if (this.roomId) {
      this.emit('send_message', {
        room_id: this.roomId,
        message: message,
        sender_id: this.userInfo.id || this.socket.id
      })
    }
  }

  // 断开连接
  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
    this.isConnected = false
    this.roomId = null
  }
}

// 创建单例实例
const socketService = new SocketService()

// 导出Vue组合式函数
export function useSocket(userInfo = {}) {
  const connected = ref(false)
  const onlineUsers = ref([])
  const messages = ref([])
  
  // 初始化连接
  const initSocket = () => {
    socketService.init(userInfo)
    
    // 监听连接状态
    socketService.on('connect', () => {
      connected.value = true
    })
    
    socketService.on('disconnect', () => {
      connected.value = false
    })
    
    // 监听在线用户变化
    socketService.on('online_users', (data) => {
      onlineUsers.value = data.users
    })
    
    // 监听用户加入
    socketService.on('user_joined', (data) => {
      onlineUsers.value.push(data.user)
    })
    
    // 监听用户离开
    socketService.on('user_left', (data) => {
      onlineUsers.value = onlineUsers.value.filter(user => user.sid !== data.user_id)
    })
    
    // 监听新消息
    socketService.on('new_message', (data) => {
      messages.value.push(data)
    })
  }
  
  // 加入房间
  const joinRoom = (roomId) => {
    socketService.joinRoom(roomId)
  }
  
  // 离开房间
  const leaveRoom = () => {
    socketService.leaveRoom()
    onlineUsers.value = []
    messages.value = []
  }
  
  // 同步文档
  const syncDocument = (docId, docType, content, version) => {
    socketService.syncDocument(docId, docType, content, version)
  }
  
  // 获取文档状态
  const getDocumentState = (docId, docType) => {
    socketService.getDocumentState(docId, docType)
  }
  
  // 发送消息
  const sendMessage = (message) => {
    socketService.sendMessage(message)
  }
  
  // 监听文档更新
  const onDocumentUpdated = (handler) => {
    socketService.on('document_updated', handler)
  }
  
  // 取消监听文档更新
  const offDocumentUpdated = (handler) => {
    socketService.off('document_updated', handler)
  }
  
  // 监听文档状态
  const onDocumentState = (handler) => {
    socketService.on('document_state', handler)
  }
  
  // 取消监听文档状态
  const offDocumentState = (handler) => {
    socketService.off('document_state', handler)
  }
  
  // 组件卸载时断开连接
  onUnmounted(() => {
    leaveRoom()
  })
  
  return {
    connected,
    onlineUsers,
    messages,
    initSocket,
    joinRoom,
    leaveRoom,
    syncDocument,
    getDocumentState,
    sendMessage,
    onDocumentUpdated,
    offDocumentUpdated,
    onDocumentState,
    offDocumentState
  }
}

export default socketService