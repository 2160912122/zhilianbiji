<template>
  <div>
    <div class="toolbar">
      <button class="btn" @click="$emit('newMap')">新建</button>
      <button class="btn" @click="$emit('saveMap')">保存</button>
      <button class="btn" @click="$emit('exportMap')">导出</button>
      <button class="btn" @click="$emit('shareMap')">分享</button>
      <button class="btn" @click="$emit('manageAllTags')">标签管理</button>
      <button class="btn" @click="$emit('showVersionHistory')">版本历史</button>
      <div style="display: flex; gap: 8px; align-items: center;">
        <button class="ai-btn" @click="$emit('openAIAssistant')">
          <div class="btn-content">
            <i class="fas fa-robot"></i>
            <span class="btn-text">AI助手</span>
          </div>
        </button>
        <button class="ai-btn" @click="$emit('openEnhancedAIAssistant')" style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);">
          <div class="btn-content">
            <i class="fas fa-star"></i>
            <span class="btn-text">AI高级功能</span>
            <span class="ai-feature-tag">NEW</span>
          </div>
        </button>
      </div>
      <button class="comment-btn" @click="$emit('toggleCommentPanel')">
        <i class="fas fa-comments"></i>
        <span class="btn-text">评论</span>
        <span id="commentCountBadge" class="comment-count-badge" v-show="commentCount>0">{{ commentCount }}</span>
      </button>
    </div>
    <div class="editbar">
      <button class="icon-btn" data-tooltip="添加子节点" @click="$emit('addChild')"><i class="fas fa-plus-circle"></i></button>
      <button class="icon-btn" data-tooltip="添加兄弟节点" @click="$emit('addBro')"><i class="fas fa-plus"></i></button>
      <button class="icon-btn" data-tooltip="编辑文字" @click="$emit('editNode')"><i class="fas fa-edit"></i></button>
      <button class="icon-btn" data-tooltip="删除节点" @click="$emit('delNode')"><i class="fas fa-trash"></i></button>
      <div class="divider"></div>
      <button class="icon-btn" data-tooltip="上移" @click="$emit('moveUp')"><i class="fas fa-chevron-up"></i></button>
      <button class="icon-btn" data-tooltip="下移" @click="$emit('moveDown')"><i class="fas fa-chevron-down"></i></button>
      <button class="icon-btn" data-tooltip="展开/收起" @click="$emit('toggleNode')"><i class="fas fa-folder-open"></i></button>
      <div class="divider"></div>
      <button class="icon-btn" data-tooltip="放大" @click="$emit('zoomIn')"><i class="fas fa-search-plus"></i></button>
      <button class="icon-btn" data-tooltip="缩小" @click="$emit('zoomOut')"><i class="fas fa-search-minus"></i></button>
      <button class="icon-btn" data-tooltip="重置缩放" @click="$emit('resetZoom')"><i class="fas fa-expand-arrows-alt"></i></button>
      <div class="divider"></div>
      <button class="icon-btn" data-tooltip="撤销" @click="$emit('undo')"><i class="fas fa-undo"></i></button>
      <button class="icon-btn" data-tooltip="重做" @click="$emit('redo')"><i class="fas fa-redo"></i></button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeToolbar',
  props: {
    commentCount: { type: Number, default: 0 }
  }
}
</script>

<style scoped>
.toolbar{
  height:48px;
  background:#fff;
  border-bottom:1px solid #e4e7ed;
  display:flex;
  align-items:center;
  padding:0 16px;
  gap:10px;
  flex-shrink: 0;
}
.toolbar .btn{
  padding:7px 12px;
  border:1px solid #409eff;
  background:#fff;
  color:#409eff;
  border-radius:4px;
  cursor:pointer;
  font-size:14px;
  flex-shrink: 0;
}
.editbar{
  height: 40px;
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  padding: 0 12px;
  gap: 6px;
  flex-shrink: 0;
  margin-left: 10px;
}
.icon-btn{
  position: relative;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: #606266;
  font-size: 18px;
  cursor: pointer;
  border-radius: 4px;
  transition: background .2s, color .2s;
  flex-shrink: 0;
}
.icon-btn:hover{
  background: #f0f9ff;
  color: #409eff;
}
.divider{
  width: 1px;
  height: 18px;
  background: #dcdfe6;
  margin: 0 4px;
  flex-shrink: 0;
}
.icon-btn::after{
  content: attr(data-tooltip);
  position: absolute;
	top: 100%;
	left: 50%;
	transform: translateX(-50%);
	margin-top: 6px;
	padding: 4px 8px;
	font-size: 12px;
	color: #fff;
	background: #303133;
	border-radius: 4px;
	white-space: nowrap;
	opacity: 0;
	pointer-events: none;
	transition: opacity .2s;
	z-index: 10000;
}
.icon-btn:hover::after{
  opacity: 1;
  transition-delay: .2s;
}
/* AI按钮样式 */
.ai-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  position: relative;
  overflow: hidden;
  flex-shrink: 0;
}
.ai-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}
.ai-btn .btn-content { display: flex; align-items: center; justify-content: center; gap: 8px; }
.ai-feature-tag {
  display: inline-block;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  margin-left: 8px;
  font-weight: 500;
}
/* 评论按钮样式 */
.comment-btn {
  background: linear-gradient(135deg, #52c41a 0%, #73d13d 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(82, 196, 26, 0.3);
  position: relative;
  margin-left: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.comment-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(82, 196, 26, 0.4); }
.comment-count-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ff4d4f;
  color: white;
  border-radius: 10px;
	padding: 2px 6px;
	font-size: 10px;
	min-width: 16px;
	text-align: center;
}
</style>