<template>
  <Transition name="fade">
    <div v-if="visible" class="loading-overlay">
      <div class="overlay-content">
        <el-icon class="loading-icon" :size="48">
          <Loading />
        </el-icon>
        <p v-if="message" class="loading-message">{{ message }}</p>
        <div v-if="showProgress && progress !== undefined" class="progress-container">
          <el-progress :percentage="progress" :show-text="true" />
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { Loading } from '@element-plus/icons-vue'

defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  message: {
    type: String,
    default: '加载中...'
  },
  showProgress: {
    type: Boolean,
    default: false
  },
  progress: {
    type: Number,
    default: undefined
  }
})
</script>

<style scoped>
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.overlay-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  min-width: 300px;
}

.loading-icon {
  color: #409eff;
  animation: rotate 1.5s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.loading-message {
  font-size: 16px;
  color: #303133;
  margin: 0;
}

.progress-container {
  width: 100%;
  min-width: 200px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
