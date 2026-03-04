<template>
  <div class="pdf-reader">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <p>正在加载PDF...</p>
    </div>

    <!-- 加载失败 -->
    <div v-else-if="error" class="error-state">
      <el-icon :size="60"><DocumentDelete /></el-icon>
      <h3>加载失败</h3>
      <p>{{ error }}</p>
      <el-button type="primary" @click="loadPdf">重新加载</el-button>
    </div>

    <!-- PDF阅读器 -->
    <iframe
      v-show="!loading && !error"
      :src="pdfUrl"
      class="pdf-iframe"
      frameborder="0"
    ></iframe>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  url: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['loadComplete'])

const loading = ref(true)
const error = ref('')
let loadTimer = null

// 带token的PDF URL
const pdfUrl = computed(() => {
  const token = localStorage.getItem('token')
  // 将token作为查询参数传递
  const separator = props.url.includes('?') ? '&' : '?'
  return `${props.url}${separator}token=${token}`
})

const loadPdf = () => {
  loading.value = true
  error.value = ''

  // 设置超时，3秒后自动隐藏loading
  // 因为iframe的load事件在某些情况下不会触发
  if (loadTimer) clearTimeout(loadTimer)
  loadTimer = setTimeout(() => {
    loading.value = false
    emit('loadComplete')
  }, 3000)
}

onMounted(() => {
  loadPdf()
})

onUnmounted(() => {
  if (loadTimer) clearTimeout(loadTimer)
})
</script>

<style scoped>
.pdf-reader {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #1e1e1e;
  position: relative;
}

.loading-overlay,
.error-state {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
  gap: 15px;
  z-index: 10;
}

.error-state p {
  color: #ff6b6b;
  margin: 0;
}

.error-state h3 {
  margin: 0;
}

.pdf-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: #fff;
}
</style>
