<template>
  <div>
    <!-- 顶部导航 -->
    <div class="header">
      <div class="logo">
        <i class="fa fa-book"></i>
        <span>智联笔记</span>
      </div>
      <div class="menu">
        <div style="position: relative;">
          <button id="new-btn" @click="toggleNewMenu">
            <i class="fa fa-file-o"></i> 新建
          </button>
          <div id="new-menu" :class="{ visible: showNewMenu }">
            <div class="new-item" data-type="table" @click="createDocument('table')">
              <i class="fa fa-table" style="color: var(--primary-color);"></i>表格
            </div>
            <div class="new-item" data-type="whiteboard" @click="createDocument('whiteboard')">
              <i class="fa fa-paint-brush" style="color: #faad14;"></i>白板
            </div>
          </div>
        </div>

        <button id="open-btn" @click="openOpenModal">
          <i class="fa fa-folder-open-o"></i> 打开
        </button>
        <button id="save-btn" @click="saveDocument">
          <i class="fa fa-save"></i> 保存
        </button>
        <button id="export-btn" @click="exportDocument">
          <i class="fa fa-download"></i> 导出
        </button>
        <button id="share-btn" @click="openShareModal">
          <i class="fa fa-share-alt"></i> 分享
        </button>
        <button id="toggle-panel-btn" @click="togglePropertiesPanel">
          <i class="fa fa-sliders"></i> 属性
        </button>
        <button id="admin-btn" @click="openAdminModal">
          <i class="fa fa-cog"></i> 管理
        </button>

        <!-- 用户信息和退出按钮 -->
        <div style="position: relative; margin-left: 15px;">
          <button id="user-menu-btn" style="background-color: rgba(255, 255, 255, 0.2);" @click="toggleUserMenu">
            <i class="fa fa-user"></i>
            <span id="current-username">{{ currentUsername || '加载中...' }}</span>
          </button>
          <div id="user-dropdown" class="dropdown-menu" :class="{ visible: showUserMenu }">
            <div class="dropdown-item" id="logout-btn" @click="logout">
              <i class="fa fa-sign-out" style="color: #ef4444;"></i>退出登录
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区 - 三栏布局 -->
    <div class="container">
      <!-- 左侧导航栏 -->
      <div class="sidebar">
        <!-- 搜索笔记 -->
        <div class="sidebar-section">
          <div class="sidebar-header">搜索笔记</div>
          <div class="search-container">
            <input type="text" class="search-input" id="search-notes" placeholder="搜索笔记..." v-model="searchQuery" @input="handleSearch">
          </div>
        </div>

        <!-- 最近笔记 -->
        <div class="sidebar-section">
          <div class="sidebar-header">最近笔记</div>
          <ul class="doc-list" id="recent-notes">
            <li class="doc-item" 
                v-for="doc in recentNotes" 
                :key="doc.id"
                :class="{ active: activeDocument?.id === doc.id, [doc.type]: true }"
                @click="openDocument(doc)">
              <div class="doc-info">
                <div class="doc-name">
                  <i class="fa fa-table" v-if="doc.type === 'table'" style="color: var(--primary-color);"></i>
                  <i class="fa fa-paint-brush" v-else-if="doc.type === 'whiteboard'" style="color: #faad14;"></i>
                  {{ doc.name }}
                  <span class="doc-type">{{ doc.type === 'table' ? '表格' : '白板' }}</span>
                </div>
                <div class="doc-time">{{ formatDate(doc.updated_at) }}</div>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <!-- 中间内容区 -->
      <div class="content-area">
        <!-- 工具栏 -->
        <div class="toolbar" id="main-toolbar">
          <!-- 通用工具 -->
          <button class="tool-btn" title="撤销" id="undo-btn" :disabled="true">
            <i class="fa fa-undo"></i>
          </button>
          <button class="tool-btn" title="重做" id="redo-btn" :disabled="true">
            <i class="fa fa-repeat"></i>
          </button>
          <div class="toolbar-separator"></div>

          <!-- 表格专用工具 -->
          <button class="tool-btn table-tool" title="添加行" v-if="activeDocument?.type === 'table'" id="add-row-btn" @click="handleAddRow">
            <i class="fa fa-plus-square-o"></i>
          </button>
          <button class="tool-btn table-tool" title="添加列" v-if="activeDocument?.type === 'table'" id="add-col-btn" @click="handleAddColumn">
            <i class="fa fa-columns"></i>
          </button>
          <button class="tool-btn table-tool" title="删除选中行" v-if="activeDocument?.type === 'table'" id="delete-row-btn" @click="handleDeleteRow">
            <i class="fa fa-minus-square-o"></i>
          </button>
          <button class="tool-btn table-tool" title="导出表格" v-if="activeDocument?.type === 'table'" id="export-table-btn" @click="handleExportTable">
            <i class="fa fa-download"></i>
          </button>

          <!-- 文本格式工具 -->
          <button class="tool-btn format-tool" title="加粗" id="bold-btn" @click="handleFormat('bold')">
            <i class="fa fa-bold"></i>
          </button>
          <button class="tool-btn format-tool" title="斜体" id="italic-btn" @click="handleFormat('italic')">
            <i class="fa fa-italic"></i>
          </button>
          <button class="tool-btn format-tool" title="下划线" id="underline-btn" @click="handleFormat('underline')">
            <i class="fa fa-underline"></i>
          </button>
          <button class="tool-btn format-tool" title="删除线" id="strikethrough-btn" @click="handleFormat('strikethrough')">
            <i class="fa fa-strikethrough"></i>
          </button>
          <div class="toolbar-separator"></div>

          <!-- 对齐方式工具 -->
          <button class="tool-btn align-tool" title="左对齐" id="align-left-btn" @click="handleAlign('left')">
            <i class="fa fa-align-left"></i>
          </button>
          <button class="tool-btn align-tool" title="居中对齐" id="align-center-btn" @click="handleAlign('center')">
            <i class="fa fa-align-center"></i>
          </button>
          <button class="tool-btn align-tool" title="右对齐" id="align-right-btn" @click="handleAlign('right')">
            <i class="fa fa-align-right"></i>
          </button>
        </div>

        <div class="content-container">
          <!-- 表格容器 -->
          <div id="table-container" v-if="activeDocument?.type === 'table'">
            <TableEditor ref="tableEditorRef" />
          </div>

          <!-- 白板容器 - 使用完整的Excalidraw网站 -->
          <div id="whiteboard-container" v-if="activeDocument?.type === 'whiteboard'">
            <div class="whiteboard-header">
              <div class="whiteboard-title" id="whiteboard-title-display" contenteditable="true" @blur="updateDocumentTitle('whiteboard')">{{ activeDocument?.title || '新白板' }}</div>
            </div>
            <div class="whiteboard-content">
              <iframe 
                src="https://excalidraw.com/" 
                class="excalidraw-iframe"
                frameborder="0"
                width="100%"
                height="100%"
              ></iframe>
            </div>
          </div>

          <!-- 初始空状态 -->
          <div id="empty-state" class="empty-state" v-if="!activeDocument">
            <i class="fa fa-file-text-o"></i>
            <p>请点击"新建"按钮创建表格或白板文档</p>
            <button class="btn primary" id="quick-new-btn" @click="toggleNewMenu">
              <i class="fa fa-file-o"></i> 新建文档
            </button>
          </div>

          <!-- 过期提示 - 仅在分享链接过期时显示 -->
          <div id="expired-notice" class="expired-notice" v-if="isShareLinkExpired">
            <i class="fa fa-clock-o"></i>
            <h2>分享链接已过期</h2>
            <p>此分享链接已超过有效期，请联系文档所有者获取新的分享链接。</p>
            <button class="btn primary" id="go-home-btn" @click="goHome">返回首页</button>
          </div>
        </div>
      </div>

      <!-- 右侧属性面板 -->
      <div class="properties-panel" id="properties-panel" :class="{ visible: showPropertiesPanel }">
        <div class="panel-title">属性设置</div>

        <!-- 表格属性 -->
        <div id="table-properties" v-if="activeDocument?.type === 'table'">
          <div class="property-group">
            <label class="property-label">表格标题</label>
            <input type="text" class="property-input" id="properties-table-title" placeholder="输入表格标题" v-model="activeDocument.title" readonly>
          </div>

          <div class="property-group">
            <label class="property-label">单元格样式</label>
            <div class="style-options">
              <button class="style-btn" data-style="bold" title="加粗" id="properties-bold" @click="handleStyle('bold')">
                <i class="fa fa-bold"></i>
              </button>
              <button class="style-btn" data-style="italic" title="斜体" id="properties-italic" @click="handleStyle('italic')">
                <i class="fa fa-italic"></i>
              </button>
              <button class="style-btn" data-style="underline" title="下划线" id="properties-underline" @click="handleStyle('underline')">
                <i class="fa fa-underline"></i>
              </button>
            </div>
          </div>

          <div class="property-group">
            <label class="property-label">对齐方式</label>
            <div class="style-options">
              <button class="style-btn" data-align="left" title="左对齐" id="properties-align-left" @click="handleAlignStyle('left')">
                <i class="fa fa-align-left"></i>
              </button>
              <button class="style-btn" data-align="center" title="居中对齐" id="properties-align-center" @click="handleAlignStyle('center')">
                <i class="fa fa-align-center"></i>
              </button>
              <button class="style-btn" data-align="right" title="右对齐" id="properties-align-right" @click="handleAlignStyle('right')">
                <i class="fa fa-align-right"></i>
              </button>
            </div>
          </div>

          <div class="property-group">
            <button class="btn primary" id="properties-add-row" @click="handleAddRow">
              <i class="fa fa-plus"></i>添加行
            </button>
            <button class="btn primary" id="properties-add-col" @click="handleAddColumn">
              <i class="fa fa-plus"></i>添加列
            </button>
          </div>

          <div class="property-group">
            <button class="btn" id="properties-delete-row" @click="handleDeleteRow">
              <i class="fa fa-minus"></i>删除选中行
            </button>
            <button class="btn" id="properties-delete-col" @click="handleDeleteColumn">
              <i class="fa fa-minus"></i>删除选中列
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 打开文档弹窗 -->
    <div class="modal-overlay" id="open-modal" :class="{ visible: showOpenModal }" @click="closeModal('open-modal')">
      <div class="modal">
        <div class="modal-header">
          <div class="modal-title">打开文档</div>
          <button class="modal-close" data-modal="open-modal" @click="closeModal('open-modal')">&times;</button>
        </div>
        <div class="modal-body">
          <ul class="doc-list" id="doc-list">
            <li class="doc-item" 
                v-for="doc in documents" 
                :key="doc.id"
                :class="{ [doc.type]: true }"
                @click="openDocument(doc)">
              <div class="doc-info">
                <div class="doc-name">
                  <i class="fa fa-table" v-if="doc.type === 'table'" style="color: var(--primary-color);"></i>
                  <i class="fa fa-paint-brush" v-else-if="doc.type === 'whiteboard'" style="color: #faad14;"></i>
                  {{ doc.name }}
                  <span class="doc-type">{{ doc.type === 'table' ? '表格' : '白板' }}</span>
                </div>
                <div class="doc-time">{{ formatDate(doc.updated_at) }}</div>
              </div>
            </li>
          </ul>
        </div>
        <div class="modal-footer">
          <button class="modal-btn modal-close" data-modal="open-modal" @click="closeModal('open-modal')">取消</button>
        </div>
      </div>
    </div>

    <!-- 增强版分享弹窗 -->
    <div class="modal-overlay" id="share-modal" :class="{ visible: showShareModal }" @click="closeModal('share-modal')">
      <div class="modal" style="max-width: 500px;">
        <div class="modal-header">
          <div class="modal-title">分享文档</div>
          <button class="modal-close" data-modal="share-modal" @click="closeModal('share-modal')">&times;</button>
        </div>
        <div class="modal-body">
          <p style="margin-top: 0; margin-bottom: 16px;">通过以下链接分享你的文档：</p>

          <!-- 权限选择 -->
          <div class="share-options" style="margin-bottom: 20px;">
            <div class="share-option" style="margin-bottom: 12px;">
              <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                <input type="radio" name="share-permission" value="view" checked>
                <span>只读权限</span>
              </label>
            </div>
            <div class="share-option" style="margin-bottom: 16px;">
              <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                <input type="radio" name="share-permission" value="edit">
                <span>可编辑权限</span>
              </label>
            </div>

            <!-- 有效期选择 -->
            <div class="share-expiry" style="display: flex; align-items: center; gap: 10px;">
              <label style="font-size: 14px; color: var(--text-secondary);">链接有效期：</label>
              <select id="share-expiry" style="padding: 8px 12px; border: 1px solid var(--border-color); border-radius: var(--radius); font-size: 14px;">
                <option value="1m">1分钟</option>
                <option value="5m">5分钟</option>
                <option value="10m">10分钟</option>
                <option value="1h">1小时</option>
                <option value="1d" selected>1天</option>
                <option value="7d">7天</option>
                <option value="30d">30天</option>
                <option value="never">永久有效</option>
              </select>
            </div>
          </div>

          <!-- 分享链接显示区域 -->
          <div class="share-link-container" style="display: flex; margin-bottom: 20px; border: 1px solid var(--border-color); border-radius: var(--radius); overflow: hidden;">
            <input type="text" class="share-link" id="share-link" readonly style="flex: 1; border: none; padding: 12px 16px; font-size: 14px; background: var(--bg-tertiary);">
            <button class="copy-btn" id="copy-share-link" style="background: var(--primary-color); color: white; border: none; padding: 0 16px; cursor: pointer; display: flex; align-items: center;">
              <i class="fa fa-copy"></i>
            </button>
          </div>

          <!-- 有效期信息显示 -->
          <div id="expiry-info" style="color: var(--text-tertiary); font-size: 13px; margin-bottom: 16px; text-align: center;">
            链接有效期信息将在这里显示
          </div>

          <div style="background: var(--primary-light); padding: 12px 16px; border-radius: var(--radius); margin-bottom: 16px; border-left: 3px solid var(--primary-color);">
            <p style="margin: 0; font-size: 13px; color: var(--primary-dark);">
              <i class="fa fa-info-circle"></i> 分享链接已生成，复制后发送给其他人
            </p>
          </div>

          <div style="display: flex; gap: 12px;">
            <button class="btn primary" id="generate-link-btn" style="flex: 1;">
              <i class="fa fa-refresh"></i> 生成新链接
            </button>
            <button class="btn modal-close" data-modal="share-modal" style="flex: 1;" @click="closeModal('share-modal')">
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 管理面板 -->
    <div class="modal-overlay" id="admin-modal" :class="{ visible: showAdminModal }" @click="closeModal('admin-modal')">
      <div class="modal">
        <div class="modal-header">
          <div class="modal-title">管理面板</div>
          <button class="modal-close" data-modal="admin-modal" @click="closeModal('admin-modal')">&times;</button>
        </div>
        <div class="modal-body">
          <div style="display: flex; gap: 16px;">
            <div style="flex: 1;">
              <h3 style="margin-top: 0; margin-bottom: 16px; color: var(--text-primary); font-size: 16px; font-weight: 600;">
                <i class="fa fa-cog"></i> 系统管理
              </h3>
              <div style="display: grid; grid-template-columns: 1fr; gap: 12px;">
                <button class="btn" id="user-management-btn" style="text-align: left; justify-content: flex-start; padding: 12px 16px;">
                  <i class="fa fa-users" style="margin-right: 10px;"></i> 用户管理
                </button>
                <button class="btn" id="document-management-btn" style="text-align: left; justify-content: flex-start; padding: 12px 16px;">
                  <i class="fa fa-files-o" style="margin-right: 10px;"></i> 文档管理
                </button>
                <button class="btn" id="system-settings-btn" style="text-align: left; justify-content: flex-start; padding: 12px 16px;">
                  <i class="fa fa-sliders" style="margin-right: 10px;"></i> 系统设置
                </button>
              </div>
            </div>
            <div style="flex: 1;">
              <h3 style="margin-top: 0; margin-bottom: 16px; color: var(--text-primary); font-size: 16px; font-weight: 600;">
                <i class="fa fa-line-chart"></i> 统计信息
              </h3>
              <div style="background: var(--bg-tertiary); padding: 16px; border-radius: var(--radius); margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                  <span style="font-size: 14px; color: var(--text-secondary);">总用户数：</span>
                  <span style="font-size: 16px; font-weight: 600; color: var(--text-primary);">0</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                  <span style="font-size: 14px; color: var(--text-secondary);">总文档数：</span>
                  <span style="font-size: 16px; font-weight: 600; color: var(--text-primary);">0</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                  <span style="font-size: 14px; color: var(--text-secondary);">今日新增：</span>
                  <span style="font-size: 16px; font-weight: 600; color: var(--text-primary);">0</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn modal-close" data-modal="admin-modal" @click="closeModal('admin-modal')">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { Excalidraw } from '@excalidraw/excalidraw'
