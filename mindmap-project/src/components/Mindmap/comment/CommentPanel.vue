<template>
  <div class="comment-panel" v-show="modelValue">
    <div class="comment-panel-header">
      <h4 style="margin: 0;">💬 脑图评论</h4>
      <button class="icon-btn" @click="$emit('update:modelValue', false)" style="border: none; background: none; color: #606266;">
        <i class="fas fa-times"></i>
      </button>
    </div>

    <div class="comment-panel-content" id="commentList">
      <div v-if="!comments.length" style="text-align:center;padding:40px;color:#999">暂无评论，快来抢占沙发吧</div>
      <div v-for="c in comments" :key="c.id" class="comment-item" :data-comment-id="c.id">
        <div class="comment-header">
          <span class="comment-author">{{c.username}}</span>
          <span class="comment-time">{{formatTime(c.created_at)}}</span>
        </div>
        <div class="comment-content">{{escapeHtml(c.content)}}</div>
        <div class="comment-actions">
          <span @click="replyComment(c)" class="comment-action"><i class="fas fa-reply"></i> 回复</span>
          <span v-if="currentUser && c.user_id == currentUser.id" @click="editComment(c.id)" class="comment-action"><i class="fas fa-edit"></i> 编辑</span>
          <span v-if="currentUser && c.user_id == currentUser.id" @click="deleteComment(c.id)" class="comment-action" style="color:#f56c6c;"><i class="fas fa-trash"></i> 删除</span>
          <span v-if="c.node_id" @click="highlightNode(c.node_id)" class="comment-action"><i class="fas fa-crosshairs"></i> 定位</span>
        </div>
        <div v-for="r in c.replies" :key="r.id" class="comment-item reply">
          <div class="comment-header"><span>{{r.username}}</span><span>{{formatTime(r.created_at)}}</span></div>
          <div class="comment-content">{{escapeHtml(r.content)}}</div>
        </div>
      </div>
    </div>

    <div class="comment-panel-footer">
      <div class="comment-form">
        <textarea
          id="commentInput"
          class="comment-textarea"
          placeholder="添加评论... (支持@节点关联)"
          @keydown="handleCommentKeydown($event)"
          v-model="commentContent"
        ></textarea>
        <div class="comment-form-actions">
          <div>
            <button class="btn" @click="addCommentAtPosition()" style="font-size:12px;">
              <i class="fas fa-map-marker-alt"></i> 在当前位置添加
            </button>
            <button class="btn" @click="addCommentToSelectedNode()" style="font-size:12px;">
              <i class="fas fa-crosshairs"></i> 关联选中节点
            </button>
          </div>
          <button class="btn primary" @click="submitComment()">
            <i class="fas fa-paper-plane"></i> 发送
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getCommentList, addComment, updateComment, deleteComment } from '@/api/mindmapApi'

