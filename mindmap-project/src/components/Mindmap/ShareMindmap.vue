<template>
  <div class="container">
    <div class="header">
      <h1>{{ mindmap.name || '加载中...' }}</h1>
      <p>分享自 智联笔记</p>
      <div :class="['permission-badge', permissionClass]" id="permissionBadge">{{ permissionText }}</div>
      <div id="timeInfo" style="margin-top:10px;font-size:14px;color:#666;">{{ timeInfo }}</div>
    </div>
    <div class="mind-container">
      <div v-if="isLoading" class="loading-message">
        <div class="loading-spinner"></div>
        <p>脑图加载中...</p>
      </div>
      <div v-else>
        <div id="toolbar" class="toolbar" v-show="isEditable">
          <button @click="addChild">+子节点</button>
          <button @click="addBrother">+兄弟节点</button>
          <button @click="editNode">编辑</button>
          <button @click="removeNode">删除</button>
          <button @click="saveMap">保存</button>
        </div>
        <div id="saveNotice" class="save-notice" v-show="showSaveNotice">保存成功</div>
        <div id="jsmind_container" style="width:100%;height:500px"></div>
        <div id="errorContainer" class="error-message" v-show="showError">{{ errorMsg }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import { getShareMindmap, updateShareMindmap } from '@/api/mindmapApi'
export default {
  name: 'ShareMindmap',
  data() {
    return {
      jm: null,
      mindmap: {},
      isEditable: false,
      mindmapId: this.$route.params.mid, // 从路由参数获取脑图ID
      shareType: this.$route.params.share_type, // 从路由参数获取分享类型
      permissionText: '',
      permissionClass: '',
      timeInfo: '',
      showSaveNotice: false,
      showError: false,
      errorMsg: '',
      isLoading: false
    }
  },
  mounted() {
    // 确保DOM完全加载后再初始化脑图
    this.$nextTick(() => {
      this.loadShareMindmap().catch(err => {
        console.error('加载脑图失败:', err)
        this.showError = true
        this.errorMsg = '加载脑图失败: ' + err.message
        this.isLoading = false
      })
    })
  },
  methods: {
    async loadShareMindmap() {
      this.isLoading = true
      this.showError = false
      try {
        const res = await getShareMindmap(this.shareType, this.mindmapId) // 传递分享类型和脑图ID参数
        this.mindmap = res.data
        // 根据分享类型判断是否可编辑
        this.isEditable = this.shareType === 'editable'
        this.permissionText = this.isEditable ? '可编辑' : '只读'
        this.permissionClass = this.isEditable ? 'permission-editable' : 'permission-readonly'
        this.timeInfo = res.data.is_expired ? '❌ 分享链接已过期' : res.data.remaining_time ? `⏰ 剩余时间: ${res.data.remaining_time}` : '✅ 永久有效'
        
        // 设置isLoading为false，确保容器元素渲染出来
        this.isLoading = false
        
        // 等待DOM更新后再初始化脑图
        this.$nextTick(() => {
          try {
            this.initJSMind(res.data)
          } catch (initError) {
            console.error('初始化脑图失败:', initError)
            this.showError = true
            this.errorMsg = '脑图加载失败: ' + initError.message
          }
        })
      } catch (err) {
        this.showError = true
        this.errorMsg = err.response?.status === 410 ? '分享链接已过期' : err.response?.status === 400 ? '分享链接无效' : '加载脑图失败: ' + err.message
        this.isLoading = false
      }
    },
    initJSMind(data) {
      try {
        // 确保window.jsMind存在
        const J = window.jsMind || window.jsmind
        if (!J) {
          throw new Error('jsMind库未加载')
        }
        
        // 检查容器元素是否存在
        const containerEl = document.getElementById('jsmind_container')
        if (!containerEl) {
          throw new Error('脑图容器元素不存在')
        }
        
        // 初始化jsMind实例
        if (!this.jm) {
          this.jm = new J({
            container: 'jsmind_container',
            theme: 'primary',
            editable: this.isEditable
          })
        }
        
        // 处理脑图数据
        let mindData = data.data
        if (typeof mindData === 'string') {
          try {
            mindData = JSON.parse(mindData)
          } catch (parseError) {
            throw new Error('脑图数据JSON解析失败: ' + parseError.message)
          }
        }
        
        // 检查mindData是否为null或undefined
        if (!mindData) {
          // 如果脑图数据为空，创建默认结构
          mindData = {
            meta: { name: data.name || '默认脑图' },
            format: 'node_tree',
            data: {
              id: 'root',
              topic: '中心主题',
              children: []
            }
          }
        }
        
        // 确保mindData包含有效的jsmind数据结构
        if (mindData.id && !mindData.format) {
          mindData = { meta: { name: data.name }, format: 'node_tree', data: mindData }
        }
        
        // 检查必要的字段
        if (!mindData.format || !mindData.data) {
          // 如果缺少必要字段，创建默认结构
          mindData = {
            meta: { name: data.name || '默认脑图' },
            format: 'node_tree',
            data: {
              id: 'root',
              topic: '中心主题',
              children: []
            }
          }
        } else {
          // 检查根节点
          const rootNode = mindData.format === 'node_tree' ? mindData.data : mindData.data.root
          if (!rootNode || !rootNode.id) {
            // 如果根节点无效，创建默认根节点
            mindData = {
              meta: { name: data.name || '默认脑图' },
              format: 'node_tree',
              data: {
                id: 'root',
                topic: '中心主题',
                children: []
              }
            }
          }
        }
        
        // 显示脑图
        if (this.jm) {
          this.jm.show(mindData)
        } else {
          throw new Error('jsMind实例未初始化')
        }
      } catch (err) {
        console.error('初始化脑图失败:', err)
        this.showError = true
        this.errorMsg = '脑图加载失败: ' + err.message
      }
    },
    // 编辑/保存等原有方法
    addChild() {
      const selectedNode = this.jm.get_selected_node()
      if (selectedNode) {
        // 生成唯一的节点ID并设置正确的主题文本
        const nodeId = `node_${Date.now()}`
        this.jm.add_node(selectedNode, nodeId, '新子节点')
      } else {
        alert('请先选择一个节点')
      }
    },
    addBrother() {
      const selectedNode = this.jm.get_selected_node()
      if (selectedNode && selectedNode.parent) {
        // 生成唯一的节点ID并设置正确的主题文本
        const nodeId = `node_${Date.now()}`
        this.jm.add_node(selectedNode.parent, nodeId, '新兄弟节点')
      } else {
        alert('请先选择一个节点')
      }
    },
    editNode() {
      const selectedNode = this.jm.get_selected_node()
      if (selectedNode) {
        // 使用begin_edit方法启动节点编辑模式
        this.jm.begin_edit(selectedNode)
      } else {
        alert('请先选择一个节点')
      }
    },
    removeNode() {
      const selectedNode = this.jm.get_selected_node()
      if (selectedNode && selectedNode.parent) {
        if (confirm('确定要删除这个节点吗？')) {
          this.jm.remove_node(selectedNode)
        }
      } else {
        alert('请先选择一个节点')
      }
    },
    async saveMap() {
      const data = this.jm.get_data()
      await updateShareMindmap(this.mindmapId, { data })
      this.showSaveNotice = true
      setTimeout(()=>this.showSaveNotice=false,2000)
    }
  },
  unmounted() {
    // 组件销毁时清理jsMind实例
    if (this.jm) {
      // 尝试清理jsMind实例
      try {
        // 如果jsMind实例有destroy方法，调用它
        if (typeof this.jm.destroy === 'function') {
          this.jm.destroy()
        }
      } catch (error) {
        console.error('清理jsMind实例失败:', error)
      } finally {
        this.jm = null
      }
    }
  }
}
</script>

<style scoped>
        *{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei"}
        body{background:#f5f7fa;padding:20px}
        .container{max-width:1200px;margin:0 auto;background:#fff;border-radius:8px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,.1)}
        .header{margin-bottom:20px;text-align:center;position:relative}
        .permission-badge{
            position:absolute;
            top:10px;
            right:10px;
            padding:4px 8px;
            border-radius:12px;
            font-size:12px;
            font-weight:500;
        }
        .permission-readonly{background:#e6f7ff;color:#1890ff;}
        .permission-editable{background:#f6ffed;color:#52c41a;}
        .mind-container{height:600px;border:1px solid #e4e7ed;border-radius:4px;position:relative}
        .toolbar{
            position:absolute;
            top:10px;
            left:10px;
            background:rgba(255,255,255,0.9);
            padding:8px;
            border-radius:4px;
            box-shadow:0 2px 8px rgba(0,0,0,0.1);
            z-index:100;
            display:flex;
            gap:5px;
        }
        .toolbar button{
            padding:6px;
            border:1px solid #d9d9d9;
            background:#fff;
            border-radius:4px;
            cursor:pointer;
            font-size:14px;
        }
        .toolbar button:hover{
            border-color:#409eff;
            color:#409eff;
        }
        .save-notice{
            position:absolute;
            top:10px;
            right:10px;
            background:#f6ffed;
            border:1px solid #b7eb8f;
            padding:8px 12px;
            border-radius:4px;
            font-size:14px;
            display:none;
        }
        .error-message{
            text-align:center;
            padding:50px;
            color:#f56c6c;
            background:#fef0f0;
            border:1px solid #fbc4c4;
            border-radius:4px;
            margin:20px 0;
        }

        .expired-message {
            text-align: center;
            padding: 50px;
            color: #fa541c;
            background: #fff2e8;
            border: 1px solid #ffbb96;
            border-radius: 4px;
            margin: 20px 0;
        }
        
        .loading-message {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 500px;
            text-align: center;
            color: #409eff;
            background: #ecf5ff;
            border: 1px solid #d9ecff;
            border-radius: 4px;
        }
        
        .loading-spinner {
            border: 4px solid rgba(64, 158, 255, 0.3);
            border-radius: 50%;
            border-top: 4px solid #409eff;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
</style>