import TableEditor from '../components/TableEditor.vue'
import { documentAPI } from '../services/api'
import { getCurrentUser } from '../utils/auth'

const router = useRouter()

// 响应式数据
const showNewMenu = ref(false)
const showUserMenu = ref(false)
const showPropertiesPanel = ref(false)
const showOpenModal = ref(false)
const showShareModal = ref(false)
const showAdminModal = ref(false)
const activeDocument = ref(null)
const documents = ref([])
const recentNotes = ref([])
const searchQuery = ref('')
const currentUsername = ref('')
const isShareLinkExpired = ref(false)

// Excalidraw状态
const excalidrawRef = ref(null)
const excalidrawData = ref({
  elements: [],
  appState: {
    theme: 'light',
    language: 'zh-CN',
  }
})

// TableEditor状态
const tableEditorRef = ref(null)

// 方法
const toggleNewMenu = () => {
  showNewMenu.value = !showNewMenu.value
  showUserMenu.value = false
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
  showNewMenu.value = false
}

const togglePropertiesPanel = () => {
  showPropertiesPanel.value = !showPropertiesPanel.value
}

const openOpenModal = () => {
  showOpenModal.value = true
}

const openShareModal = () => {
  showShareModal.value = true
}

const openAdminModal = () => {
  showAdminModal.value = true
}

