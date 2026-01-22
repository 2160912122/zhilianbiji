<template>
  <div class="modal" v-show="modelValue" @click.self="$emit('update:modelValue', false)">
    <div>
        <h4>新建脑图</h4>
        <input v-model="localName" placeholder="脑图名称" @input="$emit('updateForm', {name: localName, topic: localTopic})">
        <input v-model="localTopic" placeholder="中心主题" @input="$emit('updateForm', {name: localName, topic: localTopic})">
      <footer>
        <button @click="$emit('update:modelValue', false)">取消</button>
        <button class="ok" @click="$emit('createMap')">创建</button>
      </footer>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NewMapModal',
  props: {
    modelValue: { type: Boolean, default: false },
      mName: { type: String, default: '' },
      mTopic: { type: String, default: '' }
  },
  data() {
      return {
        localName: this.mName,
        localTopic: this.mTopic
      }
  },
  watch: {
      modelValue(val) { if(!val) { this.localName=''; this.localTopic='' } },
      mName: { handler(val) { this.localName = val }, immediate: true },
      mTopic: { handler(val) { this.localTopic = val }, immediate: true },
      localName: { handler(val) { this.$emit('updateForm', {name: val, topic: this.localTopic}) } , immediate: false},
      localTopic: { handler(val) { this.$emit('updateForm', {name: this.localName, topic: val}) } , immediate: false}
  }
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
  width:360px;
  box-shadow:0 4px 20px rgba(0,0,0,.15);
  max-width: 90vw;
}
.modal h4{ margin-bottom:16px; font-size:18px; }
.modal input{
  width:100%;
  padding:10px 12px;
  margin-bottom:14px;
  border:1px solid #dcdfe6;
  border-radius:4px;
}
.modal footer{
  display:flex;
  justify-content:flex-end;
  gap:10px;
}
.modal footer button{
  padding:6px 14px;
  border:none;
  border-radius:4px;
  cursor:pointer;
}
.modal footer .ok{
  background:#409eff;
  color:#fff;
}
</style>