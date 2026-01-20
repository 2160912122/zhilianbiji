<template>
  <div class="note-type-select-container">
    <h1>创建新笔记</h1>
    <div class="note-types">
      <div class="note-type-card" @click="createNote('richtext')">
        <i class="fa fa-file-text-o"></i>
        <h2>空白文档</h2>
        <p>创建一个富文本格式的空白文档</p>
      </div>
      <div class="note-type-card" @click="createNote('markdown')">
        <i class="fa fa-file-code-o"></i>
        <h2>Markdown笔记</h2>
        <p>创建一个支持Markdown格式的笔记</p>
      </div>
    </div>
    <div class="actions">
      <router-link to="/notes" class="btn btn-secondary">返回列表</router-link>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const createNote = (type) => {
  // 跳转到创建笔记页面，并传递笔记类型作为路径参数
  router.push({ path: `/notes/create/${type}` })
}
</script>

<style scoped>
.note-type-select-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 0 20px;
  text-align: center;
}

.note-type-select-container h1 {
  margin-bottom: 40px;
  color: #333;
  font-size: 2rem;
}

.note-types {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-bottom: 40px;
  flex-wrap: wrap;
}

.note-type-card {
  width: 300px;
  padding: 40px 20px;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.note-type-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
  border-color: #1976d2;
}

.note-type-card i {
  font-size: 4rem;
  color: #1976d2;
  margin-bottom: 20px;
}

.note-type-card h2 {
  margin-bottom: 10px;
  color: #333;
  font-size: 1.5rem;
}

.note-type-card p {
  color: #666;
  font-size: 1rem;
}

.actions {
  margin-top: 40px;
}
</style>