const closeModal = (modalId) => {
  if (modalId === 'open-modal') {
    showOpenModal.value = false
  } else if (modalId === 'share-modal') {
    showShareModal.value = false
  } else if (modalId === 'admin-modal') {
    showAdminModal.value = false
  }
}

/**
 * 检查文档名称是否已存在
 * @param name 要检查的文档名称
 * @param type 文档类型（table或whiteboard）
 * @returns 是否存在重复名称
 */
const isNameExists = (name, type) => {
  return documents.value.some(doc => 
    doc.name === name && doc.type === type
  );
};

/**
 * 创建新文档
 */
const createDocument = async (type) => {
  showNewMenu.value = false
  try {
    // 文档类型相关信息
    const typeInfo = type === 'table' ? { 
      name: '表格', 
      defaultName: `新表格_${new Date().getTime()}`,
      apiMethod: documentAPI.newTable
    } : {
      name: '白板', 
      defaultName: `新白板_${new Date().getTime()}`,
      apiMethod: documentAPI.newWhiteboard
    };

    // 提示用户输入文档名称
    const name = await ElMessageBox.prompt(`请输入${typeInfo.name}名称`, `新建${typeInfo.name}`, {
      confirmButtonText: '创建',
      cancelButtonText: '取消',
      inputValidator: (value) => {
        if (!value.trim()) {
          return `${typeInfo.name}名称不能为空`;
        }
        if (isNameExists(value.trim(), type)) {
          return `该${typeInfo.name}名称已存在`;
        }
        return true;
      },
      inputValue: typeInfo.defaultName // 默认名称
    }).then(({ value }) => value.trim());

    let result = await typeInfo.apiMethod(name)

    if (result && result.id) {
      await fetchDocuments()
      const newDoc = documents.value.find(doc => doc.id === result.id)
      if (newDoc) {
        activeDocument.value = newDoc
        // 确保TableEditor组件已渲染完成
        await nextTick()
        if (tableEditorRef.value) {
          tableEditorRef.value.initTable(newDoc.id)
        }
      }
    }
  } catch (error) {
    if (error === 'cancel') {
      // 用户取消操作，不显示错误信息
      return;
    }
    console.error('创建文档失败:', error)
  }
}

