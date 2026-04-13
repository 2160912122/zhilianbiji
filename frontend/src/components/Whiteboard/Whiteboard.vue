<template>
  <div class="whiteboard-wrapper">
    <div id="whiteboard-container" ref="whiteboardContainer"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { io } from 'socket.io-client'

const props = defineProps({
  roomKey: {
    type: String,
    required: true
  }
})

const whiteboardContainer = ref(null)
let whiteboard = null
let socket = null

onMounted(() => {
  // 加载 Whitebophir 核心文件
  loadWhitebophirScripts()
})

onUnmounted(() => {
  // 清理白板资源
  if (whiteboard) {
    console.log('清理白板资源')
  }
  // 断开 Socket 连接
  if (socket) {
    socket.disconnect()
  }
})

watch(() => props.roomKey, (newRoomKey) => {
  // 当 roomKey 变化时，重新初始化白板
  if (newRoomKey) {
    initWhiteboard(newRoomKey)
  }
})

function loadWhitebophirScripts() {
  // 加载 Whitebophir 的核心 JavaScript 文件
  const scripts = [
    '/src/components/Whiteboard/wbo/path-data-polyfill.js',
    '/src/components/Whiteboard/wbo/minitpl.js',
    '/src/components/Whiteboard/wbo/intersect.js',
    '/src/components/Whiteboard/wbo/board.js',
    '/src/components/Whiteboard/wbo/tools/pencil/wbo_pencil_point.js',
    '/src/components/Whiteboard/wbo/tools/pencil/pencil.js',
    '/src/components/Whiteboard/wbo/tools/cursor/cursor.js',
    '/src/components/Whiteboard/wbo/tools/line/line.js',
    '/src/components/Whiteboard/wbo/tools/rect/rect.js',
    '/src/components/Whiteboard/wbo/tools/ellipse/ellipse.js',
    '/src/components/Whiteboard/wbo/tools/text/text.js',
    '/src/components/Whiteboard/wbo/tools/eraser/eraser.js',
    '/src/components/Whiteboard/wbo/tools/hand/hand.js',
    '/src/components/Whiteboard/wbo/tools/grid/grid.js',
    '/src/components/Whiteboard/wbo/tools/download/download.js',
    '/src/components/Whiteboard/wbo/tools/zoom/zoom.js',
    '/src/components/Whiteboard/wbo/tools/clear/clear.js',
    '/src/components/Whiteboard/wbo/canvascolor.js'
  ]

  let loaded = 0
  scripts.forEach(scriptSrc => {
    const script = document.createElement('script')
    script.src = scriptSrc
    script.onload = () => {
      loaded++
      if (loaded === scripts.length) {
        // 所有脚本加载完成后，初始化白板
        initWhiteboard(props.roomKey)
      }
    }
    script.onerror = (error) => {
      console.error(`加载脚本失败: ${scriptSrc}`, error)
    }
    document.head.appendChild(script)
  })

  // 加载 Whitebophir 的 CSS 文件
  const link = document.createElement('link')
  link.rel = 'stylesheet'
  link.href = '/src/components/Whiteboard/wbo/board.css'
  document.head.appendChild(link)
  
  // 加载工具的 CSS 文件
  const toolCssFiles = [
    '/src/components/Whiteboard/wbo/tools/pencil/pencil.css',
    '/src/components/Whiteboard/wbo/tools/line/line.css',
    '/src/components/Whiteboard/wbo/tools/rect/rect.css',
    '/src/components/Whiteboard/wbo/tools/ellipse/ellipse.css',
    '/src/components/Whiteboard/wbo/tools/text/text.css'
  ]
  
  toolCssFiles.forEach(cssSrc => {
    const link = document.createElement('link')
    link.rel = 'stylesheet'
    link.href = cssSrc
    document.head.appendChild(link)
  })
}

