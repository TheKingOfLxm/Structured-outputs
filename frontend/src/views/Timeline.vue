<template>
  <div class="timeline-page">
    <div class="content-wrapper">
      <el-card class="timeline-card">
        <template #header>
          <div class="card-header">
            <el-button link @click="goBack">
              <el-icon><ArrowLeft /></el-icon>
              返回
            </el-button>
            <div class="header-title">
              <el-icon><Clock /></el-icon>
              <span>研究时间线</span>
            </div>
            <div class="header-actions">
              <el-button @click="handleRegenerate" :loading="regenerating">
                <el-icon><Refresh /></el-icon>
                重新生成
              </el-button>
              <el-button @click="handleExport">
                <el-icon><Download /></el-icon>
                导出
              </el-button>
            </div>
          </div>
        </template>

        <div v-if="paper" class="paper-info">
          <h3>{{ paper.title }}</h3>
        </div>

        <div v-loading="loading" class="timeline-container">
          <div v-if="!loading && !timelineData.length" class="empty-state">
            <el-icon :size="64"><Clock /></el-icon>
            <p>暂无时间线数据</p>
            <el-button type="primary" @click="handleRegenerate">生成时间线</el-button>
          </div>

          <el-timeline v-else-if="timelineData.length">
            <el-timeline-item
              v-for="(item, index) in timelineData"
              :key="index"
              :timestamp="item.time || item.year"
              placement="top"
              :type="getTimelineType(index)"
              :color="getTimelineColor(index)"
            >
              <el-card>
                <h4>{{ item.title || item.event }}</h4>
                <p v-if="item.description">{{ item.description }}</p>
                <div v-if="item.keywords && item.keywords.length" class="keywords">
                  <el-tag
                    v-for="keyword in item.keywords"
                    :key="keyword"
                    size="small"
                    class="keyword-tag"
                  >
                    {{ keyword }}
                  </el-tag>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { paperApi, generateApi } from '@/api'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const regenerating = ref(false)
const paper = ref(null)
const timelineData = ref([])

const loadPaperInfo = async () => {
  try {
    const res = await paperApi.getPaperDetail(route.params.id)
    paper.value = res.data
  } catch (error) {
    console.error('加载失败:', error)
  }
}

const loadTimeline = async () => {
  loading.value = true
  try {
    const res = await generateApi.getGenerateHistory(route.params.id)
    const timelineItem = res.data.list?.find(item => item.type === 'timeline')
    if (timelineItem && timelineItem.content) {
      timelineData.value = JSON.parse(timelineItem.content)
    }
  } catch (error) {
    console.error('加载失败:', error)
  } finally {
    loading.value = false
  }
}

const handleRegenerate = async () => {
  regenerating.value = true
  try {
    await generateApi.generateTimeline({ paperId: route.params.id })
    ElMessage.success('生成成功')
    setTimeout(() => {
      loadTimeline()
    }, 1000)
  } catch (error) {
    console.error('生成失败:', error)
    ElMessage.error('生成失败，请重试')
  } finally {
    regenerating.value = false
  }
}

const handleExport = () => {
  if (!timelineData.value.length) {
    ElMessage.warning('请先生成时间线')
    return
  }

  // 生成图片或导出数据
  const dataStr = JSON.stringify(timelineData.value, null, 2)
  const blob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `时间线-${paper.value?.title || '论文'}.json`
  link.click()
  URL.revokeObjectURL(url)
}

const getTimelineType = (index) => {
  const types = ['primary', 'success', 'warning', 'danger', 'info']
  return types[index % types.length]
}

const getTimelineColor = (index) => {
  const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399']
  return colors[index % colors.length]
}

const goBack = () => {
  router.push(`/paper/${route.params.id}`)
}

onMounted(() => {
  loadPaperInfo()
  loadTimeline()
})
</script>

<style scoped>
.timeline-page {
  height: 100%;
}

.content-wrapper {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.timeline-card {
  min-height: calc(100vh - 120px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.paper-info {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.paper-info h3 {
  font-size: 16px;
  color: #303133;
  margin: 0;
}

.timeline-container {
  min-height: 400px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #909399;
}

.empty-state p {
  margin-bottom: 20px;
}

.el-timeline :deep(.el-timeline-item__timestamp) {
  font-weight: 600;
  color: #303133;
}

.el-timeline :deep(.el-card) {
  border-radius: 8px;
}

.el-timeline h4 {
  font-size: 16px;
  color: #303133;
  margin: 0 0 10px;
}

.el-timeline p {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin: 10px 0;
}

.keywords {
  margin-top: 10px;
}

.keyword-tag {
  margin-right: 8px;
}
</style>
