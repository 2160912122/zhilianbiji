<template>
  <van-popup
    v-model:show="isShowModal"
    position="center"
    round
    closeable
    close-icon-position="top-right"
    overlay-closeable
    class="version-modal"
    @close="handleModalClose"
  >
    <div class="modal-header">
      <h3 class="modal-title">版本历史</h3>
      <p class="modal-desc">查看、恢复或删除历史版本</p>
    </div>

    <div class="modal-content">
      <div v-if="loading" class="empty">加载中…</div>
      <div v-else>
        <div v-if="versions.length === 0" class="empty">暂无版本</div>
        <div class="version-list">
          <div v-for="v in versions" :key="v.id" class="version-item">
            <div class="meta">
              <div class="title">{{ v.change_description || v.description || ('版本 ' + v.id) }}</div>
              <div class="time">{{ formatTime(v.created_at || v.create_time || v.created || v.updated_at) }}</div>
            </div>
            <div class="actions">
              <van-button size="small" type="primary" plain @click="showDetail(v)">详情</van-button>
              <van-button size="small" type="danger" plain @click="confirmRestore(v)">恢复</van-button>
              <van-button size="small" plain @click="confirmDelete(v)">删除</van-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="modal-footer">
      <van-button type="default" round class="btn cancel-btn" @click="handleModalClose">关闭</van-button>
    </div>
  </van-popup>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue'
import { getVersionList, getVersionDetail, restoreVersion, deleteVersion } from '@/api/versionApi'
import { showToast, showConfirmDialog } from 'vant'

const props = defineProps({
  show: { type: Boolean, default: false },
  mindmapId: { type: [String, Number], default: null }
})
const emit = defineEmits(['update:show', 'restore'])

const isShowModal = ref(props.show)
const versions = ref([])
const loading = ref(false)

watch(
  () => props.show,
  (val) => {
    isShowModal.value = val
    if (val) loadVersions()
  },
  { immediate: true }
)

async function loadVersions() {
  if (!props.mindmapId) return
  loading.value = true
  try {
    const res = await getVersionList(props.mindmapId)
    versions.value = (res && res.data) || []
  } catch (e) {
    console.error(e)
    showToast('获取版本列表失败')
  } finally {
    loading.value = false
  }
}

function handleModalClose() {
  isShowModal.value = false
  emit('update:show', false)
}

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  if (isNaN(d.getTime())) return t
  return d.toLocaleString()
}

async function showDetail(v) {
  try {
    const res = await getVersionDetail(props.mindmapId, v.id)
    const data = (res && res.data) || res || {}
    // 简单展示版本详情
    await showConfirmDialog({
      title: '版本详情',
      message: JSON.stringify(data, null, 2),
      confirmButtonText: '关闭'
    })
  } catch (e) {
    console.error(e)
    showToast('获取版本详情失败')
  }
}

async function confirmRestore(v) {
  try {
    await showConfirmDialog({ title: '恢复确认', message: '确定要将该版本恢复到当前脑图吗？' })
    await restoreVersion(props.mindmapId, v.id)
    showToast('已恢复版本')
    emit('restore', v)
    handleModalClose()
  } catch (e) {
    // 取消或出错
  }
}

async function confirmDelete(v) {
  try {
    await showConfirmDialog({ title: '删除确认', message: '确定要删除该版本吗？此操作不可恢复', confirmButtonText: '删除', confirmButtonColor: '#ee0a24' })
    await deleteVersion(props.mindmapId, v.id)
    showToast('版本已删除')
    loadVersions()
  } catch (e) {
    // 取消或出错
  }
}
</script>

<style scoped>
.version-modal {
  width: 92%;
  max-width: 720px;
  padding: 18px 16px;
  box-sizing: border-box;
}
.modal-header { text-align: center; margin-bottom: 12px }
.modal-title { font-size: 18px; margin: 0; font-weight: 600 }
.modal-desc { font-size: 13px; color: #888; margin: 6px 0 0 }
.modal-content { max-height: 60vh; overflow: auto; margin: 12px 0 }
.empty { text-align: center; color: #999; padding: 24px 0 }
.version-list { display: flex; flex-direction: column; gap: 8px }
.version-item { display: flex; justify-content: space-between; align-items: center; padding: 10px; border: 1px solid #eef0f2; border-radius: 8px }
.version-item .meta { display: flex; flex-direction: column }
.version-item .title { font-weight: 500 }
.version-item .time { font-size: 12px; color: #999; margin-top: 4px }
.actions { display: flex; gap: 8px }
.modal-footer { display:flex; justify-content:flex-end; margin-top: 12px }
.btn { min-width: 96px }
</style>
