<template>
  <div class="empty-box">
    <van-icon name="file-text-o" size="60" color="#c8c9cc" />
    <p class="empty-text">暂无脑图笔记</p>
    <van-button type="primary" round size="small" @click="emit('createMindMap')">
      创建我的第一个脑图
    </van-button>
  </div>
</template>

<script setup name="HomeEmpty">
import { defineEmits } from 'vue'
const emit = defineEmits(['createMindMap'])
</script>

<style lang="scss" scoped>
.empty-box {
  text-align: center;
  padding: 60px 0;
  .empty-text {
    font-size: 14px;
    color: #969799;
    margin: 12px 0 20px;
  }
}
</style>