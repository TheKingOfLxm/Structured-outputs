<template>
  <div class="mindmap-page">
    <div class="content-wrapper">
      <el-card class="mindmap-card">
        <template #header>
          <div class="card-header">
            <el-button link @click="goBack">
              <el-icon><ArrowLeft /></el-icon>
              返回
            </el-button>
            <div class="header-title">
              <el-icon><Share /></el-icon>
              <span>思维导图</span>
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

        <div v-loading="loading" class="mindmap-container">
          <div v-if="!loading && !mindmapData" class="empty-state">
            <el-icon :size="64"><DocumentCopy /></el-icon>
            <p>暂无思维导图数据</p>
            <el-button type="primary" @click="handleRegenerate">生成思维导图</el-button>
          </div>

          <div v-else-if="mindmapData" ref="mindmapRef" class="mindmap-canvas"></div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { paperApi, generateApi } from '@/api'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const regenerating = ref(false)
const paper = ref(null)
const mindmapData = ref(null)
const mindmapRef = ref(null)
let chart = null

const loadPaperInfo = async () => {
  try {
    const res = await paperApi.getPaperDetail(route.params.id)
    paper.value = res.data
  } catch (error) {
    console.error('加载失败:', error)
  }
}

const loadMindMap = async () => {
  loading.value = true
  try {
    const res = await generateApi.getGenerateHistory(route.params.id)
    const mindmapItem = res.data.list?.find(item => item.type === 'mindmap')
    if (mindmapItem && mindmapItem.content) {
      mindmapData.value = JSON.parse(mindmapItem.content)
      await nextTick()
      renderMindMap()
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
    await generateApi.generateMindMap({ paperId: route.params.id })
    ElMessage.success('生成成功')
    setTimeout(() => {
      loadMindMap()
    }, 1000)
  } catch (error) {
    console.error('生成失败:', error)
    ElMessage.error('生成失败，请重试')
  } finally {
    regenerating.value = false
  }
}

const handleExport = () => {
  if (!chart) {
    ElMessage.warning('请先生成思维导图')
    return
  }
  const url = chart.getDataURL({
    type: 'png',
    pixelRatio: 2,
    backgroundColor: '#fff'
  })
  const link = document.createElement('a')
  link.href = url
  link.download = `思维导图-${paper.value?.title || '论文'}.png`
  link.click()
}

const renderMindMap = () => {
  if (!mindmapRef.value || !mindmapData.value) return

  if (chart) {
    chart.dispose()
  }

  chart = echarts.init(mindmapRef.value)

  const option = {
    tooltip: {
      trigger: 'item',
      triggerOn: 'mousemove'
    },
    series: [
      {
        type: 'tree',
        data: [mindmapData.value],
        top: '5%',
        left: '10%',
        bottom: '5%',
        right: '20%',
        symbolSize: 10,
        label: {
          position: 'left',
          verticalAlign: 'middle',
          align: 'right',
          fontSize: 14
        },
        leaves: {
          label: {
            position: 'right',
            verticalAlign: 'middle',
            align: 'left'
          }
        },
        emphasis: {
          focus: 'descendant'
        },
        expandAndCollapse: true,
        animationDuration: 550,
        animationDurationUpdate: 750
      }
    ]
  }

  chart.setOption(option)
}

const goBack = () => {
  router.push(`/paper/${route.params.id}`)
}

onMounted(() => {
  loadPaperInfo()
  loadMindMap()

  window.addEventListener('resize', () => {
    chart?.resize()
  })
})

onUnmounted(() => {
  if (chart) {
    chart.dispose()
  }
})
</script>

<style scoped>
.mindmap-page {
  height: 100%;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.mindmap-card {
  height: calc(100vh - 120px);
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

.mindmap-container {
  height: calc(100% - 100px);
  min-height: 500px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}

.empty-state .icon {
  margin-bottom: 20px;
}

.empty-state p {
  margin-bottom: 20px;
}

.mindmap-canvas {
  width: 100%;
  height: 100%;
  min-height: 500px;
}
</style>
