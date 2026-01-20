<template>
  <div class="container">
    <h1>标签管理</h1>
    <div class="actions">
      <router-link to="/notes" class="btn btn-secondary">返回笔记</router-link>
    </div>
    
    <div class="tag-form">
      <h2>创建新标签</h2>
      <div class="form-group">
        <input 
          type="text" 
          v-model="newTagName" 
          class="form-control"
          placeholder="输入标签名称"
        />
      </div>
      <button class="btn btn-primary" @click="createTag">创建标签</button>
    </div>
    
    <div class="tags-list">
      <h2>现有标签</h2>
      <div class="tags-cloud">
        <span 
          v-for="tag in tags" 
          :key="tag.id" 
          class="tag-item"
        >
          {{ tag.name }}
          <button class="tag-remove" @click="deleteTag(tag.id)">&times;</button>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { tagService } from '../services/tag.js'

const tags = ref([])
const newTagName = ref('')

onMounted(() => {
  loadTags()
})

async function loadTags() {
  try {
    tags.value = await tagService.getTags()
  } catch (error) {
    console.error('加载标签失败:', error)
    alert('加载标签失败')
  }
}

async function createTag() {
  if (!newTagName.value.trim()) {
    alert('标签名称不能为空')
    return
  }
  
  try {
    await tagService.createTag({ name: newTagName.value.trim() })
    newTagName.value = ''
    loadTags()
    alert('标签创建成功')
  } catch (error) {
    console.error('创建标签失败:', error)
    alert('创建标签失败')
  }
}

async function deleteTag(tagId) {
  if (confirm('确定要删除这个标签吗？')) {
    try {
      await tagService.deleteTag(tagId)
      loadTags()
      alert('标签删除成功')
    } catch (error) {
      console.error('删除标签失败:', error)
      alert('删除标签失败')
    }
  }
}
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.actions {
  margin-bottom: 20px;
}

.tag-form {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.tag-form h2 {
  margin-top: 0;
  margin-bottom: 15px;
}

.form-group {
  margin-bottom: 15px;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.tags-list h2 {
  margin-bottom: 15px;
}

.tags-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.tag-item {
  background-color: #e3f2fd;
  color: #1565c0;
  padding: 8px 15px;
  border-radius: 16px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.tag-remove {
  background: none;
  border: none;
  color: #1565c0;
  cursor: pointer;
  font-size: 16px;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>