<template>
  <div class="modal" v-show="modelValue" @click.self="$emit('update:modelValue', false)">
    <div style="width: 400px;">
      <h4>导出脑图</h4>
      <div style="margin-bottom:16px">
        <p>选择导出格式：</p>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
        <button class="btn primary" @click="$emit('exportAsJson')">
          <i class="fas fa-file-code"></i> JSON
        </button>
        <button class="btn primary" @click="$emit('exportAsText')">
          <i class="fas fa-file-alt"></i> 文本
        </button>
        <button class="btn primary" @click="$emit('exportAsPDF')">
          <i class="fas fa-file-pdf"></i> PDF
        </button>
        <button class="btn primary" @click="$emit('exportAsImage')">
          <i class="fas fa-file-image"></i> 图片
        </button>
      </div>
      <footer style="margin-top:16px;display:flex;justify-content:flex-end;">
        <button class="btn" @click="$emit('update:modelValue', false)">取消</button>
      </footer>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ExportModal',
  props: { modelValue: { type: Boolean, default: false } }
}
</script>

<style scoped>
.modal{
  display:flex !important;
  align-items: center;
  justify-content: center;
  position:fixed;
  inset:0;
  background:rgba(0,0,0,.45);
  z-index:999;
}
.modal>div{
  position:absolute;
  top:50%;
  left:50%;
  transform:translate(-50%,-50%);
  background:#fff;
  padding:28px;
  border-radius:8px;
  box-shadow:0 4px 20px rgba(0,0,0,.15);
  max-width: 90vw;
}
.modal h4{ margin-bottom:16px; font-size:18px; }
.btn.primary {
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}
.btn {
  padding:6px 14px;
  border:1px solid #409eff;
  background:#fff;
  color:#409eff;
  border-radius:4px;
  cursor:pointer;
  font-size:14px;
}
</style>