function initWhiteboard(roomKey) {
  if (!whiteboardContainer.value) return

  // 清空容器
  whiteboardContainer.value.innerHTML = ''

  // 创建白板容器
  const boardContainer = document.createElement('div')
  boardContainer.id = 'board'
  whiteboardContainer.value.appendChild(boardContainer)

  // 创建 SVG 画布
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
  svg.id = 'canvas'
  svg.setAttribute('width', '500')
  svg.setAttribute('height', '500')
  svg.setAttribute('version', '1.1')
  boardContainer.appendChild(svg)

  // 创建 defs 元素
  const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs')
  defs.id = 'defs'
  svg.appendChild(defs)

  // 创建 drawingArea 元素
  const drawingArea = document.createElementNS('http://www.w3.org/2000/svg', 'g')
  drawingArea.id = 'drawingArea'
  svg.appendChild(drawingArea)

  // 创建 cursors 元素
  const cursors = document.createElementNS('http://www.w3.org/2000/svg', 'g')
  cursors.id = 'cursors'
  svg.appendChild(cursors)

  // 创建加载消息元素
  const loadingMessage = document.createElement('div')
  loadingMessage.id = 'loadingMessage'
  loadingMessage.textContent = '加载中...'
  whiteboardContainer.value.appendChild(loadingMessage)

  // 创建菜单元素
  const menu = document.createElement('div')
  menu.id = 'menu'
  menu.setAttribute('tabindex', '0')
  whiteboardContainer.value.appendChild(menu)

  // 创建菜单内容
  const menuItems = document.createElement('div')
  menuItems.id = 'menuItems'
  menu.appendChild(menuItems)

  // 创建工具列表
  const tools = document.createElement('ul')
  tools.id = 'tools'
  tools.className = 'tools'
  menuItems.appendChild(tools)

  // 创建工具项
  const toolItem = document.createElement('li')
  toolItem.className = 'tool'
  toolItem.setAttribute('tabindex', '-1')
  tools.appendChild(toolItem)

  // 创建工具图标
  const toolIcon = document.createElement('img')
  toolIcon.className = 'tool-icon'
  toolIcon.setAttribute('width', '35')
  toolIcon.setAttribute('height', '35')
  toolIcon.setAttribute('src', '')
  toolIcon.setAttribute('alt', 'icon')
  toolItem.appendChild(toolIcon)

  // 创建工具名称
  const toolName = document.createElement('span')
  toolName.className = 'tool-name'
  toolItem.appendChild(toolName)

  // 创建次要图标
  const secondaryIcon = document.createElement('img')
  secondaryIcon.className = 'tool-icon secondaryIcon'
  secondaryIcon.setAttribute('width', '35')
  secondaryIcon.setAttribute('height', '35')
  secondaryIcon.setAttribute('src', 'data:,')
  secondaryIcon.setAttribute('alt', 'icon')
  toolItem.appendChild(secondaryIcon)

  // 创建设置列表
  const settings = document.createElement('ul')
  settings.id = 'settings'
  settings.className = 'tools'
  menuItems.appendChild(settings)

  // 创建颜色选择器
  const colorItem = document.createElement('li')
  colorItem.className = 'tool'
  colorItem.setAttribute('tabindex', '-1')
  settings.appendChild(colorItem)

  const colorInput = document.createElement('input')
  colorInput.className = 'tool-icon'
  colorInput.setAttribute('type', 'color')
  colorInput.id = 'chooseColor'
  colorInput.setAttribute('value', '#1913B0')
  colorItem.appendChild(colorInput)

  const colorLabel = document.createElement('label')
  colorLabel.className = 'tool-name'
  colorLabel.setAttribute('for', 'chooseColor')
  colorLabel.textContent = '颜色'
  colorItem.appendChild(colorLabel)

  const colorPresets = document.createElement('span')
  colorPresets.className = 'colorPresets'
  colorPresets.id = 'colorPresetSel'
  colorItem.appendChild(colorPresets)

  const colorPresetButton = document.createElement('span')
  colorPresetButton.className = 'colorPresetButton'
  colorPresets.appendChild(colorPresetButton)

  // 创建大小选择器
  const sizeItem = document.createElement('li')
  sizeItem.className = 'tool'
  sizeItem.setAttribute('tabindex', '-1')
  sizeItem.setAttribute('title', '大小 (快捷键: alt + 鼠标滚轮)')
  settings.appendChild(sizeItem)

  const sizeIcon = document.createElement('img')
  sizeIcon.className = 'tool-icon'
  sizeIcon.setAttribute('width', '60')
  sizeIcon.setAttribute('height', '60')
  sizeIcon.setAttribute('src', '/src/components/Whiteboard/wbo/tools/zoom/icon.svg')
  sizeIcon.setAttribute('alt', 'size')
  sizeItem.appendChild(sizeIcon)

  const sizeLabel = document.createElement('label')
  sizeLabel.className = 'tool-name slider'
  sizeLabel.setAttribute('for', 'chooseSize')
  sizeItem.appendChild(sizeLabel)

  const sizeSpan = document.createElement('span')
  sizeSpan.textContent = '大小'
  sizeLabel.appendChild(sizeSpan)

  const sizeInput = document.createElement('input')
  sizeInput.setAttribute('type', 'range')
  sizeInput.id = 'chooseSize'
  sizeInput.setAttribute('value', '4')
  sizeInput.setAttribute('min', '1')
  sizeInput.setAttribute('max', '50')
  sizeInput.setAttribute('step', '1')
  sizeInput.className = 'rangeChooser'
  sizeLabel.appendChild(sizeInput)

  // 创建透明度选择器
  const opacityItem = document.createElement('li')
  opacityItem.className = 'tool'
  opacityItem.setAttribute('tabindex', '-1')
  settings.appendChild(opacityItem)

  const opacityIcon = document.createElement('span')
  opacityIcon.className = 'tool-icon'
  opacityIcon.innerHTML = `
    <svg viewBox="0 0 8 8">
      <pattern id="opacityPattern" x="0" y="0" width="4" height="4" patternUnits="userSpaceOnUse">
        <rect x=0 y=0 width=2 height=2 fill=black></rect>
        <rect x=2 y=2 width=2 height=2 fill=black></rect>
        <rect x=2 y=0 width=2 height=2 fill=#eeeeee></rect>
        <rect x=0 y=2 width=2 height=2 fill=#eeeeee></rect>
      </pattern>
      <circle cx=4 cy=4 id="opacityIndicator" r=3.5 fill="url(#opacityPattern)"></circle>
    </svg>
  `
  opacityItem.appendChild(opacityIcon)

  const opacityLabel = document.createElement('label')
  opacityLabel.className = 'tool-name slider'
  opacityLabel.setAttribute('for', 'chooseOpacity')
  opacityItem.appendChild(opacityLabel)

  const opacitySpan = document.createElement('span')
  opacitySpan.textContent = '透明度'
  opacityLabel.appendChild(opacitySpan)

  const opacityInput = document.createElement('input')
  opacityInput.setAttribute('type', 'range')
  opacityInput.id = 'chooseOpacity'
  opacityInput.setAttribute('value', '1')
  opacityInput.setAttribute('min', '0.2')
  opacityInput.setAttribute('max', '1')
  opacityInput.setAttribute('step', '0.1')
  opacityInput.className = 'rangeChooser'
  opacityLabel.appendChild(opacityInput)

  // 创建配置和翻译数据
  const configuration = {
    boardName: roomKey,
    lang: 'zh-CN',
    baseUrl: window.location.origin,
    boardUriComponent: roomKey,
    hideMenu: false,
    moderator: true,
    BLOCKED_TOOLS: []
  }

  const translations = {
    collaborative_whiteboard: '协作白板',
    loading: '加载中...',
    color: '颜色',
    size: '大小',
    keyboard_shortcut: '快捷键',
    mousewheel: '鼠标滚轮',
    opacity: '透明度',
    tagline: '在线协作白板'
  }

  // 创建配置脚本
  const configScript = document.createElement('script')
  configScript.type = 'application/json'
  configScript.id = 'configuration'
  configScript.textContent = JSON.stringify(configuration)
  whiteboardContainer.value.appendChild(configScript)

  // 创建翻译脚本
  const translationScript = document.createElement('script')
  translationScript.type = 'application/json'
  translationScript.id = 'translations'
  translationScript.textContent = JSON.stringify(translations)
  whiteboardContainer.value.appendChild(translationScript)

  // 初始化 Socket.IO 连接
  initSocket(roomKey)

  // 初始化 Whitebophir
  console.log('初始化白板，roomKey:', roomKey)
  
  // 等待一段时间，确保所有脚本都已加载
  setTimeout(() => {
    // 这里需要调用 Whitebophir 的初始化函数
    // 根据 board.js 的逻辑，它会自动初始化
    console.log('白板初始化完成')
  }, 1000)
}

