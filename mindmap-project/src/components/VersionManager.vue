<template>
  <div class="modal" v-show="showVersionModal" @click.self="closeModal">
    <div style="width:800px;max-height:80vh;overflow-y:auto;">
      <h4>📚 版本历史 - {{ mindmapName }}</h4>
      <div style="margin-bottom:16px;display:flex;gap:10px;align-items:center;">
        <button class="btn primary" @click="createManualVersion">创建手动版本</button>
        <input type="text" v-model="versionDesc" placeholder="输入版本描述" style="flex:1;padding:6px;border:1px solid #dcdfe6;border-radius:4px;">
      </div>
      <div id="versionsList" style="border:1px solid #e4e7ed;border-radius:4px;">
        <div v-for="v in versions" :key="v.id" class="version-item" @click="showVersionDetail(v.id)">
          <!-- 版本列表原有结构 -->
        </div>
      </div>
      <footer><button @click="closeModal">关闭</button></footer>
    </div>
  </div>
</template>

<script>
import { getVersionList, createVersion } from '@/api/versionApi'
export default {
  name: 'VersionManager',
  props: {
    show: Boolean,
    mindmapId: Number,
    mindmapName: String
  },
  data() {
    return {
      versions: [],
      versionDesc: ''
    }
  },
  computed: {
    showVersionModal() { return this.show }
  },
  watch: {
    show(val) { val && this.loadVersions() }
  },
  methods: {
    async loadVersions() {
      const res = await getVersionList(this.mindmapId)
      this.versions = res.data
    },
    async createManualVersion() {
      await createVersion(this.mindmapId, { change_description: this.versionDesc || '手动创建版本' })
      this.loadVersions()
    },
    closeModal() {
      this.$emit('update:show', false)
    }
  }
}
</script>