const openDocument = async (doc) => {
  // 设置activeDocument，条件渲染会自动处理显示和隐藏
  activeDocument.value = doc
  
  // 如果是表格文档，确保TableEditor组件已渲染完成并初始化表格
  if (doc.type === 'table') {
    await nextTick()
    if (tableEditorRef.value) {
      tableEditorRef.value.initTable(doc.id)
    }
  }
}

const saveDocument = async () => {
  try {
    if (!activeDocument.value) return;
    
    if (activeDocument.value.type === 'table' && tableEditorRef.value) {
      // 调用TableEditor的saveTable方法保存表格
      await tableEditorRef.value.saveTable();
    } else if (activeDocument.value.type === 'whiteboard') {
      // 保存白板文档
      if (excalidrawRef.value) {
        const excalidraw = excalidrawRef.value;
        const data = excalidraw.getSceneElements();
        
        // 调用后端保存白板数据
        await documentAPI.saveWhiteboard({
          id: activeDocument.value.id,
          title: activeDocument.value.name,
          room_key: activeDocument.value.roomKey || '',
          data: data
        });
        
        ElMessage.success('白板保存成功！');
      }
    }
  } catch (error) {
    console.error('保存文档失败:', error);
    ElMessage.error('保存文档失败');
  }
}

const exportDocument = () => {
  console.log('导出文档')
}

