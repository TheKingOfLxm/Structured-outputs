<template>
  <div class="paper-detail-page">
    <div class="content-wrapper">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-icon class="is-loading" :size="40"><Loading /></el-icon>
        <p>正在加载论文信息...</p>
      </div>

      <!-- 论文详情 -->
      <div v-else-if="paper">
        <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <el-button link @click="goBack">
                <el-icon><ArrowLeft /></el-icon>
                返回
              </el-button>
              <div class="header-actions">
                <el-button type="primary" @click="goToGenerate">
                  <el-icon><MagicStick /></el-icon>
                  生成内容
                </el-button>
                <el-button @click="handleReparse" :loading="reparsing">
                  <el-icon><Refresh /></el-icon>
                  重新解析
                </el-button>
              </div>
            </div>
          </template>

          <!-- 论文基本信息 -->
          <div class="paper-info">
            <h1 class="paper-title">{{ paper.title || '未命名论文' }}</h1>

            <el-descriptions :column="2" border class="info-table">
              <el-descriptions-item label="作者">{{ paper.authors || '未知' }}</el-descriptions-item>
              <el-descriptions-item label="发布时间">{{ paper.publishDate || '-' }}</el-descriptions-item>
              <el-descriptions-item label="来源">{{ paper.source || '-' }}</el-descriptions-item>
              <el-descriptions-item label="上传时间">{{ formatDate(paper.uploadTime) }}</el-descriptions-item>
            </el-descriptions>

            <div v-if="paper.keywords && paper.keywords.length" class="keywords-section">
              <h3>关键词</h3>
              <el-tag v-for="keyword in paper.keywords" :key="keyword" class="keyword-tag">
                {{ keyword }}
              </el-tag>
            </div>

            <div v-if="paper.abstract" class="abstract-section">
              <h3>摘要</h3>
              <p class="abstract-content">{{ paper.abstract }}</p>
            </div>
          </div>
        </el-card>

        <!-- 论文章节 -->
        <el-card v-if="paper.sections && paper.sections.length" class="sections-card">
          <template #header>
            <div class="card-header">
              <el-icon><Document /></el-icon>
              <span>论文章节</span>
            </div>
          </template>

          <el-collapse v-model="activeSections">
            <el-collapse-item v-for="(section, index) in paper.sections" :key="index" :name="index">
              <template #title>
                <span class="section-title">{{ section.title }}</span>
              </template>
              <div class="section-content">
                {{ section.content }}
              </div>
            </el-collapse-item>
          </el-collapse>
        </el-card>

        <!-- 生成内容快捷入口 -->
        <el-card class="generate-card">
          <template #header>
            <div class="card-header">
              <el-icon><MagicStick /></el-icon>
              <span>内容生成</span>
            </div>
          </template>

          <div class="generate-options">
            <div class="option-item" @click="goToMindMap">
              <div class="option-icon">
                <el-icon :size="32"><Share /></el-icon>
              </div>
              <div class="option-info">
                <h4>思维导图</h4>
                <p>可视化展示论文结构</p>
              </div>
            </div>

            <div class="option-item" @click="goToTimeline">
              <div class="option-icon">
                <el-icon :size="32"><Clock /></el-icon>
              </div>
              <div class="option-info">
                <h4>时间线</h4>
                <p>展示研究演进过程</p>
              </div>
            </div>

            <div class="option-item" @click="goToGraph">
              <div class="option-icon">
                <el-icon :size="32"><Connection /></el-icon>
              </div>
              <div class="option-info">
                <h4>概念图谱</h4>
                <p>展示知识关系网络</p>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 空状态 -->
      <el-empty v-else description="论文不存在或已被删除" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { paperApi } from '@/api'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const reparsing = ref(false)
const paper = ref(null)
const activeSections = ref([])

const loadPaperDetail = async () => {
  loading.value = true
  try {
    const res = await paperApi.getPaperDetail(route.params.id)
    paper.value = res.data
  } catch (error) {
    console.error('加载失败:', error)
    ElMessage.error('加载论文详情失败')
  } finally {
    loading.value = false
  }
}

const handleReparse = async () => {
  reparsing.value = true
  try {
    await paperApi.parsePaper(route.params.id)
    ElMessage.success('开始解析论文')
    setTimeout(() => {
      loadPaperDetail()
    }, 2000)
  } catch (error) {
    console.error('解析失败:', error)
    ElMessage.error('解析失败，请重试')
  } finally {
    reparsing.value = false
  }
}

const goBack = () => {
  router.push('/papers')
}

const goToGenerate = () => {
  router.push(`/generate/${route.params.id}`)
}

const goToMindMap = () => {
  router.push(`/mindmap/${route.params.id}`)
}

const goToTimeline = () => {
  router.push(`/timeline/${route.params.id}`)
}

const goToGraph = () => {
  router.push(`/graph/${route.params.id}`)
}

const formatDate = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

onMounted(() => {
  loadPaperDetail()
})
</script>

<style scoped>
.paper-detail-page {
  height: 100%;
}

.content-wrapper {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #909399;
}

.loading-container p {
  margin-top: 20px;
}

.detail-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.paper-info {
  padding: 10px 0;
}

.paper-title {
  font-size: 24px;
  color: #303133;
  margin: 0 0 20px;
  line-height: 1.5;
}

.info-table {
  margin: 20px 0;
}

.keywords-section {
  margin: 20px 0;
}

.keywords-section h3 {
  font-size: 16px;
  color: #303133;
  margin: 0 0 12px;
}

.keyword-tag {
  margin-right: 10px;
  margin-bottom: 10px;
}

.abstract-section {
  margin: 20px 0;
}

.abstract-section h3 {
  font-size: 16px;
  color: #303133;
  margin: 0 0 12px;
}

.abstract-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
  text-indent: 2em;
  margin: 0;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.sections-card {
  margin-bottom: 20px;
}

.section-title {
  font-weight: 600;
  color: #303133;
}

.section-content {
  color: #606266;
  line-height: 1.8;
  white-space: pre-wrap;
}

.generate-card {
  margin-bottom: 20px;
}

.generate-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.option-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.1);
  transform: translateY(-2px);
}

.option-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ecf5ff;
  border-radius: 8px;
  color: #409eff;
  flex-shrink: 0;
}

.option-info h4 {
  font-size: 16px;
  color: #303133;
  margin: 0 0 8px;
}

.option-info p {
  font-size: 14px;
  color: #909399;
  margin: 0;
}
</style>