function initSocket(roomKey) {
  // 断开之前的连接
  if (socket) {
    socket.disconnect()
  }

  // 初始化 Socket.IO 连接
  socket = io({
    reconnection: true,
    reconnectionDelay: 100,
    timeout: 1000 * 60 * 20,
    path: '/socket.io'
  })

  // 监听连接事件
  socket.on('connect', () => {
    console.log('Socket.IO 连接成功')
    // 加入白板房间
    socket.emit('getboard', roomKey)
  })

  // 监听断开连接事件
  socket.on('disconnect', () => {
    console.log('Socket.IO 连接断开')
  })

  // 监听错误事件
  socket.on('error', (error) => {
    console.error('Socket.IO 错误:', error)
  })

  // 监听广播消息
  socket.on('broadcast', (message) => {
    console.log('收到广播消息:', message)
    // 处理消息
    if (window.handleMessage) {
      window.handleMessage(message)
    }
  })

  // 重写 Tools.socket 对象，使其使用我们的 Socket.IO 连接
  window.Tools = window.Tools || {}
  window.Tools.socket = {
    emit: (event, data) => {
      console.log('发送消息:', event, data)
      socket.emit(event, data)
    },
    on: (event, callback) => {
      socket.on(event, callback)
    },
    connect: () => {
      console.log('Socket 已连接')
    },
    destroy: () => {
      socket.disconnect()
    }
  }

  // 重写 Tools.connect 方法
  window.Tools.connect = function() {
    console.log('Tools.connect 被调用')
  }
}
</script>

<style scoped>
.whiteboard-wrapper {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

#whiteboard-container {
  width: 100%;
  height: 100%;
  min-height: 600px;
}
</style>