const logout = () => {
  localStorage.removeItem('user')
  router.push('/login')
}

const goHome = () => {
  router.push('/')
}

const fetchDocuments = async () => {
  try {
    const result = await documentAPI.getDocuments()
    if (Array.isArray(result)) {
      documents.value = result
    } else if (result.status === 'success') {
      documents.value = result.documents || []
    } else {
      documents.value = []
    }
    recentNotes.value = [...documents.value].sort((a, b) => new Date(b.modified) - new Date(a.modified))
  } catch (error) {
    console.error('获取文档列表失败:', error)
  }
}

// Excalidraw数据变化处理
const onExcalidrawChange = (elements, appState) => {
  if (activeDocument.value?.type === 'whiteboard') {
    // 可以在这里保存Excalidraw数据到activeDocument或直接保存到后端
    activeDocument.value.excalidrawData = { elements, appState }
  }
}

const updateDocumentTitle = (type) => {
  console.log('更新文档标题:', type)
}

// 监听activeDocument变化，更新Excalidraw数据或TableEditor
watch(() => activeDocument.value, (newDoc) => {
  if (newDoc?.type === 'whiteboard') {
    // 如果有保存的Excalidraw数据，加载它
    if (newDoc.excalidrawData) {
      excalidrawData.value = newDoc.excalidrawData
    } else {
      // 否则重置为新的空白数据
      excalidrawData.value = {
        elements: [],
        appState: {
          theme: 'light',
          language: 'zh-CN',
        }
      }
    }
  } else if (newDoc?.type === 'table' && tableEditorRef.value) {
    // 如果是表格文档，调用TableEditor的initTable方法加载表格数据
    tableEditorRef.value.initTable(newDoc.id)
  }
}, { deep: true })

