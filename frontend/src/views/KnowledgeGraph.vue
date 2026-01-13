<template>
  <div class="graph-page">
    <div class="content-wrapper">
      <el-card class="graph-card">
        <template #header>
          <div class="card-header">
            <el-button link @click="goBack">
              <el-icon><ArrowLeft /></el-icon>
              返回
            </el-button>
            <div class="header-title">
              <el-icon><Connection /></el-icon>
              <span>概念图谱</span>
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

        <div v-loading="loading" class="graph-container">
          <div v-if="!loading && !graphData" class="empty-state">
            <el-icon :size="64"><Connection /></el-icon>
            <p>暂无概念图谱数据</p>
            <el-button type="primary" @click="handleRegenerate">生成概念图谱</el-button>
          </div>

          <div v-else-if="graphData" ref="graphRef" class="graph-canvas"></div>
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
const graphData = ref(null)
const graphRef = ref(null)
let chart = null

const loadPaperInfo = async () => {
  try {
    const res = await paperApi.getPaperDetail(route.params.id)
    paper.value = res.data
  } catch (error) {
    console.error('加载失败:', error)
  }
}

const loadGraph = async () => {
  loading.value = true
  try {
    const res = await generateApi.getGenerateHistory(route.params.id)
    const graphItem = res.data.list?.find(item => item.type === 'graph')
    if (graphItem && graphItem.content) {
      graphData.value = JSON.parse(graphItem.content)
      await nextTick()
      renderGraph()
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
    await generateApi.generateGraph({ paperId: route.params.id })
    ElMessage.success('生成成功')
    setTimeout(() => {
      loadGraph()
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
    ElMessage.warning('请先生成概念图谱')
    return
  }
  const url = chart.getDataURL({
    type: 'png',
    pixelRatio: 2,
    backgroundColor: '#fff'
  })
  const link = document.createElement('a')
  link.href = url
  link.download = `概念图谱-${paper.value?.title || '论文'}.png`
  link.click()
}

const renderGraph = () => {
  if (!graphRef.value || !graphData.value) return

  if (chart) {
    chart.dispose()
  }

  chart = echarts.init(graphRef.value)

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}'
    },
    legend: {
      show: true,
      data: graphData.value.categories?.map(c => c.name) || []
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        data: graphData.value.nodes || [],
        links: graphData.value.links || [],
        categories: graphData.value.categories || [],
        roam: true,
        label: {
          show: true,
          position: 'right',
          formatter: '{b}'
        },
        labelLayout: {
          hideOverlap: true
        },
        scaleLimit: {
          min: 0.4,
          max: 2
        },
        lineStyle: {
          color: 'source',
          curveness: 0.3
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 10
          }
        },
        force: {
          repulsion: 200,
          edgeLength: 100
        }
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
  loadGraph()

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
.graph-page {
  height: 100%;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.graph-card {
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

.graph-container {
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

.empty-state p {
  margin-bottom: 20px;
}

.graph-canvas {
  width: 100%;
  height: 100%;
  min-height: 500px;
}
</style>
