<template>
  <div class="mindbox">
    <div id="jsmind_container" style="width: 100%; height: 100%; overflow: auto;"></div>
  </div>
</template>

<script>
import { createMindmap, updateMindmap, deleteMindmap, getMindmapById, createTag, updateTag, deleteTag, bindTagToMindmap, unbindTagFromMindmap } from '@/api/mindmapApi'
import { getVersionList, createVersion, getVersionDetail, restoreVersion } from '@/api/versionApi'
import html2canvas from 'html2canvas'

export default {
  name: 'MindmapCanvas',
  props: {
    currentId: { type: [String, Number], default: null }
  },
  data() {
    return {
      jm: null,
      comments: [],
      commentCount: 0,
      undoStack: [],
      redoStack: [],
      originalAddNode: null,
      originalRemoveNode: null,
      originalUpdateNode: null
    }
  },
  mounted() {
    // 原有的代码
    setTimeout(() => { if(!this.jm) this.initJSMind() }, 300)
    this.$nextTick(() => this.initJSMind())
    // 如果传入了 currentId，尝试打开对应脑图
    if (this.currentId && this.currentId.toString().trim()) {
      // small delay 等待 jm 初始化
      setTimeout(() => {
        this.openMap(this.currentId).catch(err => {
          console.error('Mounted openMap Error:', err)
          this.createDefaultMindMap()
        })
      }, 500)
    } else {
      // 如果没有有效的currentId，创建默认脑图
      this.createDefaultMindMap()
    }
  },
  watch: {
    currentId(newVal) {
      if (!newVal) return
      if (!this.jm) {
        // 等待 jm 初始化后再打开
        const tid = setInterval(() => {
          if (this.jm) {
            clearInterval(tid)
            this.openMap(newVal).catch(()=>{})
          }
        }, 200)
      } else {
        this.openMap(newVal).catch(()=>{})
      }
    }
  },
  methods: {
    // ========== 脑图核心初始化 ==========
    initJSMind() {
      const J = window.jsMind || window.jsmind
      if (J && !this.jm) {
        try {
          this.jm = new J({
          container: 'jsmind_container',
          theme: 'primary',
          editable: true,
          view: { hmargin: 100, vmargin: 50, line_width: 2, line_color: '#409eff' },
          layout: { hspace: 80, vspace: 20, pspace: 13 }
        })
          // 尝试直接从全局对象获取 undo 插件
          if (window.jsmind && window.jsmind.plugin && window.jsmind.plugin.undo) {
            this.jm.undo = new window.jsmind.plugin.undo(this.jm)
            console.log('undo plugin initialized from window.jsmind')
          } else if (J.plugin && J.plugin.undo) {
            this.jm.undo = new J.plugin.undo(this.jm)
            console.log('undo plugin initialized from J.plugin')
          } else {
            // 尝试手动加载 undo 插件
            console.log('undo plugin not found, trying to load...')
            const script = document.createElement('script')
            script.src = '/jsmind.undo.js'
            script.onload = () => {
              console.log('jsmind.undo.js loaded successfully')
              if (window.jsmind && window.jsmind.plugin && window.jsmind.plugin.undo) {
                this.jm.undo = new window.jsmind.plugin.undo(this.jm)
                console.log('undo plugin initialized after loading')
              }
            }
            script.onerror = (error) => {
              console.error('Failed to load jsmind.undo.js:', error)
            }
            document.head.appendChild(script)
          }
          
          // 添加事件监听器来捕获用户操作
          this.setupEventListeners()
          
          this.createDefaultMindMap()
          this.$emit('jmInit', this.jm) // 把实例传给根组件
        } catch (e) {
          console.error('jsMind init failed', e)
        }
      } else if (!this.jm) {
        setTimeout(() => this.initJSMind(), 500)
      }
    },
    
    // 设置事件监听器来捕获用户操作
    setupEventListeners() {
      if (!this.jm) return
      
      // 保存原始方法到data中
      this.originalAddNode = this.jm.add_node
      this.originalRemoveNode = this.jm.remove_node
      this.originalUpdateNode = this.jm.update_node
      
      // 重写 add_node 方法
      this.jm.add_node = (parent_node, node_id, node_topic, node_direction, node_expanded) => {
        const result = this.originalAddNode.call(this.jm, parent_node, node_id, node_topic, node_direction, node_expanded)
        if (result) {
          // 记录添加节点操作
          this.undoStack.push({
            type: 'add',
            parent: parent_node instanceof Object ? parent_node.id : parent_node, // 存储 parent 的 ID
            node: {
              id: result.id,
              topic: result.topic
            }
          })
          // 清空 redo 栈
          this.redoStack = []
          console.log('Add node operation recorded:', result.id)
        }
        return result
      }
      
      // 重写 remove_node 方法
      this.jm.remove_node = (node) => {
        if (!node) return false
        
        // 记录删除节点操作
        this.undoStack.push({
          type: 'remove',
          node: {
            id: node.id,
            topic: node.topic
          },
          parent: node.parent instanceof Object ? node.parent.id : node.parent // 存储 parent 的 ID
        })
        // 清空 redo 栈
        this.redoStack = []
        console.log('Remove node operation recorded:', node.id)
        
        return this.originalRemoveNode.call(this.jm, node)
      }
      
      // 重写 update_node 方法
      this.jm.update_node = (node, new_topic) => {
        if (!node || !new_topic) return false
        
        const old_topic = node.topic
        const result = this.originalUpdateNode.call(this.jm, node, new_topic)
        if (result) {
          // 记录更新节点操作
          this.undoStack.push({
            type: 'update',
            node: {
              id: node.id
            },
            oldTopic: old_topic,
            newTopic: new_topic
          })
          // 清空 redo 栈
          this.redoStack = []
          console.log('Update node operation recorded:', node.id)
        }
        return result
      }
    },
    // 创建默认脑图
    createDefaultMindMap() {
      const defaultData = {
        meta: { name: "默认脑图", author: this.$root.currentUser?.username || '未知用户', version: '1.0' },
        format: 'node_tree',
        data: { id: 'root', topic: '中心主题', direction: 'right', expanded: true, children: [] }
      }
      if (this.jm) this.jm.show(defaultData)
    },
    // ========== 脑图核心操作 ==========
    async createMap(mName, mTopic, currentUser) {
      if(!mName.trim() || !mTopic.trim()) return this.$emit('canvasError', '请填写完整的脑图名称和中心主题', 'warning')
      const data = {
        meta: { name: mName, author: currentUser.username, version: '1.0' },
        format: 'node_tree',
        data: { id: 'root', topic: mTopic, direction: 'right', expanded: true, children: [] }
      }
      try {
        const res = await createMindmap({ name: mName, data })
        this.$root.mapList.push(res.data)
        this.openMap(res.data.id)
        this.$emit('canvasError', '脑图创建成功', 'success')
      } catch (err) {
        this.$emit('canvasError', '创建失败：'+err.message, 'error')
      }
    },
    async openMap(id) {
      try {
        // 检查id是否为空
        if (!id) {
          throw new Error('脑图ID为空')
        }
        
        const res = await getMindmapById(id)
        
        // 检查res是否为null或undefined
        if (!res) {
          throw new Error('获取脑图响应失败')
        }
        
        const m = res.data
        // 检查m是否为null或undefined
        if (!m) {
          throw new Error('获取脑图数据失败，数据为空')
        }
        
        let mindData = m.data
        // 处理m.data的各种情况
        if (mindData === null || mindData === undefined) {
          throw new Error('脑图数据字段为空')
        }
        
        if (typeof mindData === 'string') {
          try {
            mindData = JSON.parse(mindData)
          } catch (parseError) {
            throw new Error('脑图数据JSON解析失败: ' + parseError.message)
          }
          // 检查解析后的JSON是否有效
          if (!mindData) {
            throw new Error('解析后的脑图数据为空')
          }
        }
        
        // 检查mindData是否为null或undefined
        if (!mindData) {
          throw new Error('脑图数据为空')
        }
        
        // 检查mindData格式是否有效
        if (mindData && mindData.id && !mindData.format) {
          mindData = { meta: { name: m.name }, format: 'node_tree', data: mindData }
        }
        
        // 确保mindData包含有效的jsmind数据结构
        if (!mindData.format || !mindData.data) {
          // 如果缺少format或data字段，创建默认的有效结构
          mindData = {
            meta: { name: m.name || '默认脑图' },
            format: 'node_tree',
            data: {
              id: 'root',
              topic: m.name || '默认主题',
              children: []
            }
          }
        } else {
          // 检查根节点是否存在且具有有效id
          const rootNode = mindData.format === 'node_tree' ? mindData.data : mindData.data.root
          if (!rootNode || !rootNode.id) {
            // 如果根节点无效，创建默认根节点
            mindData = {
              meta: { name: m.name || '默认脑图' },
              format: 'node_tree',
              data: {
                id: 'root',
                topic: m.name || '默认主题',
                children: []
              }
            }
          }
        }
        
        if(!this.jm) this.initJSMind()
        this.jm && this.jm.show(mindData)
        await this.loadComments(id)
      } catch (err) {
        console.error('openMap Error:', err)
        this.$emit('canvasError', '打开失败：'+err.message, 'error')
        this.createDefaultMindMap()
      }
    },
    async saveMap(id) {
      if(!this.jm || !id) return this.$emit('canvasError', '无正在编辑的脑图', 'warning')
      try {
        const data = this.jm.get_data()
        await updateMindmap(id, { data })
        await this.createVersion(id, {change_description: '自动保存'})
      } catch (err) {
        this.$emit('canvasError', '保存失败：'+err.message, 'error')
      }
    },
    async delMap(id) {
      try {
        await deleteMindmap(id)
        if(this.$root.currentId === id) {
          this.$root.currentId = null
          this.jm && this.jm.clear()
        }
      } catch (err) {
        this.$emit('canvasError', '删除失败：'+err.message, 'error')
      }
    },
    // ========== 节点操作 ==========
    addChild() {
      if(!this.jm) return this.$emit('canvasError', '脑图未初始化', 'warning')
      const node = this.jm.get_selected_node()
      if(!node) return this.$emit('canvasError', '请先选中一个节点', 'warning')
      this.jm.add_node(node, 'node_'+Date.now(), '新节点')
    },
    addBro() {
      if(!this.jm) return this.$emit('canvasError', '脑图未初始化', 'warning')
      const node = this.jm.get_selected_node()
      if(!node) return this.$emit('canvasError', '请先选中一个节点', 'warning')
      
      try {
        // 检查节点是否有父节点或是否为根节点
        if (!node.parent && node.id !== 'root') {
          return this.$emit('canvasError', '选中的节点无效', 'warning')
        }
        
        this.jm.insert_node_after(node, 'node_'+Date.now(), '兄弟节点')
      } catch (err) {
        console.error('添加兄弟节点失败:', err)
        this.$emit('canvasError', '添加兄弟节点失败，请重试', 'error')
      }
    },
    editNode() {
      if(!this.jm) return this.$emit('canvasError', '脑图未初始化', 'warning')
      const node = this.jm.get_selected_node()
      if(!node) return this.$emit('canvasError', '请先选中一个节点', 'warning')
      this.jm.begin_edit(node)
    },
    delNode() {
      if(!this.jm) return this.$emit('canvasError', '脑图未初始化', 'warning')
      const node = this.jm.get_selected_node()
      if(!node) return this.$emit('canvasError', '请先选中一个节点', 'warning')
      this.jm.remove_node(node)
    },
    moveUp() {
        if(this.jm) {
          const node = this.jm.get_selected_node();
          if(node && node.parent && node.parent.id) {
            this.jm.move_node(node, 'up');
          } else {
            console.warn('No valid node selected or node has no parent');
          }
        }
      },
    moveDown() { if(this.jm) { const node = this.jm.get_selected_node(); node && this.jm.move_node(node, 'down') } },
    toggleNode() {
      if(!this.jm) return this.$emit('canvasError', '脑图未初始化', 'warning')
      const node = this.jm.get_selected_node()
      if(!node) return this.$emit('canvasError', '请先选中一个节点', 'warning')
      this.jm.toggle_node(node)
    },
    zoomIn() { this.jm && this.jm.view.zoomIn() },
    zoomOut() { this.jm && this.jm.view.zoomOut() },
    resetZoom() { this.jm && this.jm.view.setZoom(1) },
    undo() {
      console.log('Undo called, undoStack length:', this.undoStack.length)
      if (this.jm && this.undoStack.length > 0) {
        const operation = this.undoStack.pop()
        console.log('Undo operation:', operation)
        this.redoStack.push(operation)
        console.log('RedoStack after push:', this.redoStack.length)
        
        switch (operation.type) {
          case 'add': {
            // 对于添加操作，撤销就是删除该节点
            const nodeToRemove = this.jm.get_node(operation.node.id)
            console.log('Node to remove:', nodeToRemove)
            if (nodeToRemove) {
              // 使用原始方法，避免再次触发操作记录
              this.originalRemoveNode.call(this.jm, nodeToRemove)
            }
            break
          }
          case 'remove': {
            // 对于删除操作，撤销就是使用节点的 ID 重新添加该节点
            if (operation.parent && operation.node) {
              const parentNode = this.jm.get_node(operation.parent)
              console.log('Parent node:', parentNode)
              if (parentNode) {
                // 使用原始方法，避免再次触发操作记录
                this.originalAddNode.call(this.jm, parentNode, operation.node.id, operation.node.topic)
              }
            }
            break
          }
          case 'update': {
            // 对于更新操作，撤销就是恢复原来的主题
            const nodeToUpdate = this.jm.get_node(operation.node.id)
            console.log('Node to update:', nodeToUpdate)
            if (nodeToUpdate) {
              // 使用原始方法，避免再次触发操作记录
              this.originalUpdateNode.call(this.jm, nodeToUpdate, operation.oldTopic)
            }
            break
          }
        }
        console.log('Undo performed:', operation.type)
      } else {
        console.log('Undo not performed, either jm is null or undoStack is empty')
      }
    },
    redo() {
      console.log('Redo called, redoStack length:', this.redoStack.length)
      console.log('RedoStack content:', this.redoStack)
      if (this.jm && this.redoStack.length > 0) {
        const operation = this.redoStack.pop()
        console.log('Redo operation:', operation)
        this.undoStack.push(operation)
        
        switch (operation.type) {
          case 'add': {
            // 对于添加操作，重做就是重新添加该节点
            if (operation.parent && operation.node) {
              const parentNode = this.jm.get_node(operation.parent)
              if (parentNode) {
                // 使用原始方法，避免再次触发操作记录
                this.originalAddNode.call(this.jm, parentNode, operation.node.id, operation.node.topic)
              } else {
                console.log('Parent node not found:', operation.parent)
              }
            } else {
              console.log('Invalid add operation:', operation)
            }
            break
          }
          case 'remove': {
            // 对于删除操作，重做就是删除该节点
            const nodeToRemove = this.jm.get_node(operation.node.id)
            if (nodeToRemove) {
              // 使用原始方法，避免再次触发操作记录
              this.originalRemoveNode.call(this.jm, nodeToRemove)
            } else {
              console.log('Node to remove not found:', operation.node.id)
            }
            break
          }
          case 'update': {
            // 对于更新操作，重做就是恢复到新的主题
            const nodeToUpdate = this.jm.get_node(operation.node.id)
            if (nodeToUpdate) {
              // 使用原始方法，避免再次触发操作记录
              this.originalUpdateNode.call(this.jm, nodeToUpdate, operation.newTopic)
            } else {
              console.log('Node to update not found:', operation.node.id)
            }
            break
          }
        }
        console.log('Redo performed:', operation.type)
      } else {
        console.log('Redo not performed, either jm is null or redoStack is empty')
      }
    },
    
    // 测试方法：检查栈的内容
    checkStacks() {
      console.log('UndoStack length:', this.undoStack.length)
      console.log('UndoStack content:', this.undoStack)
      console.log('RedoStack length:', this.redoStack.length)
      console.log('RedoStack content:', this.redoStack)
    },
    // ========== 导出功能 ==========
    async exportCommon(type, id) {
      try {
        if (!id) {
          this.$emit('canvasError', '脑图ID为空，无法导出', 'error')
          return
        }
        
        this.$emit('canvasError', `正在导出${type.toUpperCase()}格式...`, 'info')
        const res = await fetch(`/api/mindmaps/${id}/export/${type}`, {credentials: 'include'})
        
        if (!res.ok) {
          throw new Error(`后端导出失败，状态码：${res.status}`)
        }
        
        const blob = await res.blob()
        this.downloadFile(blob, type)
        this.$emit('canvasError', `${type.toUpperCase()}导出成功`, 'success')
        this.$root.showExportModal = false
      } catch (err) {
        this.$emit('canvasError', `导出失败：${err.message}`, 'error')
      }
    },
    async exportAsImage(id) {
      try {
        this.$emit('canvasError', '正在生成图片...', 'info')
        const res = await fetch(`/api/mindmaps/${id}/export/image`, {credentials: 'include'})
        if(res.ok) {
          const blob = await res.blob()
          this.downloadFile(blob, 'png')
          this.$emit('canvasError', '图片导出成功', 'success')
          this.$root.showExportModal = false
        } else { throw new Error('后端导出失败') }
      } catch (err) {
        this.$emit('canvasError', '后端导出失败，尝试前端导出', 'warning')
        this.frontendExportAsImage()
      }
    },
    frontendExportAsImage() {
      try {
        this.$emit('canvasError', '前端生成图片中...', 'info')
        const container = document.getElementById('jsmind_container')
        if (!container) {
          throw new Error('无法找到脑图画布容器')
        }
        
        html2canvas(container, {
          scale: 2, // 提高图片质量
          useCORS: true, // 允许跨域图片
          logging: false, // 禁用日志
          backgroundColor: '#ffffff' // 设置白色背景
        }).then(canvas => {
          try {
            const image = canvas.toDataURL('image/png')
            const a = document.createElement('a')
            a.href = image
            a.download = `智联笔记-${Date.now()}.png`
            document.body.appendChild(a)
            a.click()
            document.body.removeChild(a)
            this.$emit('canvasError', '前端图片导出成功', 'success')
            this.$root.showExportModal = false
          } catch (err) {
            this.$emit('canvasError', `前端导出失败：${err.message}`, 'error')
          }
        }).catch(err => {
          this.$emit('canvasError', `前端生成图片失败：${err.message}`, 'error')
        })
      } catch (err) {
        this.$emit('canvasError', `前端导出初始化失败：${err.message}`, 'error')
      }
    },
    downloadFile(blob, suffix) {
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `智联笔记-${Date.now()}.${suffix}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    },
    // ========== 标签操作 ==========
    async createTag(name, color) { await createTag({name, color}) },
    async updateTag(id, name, color) { await updateTag(id, {name, color}) },
    async deleteTag(id) { await deleteTag(id) },
    async toggleMindmapTag(mid, tid, checked) {
      if (checked) {
        await bindTagToMindmap(mid, { tag_id: tid })
      } else {
        await unbindTagFromMindmap(mid, tid)
      }
    },
    // ========== 版本操作 ==========
    async loadVersions(id) {
      const res = await getVersionList(id)
      return res.data
    },
    async createVersion(id, params) {
      await createVersion(id, params)
    },
    async createManualVersion(id) {
      const desc = document.getElementById('versionDescription').value.trim() || '手动创建版本'
      await createVersion(id, {change_description: desc})
    },
    async getVersionDetail(mapId, verId) {
      const res = await getVersionDetail(mapId, verId)
      return res.data
    },
    async restoreVersion(mapId, verId) {
      await restoreVersion(mapId, verId)
    },
    // ========== 评论加载 ==========
    async loadComments(id) {
      try {
        const res = await fetch(`/api/mindmaps/${id}/comments`, {credentials: 'include'})
        this.comments = await res.json()
        this.commentCount = this.comments.reduce((t,c)=>t+1+(c.replies?.length||0),0)
        this.$root.commentCount = this.commentCount
      } catch (err) {
        this.$emit('canvasError', '加载评论失败', 'error')
      }
    }
  }
}
</script>

<style scoped>
.mindbox{
  flex:1;
  position:relative;
  background:#fff;
  min-width: 0;
  height: 100%;
  overflow: hidden;
}
#jsmind_container{
  width:100%;
  height:100%;
}
</style>