const handleSearch = () => {
  const filtered = documents.value.filter(doc => 
    doc.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
  recentNotes.value = filtered
}

const handleAddRow = () => {
  if (tableEditorRef.value) {
    tableEditorRef.value.addRow()
  }
}

const handleAddColumn = () => {
  if (tableEditorRef.value) {
    tableEditorRef.value.addColumn()
  }
}

const handleDeleteRow = () => {
  if (tableEditorRef.value) {
    tableEditorRef.value.deleteRow()
  }
}

const handleExportTable = () => {
  if (tableEditorRef.value) {
    tableEditorRef.value.exportTable()
  }
}

const handleFormat = (format) => {
  console.log('设置格式:', format)
}

const handleAlign = (align) => {
  console.log('设置对齐:', align)
}

const handleToolbarCommand = (command) => {
  console.log('工具栏命令:', command)
}

const handleInsertRow = () => {
  console.log('插入行')
}

const handleInsertColumn = () => {
  console.log('插入列')
}

const handleStyle = (style) => {
  console.log('设置样式:', style)
}

const handleAlignStyle = (align) => {
  console.log('设置对齐样式:', align)
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 生命周期钩子
onMounted(() => {
  fetchDocuments()
  const user = getCurrentUser()
  if (user) {
    currentUsername.value = user.username
  }
  
  // 点击外部关闭下拉菜单
  document.addEventListener('click', (e) => {
    if (!e.target.closest('#new-btn') && !e.target.closest('#new-menu')) {
      showNewMenu.value = false
    }
    if (!e.target.closest('#user-menu-btn') && !e.target.closest('#user-dropdown')) {
      showUserMenu.value = false
    }
  })
})
</script>

<style>
/* 样式保持与HTML模板完全一致 */
:root {
  --primary-color: #10b981;
  --primary-light: #d1fae5;
  --primary-dark: #059669;
  --bg-primary: #fff;
  --bg-secondary: #f8fafc;
  --bg-tertiary: #f1f5f9;
  --text-primary: #334155;
  --text-secondary: #64748b;
  --text-tertiary: #94a3b8;
  --border-color: #e2e8f0;
  --shadow: 0 1px 3px rgba(0,0,0,0.1);
  --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
  --radius: 6px;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  margin: 0;
  padding: 0;
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  overflow: hidden;
  height: 100vh;
  line-height: 1.5;
}

.header {
  background-color: var(--primary-color);
  padding: 0 20px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: var(--shadow-md);
  z-index: 100;
  position: relative;
}

.logo {
  display: flex;
  align-items: center;
  color: white;
  font-weight: 600;
  font-size: 20px;
}

.logo i {
  margin-right: 10px;
  font-size: 24px;
}

.menu {
  display: flex;
  align-items: center;
  gap: 12px;
}

.menu button {
  background-color: rgba(255, 255, 255, 0.15);
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: var(--radius);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
  font-size: 14px;
  font-weight: 500;
}

.menu button:hover {
  background-color: rgba(255, 255, 255, 0.25);
  transform: translateY(-1px);
}

.menu button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.menu button:disabled:hover {
  background-color: rgba(255, 255, 255, 0.15);
}

/* 更新下拉菜单样式 */
#new-menu, #user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: white;
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
  width: 160px;
  z-index: 1000;
  border: 1px solid var(--border-color);
  display: none;
  overflow: hidden;
  margin-top: 8px;
  animation: slideDown 0.2s ease-out;
}

#user-dropdown {
  width: 140px;
  left: auto;
  right: 0;
}

