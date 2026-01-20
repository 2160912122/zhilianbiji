<template>
  <Layout>
    <div class="document-manager-view">
      <h1>文档管理</h1>
      <DocumentManager />
      <div class="divider"></div>
      <h2>表格创建器</h2>
      <TableCreator />
    </div>
  </Layout>
</template>

<script setup>
import Layout from '../components/Layout.vue'
import DocumentManager from '../components/DocumentManager.vue'
import TableCreator from '../components/TableCreator.vue'
</script>

<style scoped>
.document-manager-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  color: var(--text-primary);
  margin-bottom: 30px;
}

h2 {
  color: var(--text-primary);
  margin: 40px 0 20px 0;
}

.divider {
  height: 1px;
  background-color: var(--border-color);
  margin: 40px 0;
}
</style>