export default {
  name: 'CommentPanel',
  props: {
    modelValue: { type: Boolean, default: false },
    currentId: { type: [String, Number], default: null },
      currentUser: { type: Object, default: () => ({}) }
  },
  data() {
    return {
      comments: [],
      commentContent: '',
      currentCommentPosition: null,
      commentMarkers: []
    }
  },
  watch: {
    modelValue(val) {
      val ? this.loadComments(this.currentId) : this.clearCommentMarkers()
    }
  },
  methods: {
    formatTime(timestamp) {
      if(!timestamp) return '未知时间'
      const date = new Date(timestamp)
      const now = new Date()
      const diffMs = now - date
      const diffMins = Math.floor(diffMs/60000)
      const diffHours = Math.floor(diffMs/3600000)
      const diffDays = Math.floor(diffMs/86400000)
      if(diffMins<1) return '刚刚'
      if(diffMins<60) return `${diffMins}分钟前`
      if(diffHours<24) return `${diffHours}小时前`
      if(diffDays<7) return `${diffDays}天前`
      return date.toLocaleDateString('zh-CN', {month: 'short', day: 'numeric'})
    },
    escapeHtml(str) {
      if(!str) return ''
      return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>')
    },
    async loadComments(id) {
      try {
        const res = await getCommentList(id)
        this.comments = res.data || []
        this.renderCommentMarkers()
      } catch (err) {
        this.$emit('showToast', '加载评论失败', 'error')
      }
    },
    renderCommentMarkers() {
      this.clearCommentMarkers()
      this.comments.forEach(c => {
        if(c.x && c.y) {
          const marker = document.createElement('div')
          marker.className = 'comment-marker'
          marker.style.left = c.x+'px'
          marker.style.top = c.y+'px'
          marker.innerHTML = '<i class="fas fa-comment"></i>'
          marker.onclick = () => this.scrollToComment(c.id)
          document.querySelector('.mindbox').appendChild(marker)
          this.commentMarkers.push(marker)
        }
      })
    },
    clearCommentMarkers() {
      this.commentMarkers.forEach(m => m.remove())
      this.commentMarkers = []
    },
    scrollToComment(id) {
      const el = document.querySelector(`[data-comment-id="${id}"]`)
      el && el.scrollIntoView({behavior:'smooth', block:'center'})
    },
    addCommentAtPosition() {
      const jm = this.$root.jm
      if(!jm) return this.$emit('showToast', '脑图未初始化', 'warning')
      const view = jm.view
      this.currentCommentPosition = {
        x: view.elements.container.clientWidth/2,
        y: view.elements.container.clientHeight/2
      }
      this.commentContent = ''
      this.$nextTick(()=>document.getElementById('commentInput').focus())
    },
    addCommentToSelectedNode() {
      const jm = this.$root.jm
      if(!jm) return this.$emit('showToast', '脑图未初始化', 'warning')
      const node = jm.get_selected_node()
      if(!node) return this.$emit('showToast', '请先选中一个节点', 'warning')
      const el = document.querySelector(`[nodeid="${node.id}"]`)
      const rect = el.getBoundingClientRect()
      const mRect = document.querySelector('.mindbox').getBoundingClientRect()
      this.currentCommentPosition = {
        x: rect.left + rect.width/2 - mRect.left,
        y: rect.top + rect.height/2 - mRect.top,
        nodeId: node.id
      }
      this.commentContent = ''
      this.$nextTick(()=>document.getElementById('commentInput').focus())
    },
    async submitComment() {
      const content = this.commentContent.trim()
      if(!content) return this.$emit('showToast', '请输入评论内容', 'warning')
      try {
        await addComment(this.currentId, {
          content,
          x: this.currentCommentPosition?.x || null,
          y: this.currentCommentPosition?.y || null,
          node_id: this.currentCommentPosition?.nodeId || null
        })
        this.commentContent = ''
        this.loadComments(this.currentId)
        this.$emit('showToast', '评论发布成功', 'success')
      } catch (err) {
        this.$emit('showToast', '发布失败：'+err.message, 'error')
      }
    },
    handleCommentKeydown(e) { 
      if(e.ctrlKey && e.key === 'Enter') { e.preventDefault(); this.submitComment() }
    },
    replyComment(comment) {
      this.commentContent = `@${comment.username} `
      this.$nextTick(()=>document.getElementById('commentInput').focus())
    },
    async editComment(id) {
      const comment = this.findCommentById(id)
      if(!comment) return this.$emit('showToast', '评论不存在', 'error')
      const content = prompt('编辑您的评论', comment.content)
      if(content === null) return
      if(content.trim()) {
        try {
          await updateComment(this.currentId, id, { content: content.trim() })
          this.loadComments(this.currentId)
          this.$emit('showToast', '评论编辑成功', 'success')
        } catch (err) {
          this.$emit('showToast', '编辑失败：'+err.message, 'error')
        }
      }
    },
    async deleteComment(id) {
      if(!confirm('确定删除该评论吗？')) return
      try {
        await deleteComment(this.currentId, id)
        this.loadComments(this.currentId)
        this.$emit('showToast', '评论删除成功', 'success')
      } catch (err) {
        this.$emit('showToast', '删除失败：'+err.message, 'error')
      }
    },
    highlightNode(nid) {
      const jm = this.$root.jm
      if(!jm) return
      const node = jm.get_node(nid)
      if(node) { jm.select_node(node); this.$emit('showToast', '已定位到关联节点', 'success') }
      else { this.$emit('showToast', '节点已被删除', 'warning') }
    },
    findCommentById(id) {
      for(let c of this.comments) {
        if(c.id == id) return c
        if(c.replies) { for(let r of c.replies) { if(r.id == id) return r } }
      }
      return null
    }
  }
}
</script>

<style scoped>
.comment-panel {
  position: absolute;
  top: 60px;
  right: 20px;
  width: 350px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  max-height: 80vh;
}
.comment-panel-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.comment-panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}
.comment-panel-footer {
  padding: 16px;
  border-top: 1px solid #e4e7ed;
}
.comment-item {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
  border-left: 3px solid #409eff;
}
.comment-item.reply {
  margin-left: 20px;
  background: #f0f9ff;
  border-left-color: #91d5ff;
}
.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.comment-author { font-weight: 500; color: #409eff; }
.comment-time { font-size: 12px; color: #909399; }
.comment-content { color: #606266; line-height: 1.5; margin-bottom: 8px; }
.comment-actions { display: flex; gap: 12px; font-size: 12px; }
.comment-action { color: #909399; cursor: pointer; transition: color 0.2s; }
.comment-action:hover { color: #409eff; }
.comment-form { display: flex; flex-direction: column; gap: 8px; }
.comment-textarea {
  width: 100%;
  min-height: 80px;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  resize: vertical;
  font-family: inherit;
}
.comment-form-actions { display: flex; justify-content: space-between; align-items: center; }
.comment-marker {
  position: absolute;
  width: 20px;
  height: 20px;
  background: #ff4d4f;
  border-radius: 50%;
  cursor: pointer;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  animation: pulse 2s infinite;
}
.btn {
  padding:6px 14px;
  border:none;
  border-radius:4px;
  background:#fff;
  color:#409eff;
  cursor:pointer;
  font-size:12px;
}
.btn.primary {
  background: #409eff;
  color: white;
}
@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}
</style>