#new-menu.visible, #user-dropdown.visible {
  display: block;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.new-item, .dropdown-item {
  padding: 12px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: background-color 0.2s;
  font-size: 14px;
  border-bottom: 1px solid var(--border-color);
}

.new-item:last-child, .dropdown-item:last-child {
  border-bottom: none;
}

.new-item:hover, .dropdown-item:hover {
  background-color: var(--bg-tertiary);
}

/* 其他样式保持不变 */
.container {
  display: flex;
  height: calc(100vh - 60px);
  overflow: hidden;
}

.sidebar {
  width: 260px;
  background-color: white;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-section {
  padding: 16px 0;
  border-bottom: 1px solid var(--border-color);
}

.sidebar-header {
  padding: 0 16px 12px;
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 14px;
  letter-spacing: 0.5px;
}

.search-container {
  padding: 0 16px 16px;
}

.search-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  font-size: 14px;
  box-sizing: border-box;
  transition: all 0.2s;
}

.search-input:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.doc-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.doc-item {
  padding: 12px 16px;
  border-radius: var(--radius);
  margin-bottom: 6px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-left: 3px solid transparent;
  transition: all 0.2s;
}

.doc-item:hover {
  background-color: var(--bg-tertiary);
}

.doc-item.table {
  border-left-color: var(--primary-color);
}

.doc-item.whiteboard {
  border-left-color: #faad14;
}

.doc-item.active {
  background-color: var(--primary-light);
}

.doc-info {
  flex: 1;
  overflow: hidden;
}

.doc-name {
  font-size: 14px;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500;
}

.doc-type {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-left: 5px;
}

.doc-time {
  font-size: 12px;
  color: var(--text-tertiary);
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.toolbar {
  background-color: white;
  border-bottom: 1px solid var(--border-color);
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.toolbar.readonly {
  opacity: 0.6;
}

.toolbar.readonly .tool-btn {
  cursor: not-allowed;
}

.tool-btn {
  background: none;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: var(--radius);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.tool-btn:hover {
  background-color: var(--bg-tertiary);
  color: var(--text-primary);
}

.tool-btn.active {
  background-color: var(--primary-light);
  color: var(--primary-color);
}

.tool-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.tool-btn:disabled:hover {
  background-color: transparent;
  color: var(--text-secondary);
}

.toolbar-separator {
  width: 1px;
  height: 24px;
  background-color: var(--border-color);
  margin: 0 8px;
}

.content-container {
  flex: 1;
  overflow: hidden;
  position: relative;
}

/* 表格容器 */
#table-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: white;
  overflow: hidden;
}

.table-header {
  padding: 8px 20px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--bg-tertiary);
}

.table-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--radius);
  transition: background-color 0.2s;
}

.table-title:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.table-title.editing {
  background-color: white;
  border: 1px solid var(--primary-color);
  outline: none;
}

.formula-bar {
  height: 40px;
  background-color: white;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
}

.cell-address {
  width: 70px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border-right: 1px solid var(--border-color);
  font-size: 13px;
  background-color: var(--bg-tertiary);
  font-weight: 500;
  color: var(--text-secondary);
}

