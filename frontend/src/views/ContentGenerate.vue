<template>
  <div class="generate-page">
    <div class="content-wrapper">
      <el-card class="generate-card">
        <template #header>
          <div class="card-header">
            <el-button link @click="goBack">
              <el-icon><ArrowLeft /></el-icon>
              返回
            </el-button>
            <span>内容生成</span>
          </div>
        </template>

        <div v-if="paper" class="paper-summary">
          <h3>{{ paper.title }}</h3>
          <p>{{ paper.authors }}</p>
        </div>

        <div class="generate-types">
          <div
            v-for="type in generateTypes"
            :key="type.value"
            class="type-item"
            :class="{ active: selectedType === type.value }"
            @click="selectType(type.value)"
          >
            <div class="type-icon">
              <el-icon :size="32">
                <component :is="type.icon" />
              </el-icon>
            </div>
            <div class="type-info">
              <h4>{{ type.label }}</h4>
              <p>{{ type.description }}</p>
            </div>
          </div>
        </div>

        <div class="generate-actions">
          <el-button
            type="primary"
            size="large"
            :loading="generating"
            :disabled="!selectedType"
            @click="handleGenerate"
          >
            <el-icon><MagicStick /></el-icon>
            开始生成
          </el-button>
        </div>
      </el-card>

      <!-- 生成历史 -->
      <el-card v-if="history.length" class="history-card">
        <template #header>
          <div class="card-header">
            <el-icon><Clock /></el-icon>
            <span>生成历史</span>
          </div>
        </template>

        <el-timeline>
          <el-timeline-item
            v-for="item in history"
            :key="item.id"
            :timestamp="formatDateTime(item.createTime)"
            placement="top"
          >
            <el-card>
              <div class="history-item">
                <div class="history-info">
                  <h4>{{ getTypeLabel(item.type) }}</h4>
                  <p>{{ item.description || '无描述' }}</p>
                </div>
                <div class="history-actions">
                  <el-button type="primary" link @click="viewResult(item)">
                    查看结果
                  </el-button>
                  <el-button link @click="deleteHistory(item)">删除</el-button>
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Share, Clock, Connection, ChatDotRound } from '@element-plus/icons-vue'
import { paperApi, generateApi } from '@/api'

const router = useRouter()
const route = useRoute()

const paper = ref(null)
const selectedType = ref('')
const generating = ref(false)
const history = ref([])

const generateTypes = [
  {
    value: 'mindmap',
    label: '思维导图',
    description: '可视化展示论文结构和核心概念',
    icon: Share
  },
  {
    value: 'timeline',
    label: '时间线',
    description: '展示研究发展的时间脉络',
    icon: Clock
  },
  {
    value: 'graph',
    label: '概念图谱',
    description: '展示概念之间的知识关系',
    icon: Connection
  },
  {
    value: 'summary',
    label: '核心观点',
    description: '总结论文的核心观点和贡献',
    icon: ChatDotRound
  }
]

const loadPaperInfo = async () => {
  try {
    const res = await paperApi.getPaperDetail(route.params.id)
    paper.value = res.data
  } catch (error) {
    console.error('加载失败:', error)
  }
}

const loadHistory = async () => {
  try {
    const res = await generateApi.getGenerateHistory(route.params.id)
    history.value = res.data.list || []
  } catch (error) {
    console.error('加载历史失败:', error)
  }
}

const selectType = (type) => {
  selectedType.value = type
}

const handleGenerate = async () => {
  if (!selectedType.value) {
    ElMessage.warning('请选择生成类型')
    return
  }

  generating.value = true
  try {
    const apiMap = {
      mindmap: generateApi.generateMindMap,
      timeline: generateApi.generateTimeline,
      graph: generateApi.generateGraph,
      summary: generateApi.generateSummary
    }

    const api = apiMap[selectedType.value]
    const res = await api({ paperId: route.params.id })

    ElMessage.success('生成成功')

    // 跳转到对应的结果页面
    setTimeout(() => {
      const routeMap = {
        mindmap: `/mindmap/${route.params.id}`,
        timeline: `/timeline/${route.params.id}`,
        graph: `/graph/${route.params.id}`,
        summary: `/paper/${route.params.id}`
      }
      router.push(routeMap[selectedType.value])
    }, 500)
  } catch (error) {
    console.error('生成失败:', error)
    ElMessage.error('生成失败，请重试')
  } finally {
    generating.value = false
  }
}

const getTypeLabel = (type) => {
  const item = generateTypes.find(t => t.value === type)
  return item ? item.label : type
}

const viewResult = (item) => {
  const routeMap = {
    mindmap: `/mindmap/${route.params.id}`,
    timeline: `/timeline/${route.params.id}`,
    graph: `/graph/${route.params.id}`,
    summary: `/paper/${route.params.id}`
  }
  router.push(routeMap[item.type])
}

const deleteHistory = (item) => {
  ElMessageBox.confirm('确定要删除这条生成记录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    // TODO: 调用删除接口
    history.value = history.value.filter(h => h.id !== item.id)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

const goBack = () => {
  router.push(`/paper/${route.params.id}`)
}

const formatDateTime = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

onMounted(() => {
  loadPaperInfo()
  loadHistory()
})
</script>

<style scoped>
.generate-page {
  height: 100%;
}

.content-wrapper {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.generate-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.paper-summary {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 30px;
}

.paper-summary h3 {
  font-size: 18px;
  color: #303133;
  margin: 0 0 8px;
}

.paper-summary p {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.generate-types {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.type-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.type-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.1);
}

.type-item.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.type-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 8px;
  color: #909399;
  flex-shrink: 0;
  transition: all 0.3s;
}

.type-item.active .type-icon {
  background: #409eff;
  color: #fff;
}

.type-info h4 {
  font-size: 16px;
  color: #303133;
  margin: 0 0 8px;
}

.type-info p {
  font-size: 13px;
  color: #909399;
  margin: 0;
  line-height: 1.4;
}

.generate-actions {
  display: flex;
  justify-content: center;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

.history-card {
  margin-bottom: 20px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.history-info h4 {
  font-size: 16px;
  color: #303133;
  margin: 0 0 8px;
}

.history-info p {
  font-size: 14px;
  color: #606266;
  margin: 0;
}

.history-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}
</style>