.formula-input {
  flex: 1;
  height: 100%;
  border: none;
  padding: 0 16px;
  font-size: 14px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.formula-input:focus {
  outline: none;
}

.formula-input:read-only {
  background-color: var(--bg-tertiary);
  cursor: not-allowed;
}

.table-toolbar {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: white;
  flex-wrap: wrap;
}

.table-toolbar.readonly {
  opacity: 0.6;
}

.table-toolbar.readonly .toolbar-btn {
  cursor: not-allowed;
}

.toolbar-section {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-btn {
  height: 32px;
  padding: 0 12px;
  border: 1px solid var(--border-color);
  background-color: white;
  border-radius: var(--radius);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-primary);
  transition: all 0.2s;
  font-weight: 500;
}

.toolbar-btn:hover {
  background-color: var(--bg-tertiary);
  border-color: var(--text-tertiary);
}

.toolbar-btn.active {
  background-color: var(--primary-light);
  color: var(--primary-color);
  border-color: var(--primary-color);
}

.toolbar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toolbar-btn:disabled:hover {
  background-color: white;
  border-color: var(--border-color);
}

.table-container {
  flex: 1;
  overflow: auto;
  padding: 20px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
  box-shadow: var(--shadow);
  border-radius: var(--radius);
  overflow: hidden;
}

.data-table th, .data-table td {
  border: 1px solid var(--border-color);
  padding: 12px 16px;
  text-align: left;
  min-width: 120px;
}

.data-table th {
  background-color: var(--bg-tertiary);
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 10;
  color: var(--text-primary);
}

.data-table td {
  position: relative;
  transition: background-color 0.2s;
}

.data-table td:hover {
  background-color: var(--bg-tertiary);
}

.data-table td.selected {
  background-color: var(--primary-light);
  box-shadow: inset 0 0 0 1px var(--primary-color);
}

.data-table.readonly td {
  cursor: not-allowed;
}

.data-table.readonly td:hover {
  background-color: transparent;
}

/* 白板容器 */
#whiteboard-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: white;
  overflow: hidden;
}

.whiteboard-header {
  padding: 8px 20px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--bg-tertiary);
}

.whiteboard-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--radius);
  transition: background-color 0.2s;
}

.whiteboard-title:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.whiteboard-title.editing {
  background-color: white;
  border: 1px solid var(--primary-color);
  outline: none;
}

.whiteboard-content {
  flex: 1;
  overflow: hidden;
  background-color: white;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  margin: 16px;
}

.excalidraw-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

/* 移除不再需要的iframe样式 */

/* 空状态 */
#empty-state {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  background-color: var(--bg-secondary);
}

#empty-state i {
  font-size: 80px;
  margin-bottom: 24px;
  color: var(--primary-color);
  opacity: 0.7;
}

#empty-state p {
  font-size: 18px;
  margin-bottom: 32px;
  text-align: center;
  padding: 0 20px;
  max-width: 400px;
  line-height: 1.6;
}

#quick-new-btn {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 500;
}

#quick-new-btn:hover {
  background-color: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* 属性面板 */
.properties-panel {
  width: 280px;
  background-color: white;
  border-left: 1px solid var(--border-color);
  padding: 16px;
  overflow-y: auto;
  box-shadow: -1px 0 3px rgba(0,0,0,0.05);
  display: none;
}

.properties-panel.visible {
  display: block;
}

.panel-title {
  font-size: 16px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
  font-weight: 600;
}

.property-group {
  margin-bottom: 20px;
}

.property-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.property-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  font-size: 14px;
  box-sizing: border-box;
  transition: all 0.2s;
}

.property-input:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.property-input:read-only {
  background-color: var(--bg-tertiary);
  cursor: not-allowed;
}

.style-options {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.style-btn {
  width: 40px;
  height: 40px;
  border-radius: var(--radius);
  cursor: pointer;
  border: 2px solid transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  background-color: var(--bg-tertiary);
}

.style-btn:hover {
  background-color: #e2e8f0;
}

.style-btn.selected {
  border-color: var(--primary-color);
  background-color: var(--primary-light);
}

.style-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.style-btn:disabled:hover {
  background-color: var(--bg-tertiary);
}

/* 按钮样式 */
.btn {
  padding: 10px 18px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background-color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
  font-size: 14px;
  font-weight: 500;
}

.btn:hover {
  background-color: var(--bg-tertiary);
}

.btn.primary {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.btn.primary:hover {
  background-color: var(--primary-dark);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn:disabled:hover {
  background-color: white;
}

.btn.primary:disabled:hover {
  background-color: var(--primary-color);
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: none;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-overlay.visible {
  display: flex;
}

.modal {
  background: white;
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
  width: 90%;  /* 改为百分比宽度 */
  max-width: 800px;  /* 增加最大宽度 */
  max-height: 90%;
  overflow: auto;
}

.modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.modal-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--text-secondary);
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background-color: var(--bg-tertiary);
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.modal-btn {
  padding: 10px 20px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background: white;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.modal-btn:hover {
  background-color: var(--bg-tertiary);
}

.modal-btn-primary {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.modal-btn-primary:hover {
  background-color: var(--primary-dark);
}

/* 用户下拉菜单样式 */
#user-dropdown {
  right: 0;
  left: auto;
}

#current-username {
  margin-left: 5px;
}

#user-menu-btn {
  display: flex;
  align-items: center;
}
</style>