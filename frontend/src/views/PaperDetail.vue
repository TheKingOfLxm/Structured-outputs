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
              <el-descriptions-item label="作者">{{ formatAuthors(paper.authors) }}</el-descriptions-item>
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

        <!-- 论文阅读报告（八元组） -->
        <el-card v-if="summaryReport" class="summary-card">
          <template #header>
            <div class="card-header">
              <el-icon><ChatDotRound /></el-icon>
              <span>论文阅读报告</span>
              <el-button type="primary" link @click="generateSummary" :loading="generatingSummary">
                <el-icon><Refresh /></el-icon>
                重新生成
              </el-button>
            </div>
          </template>

          <div class="summary-content">
            <div class="summary-item">
              <h4 class="summary-label">摘要</h4>
              <p class="summary-text">{{ summaryReport.abstract || '-' }}</p>
            </div>
            <el-divider />
            <div class="summary-item">
              <h4 class="summary-label">关键词</h4>
              <p class="summary-text">{{ summaryReport.keywords || '-' }}</p>
            </div>
            <el-divider />
            <div class="summary-item">
              <h4 class="summary-label">研究问题</h4>
              <p class="summary-text">{{ summaryReport.researchQuestion || '-' }}</p>
            </div>
            <el-divider />
            <div class="summary-item">
              <h4 class="summary-label">方法</h4>
              <p class="summary-text">{{ summaryReport.method || '-' }}</p>
            </div>
            <el-divider />
            <div class="summary-item">
              <h4 class="summary-label">结果</h4>
              <p class="summary-text">{{ summaryReport.results || '-' }}</p>
            </div>
            <el-divider />
            <div class="summary-item">
              <h4 class="summary-label">讨论</h4>
              <p class="summary-text">{{ summaryReport.discussion || '-' }}</p>
            </div>
            <el-divider />
            <div class="summary-item">
              <h4 class="summary-label">创新点</h4>
              <p class="summary-text">{{ summaryReport.innovation || '-' }}</p>
            </div>
            <el-divider />
            <div class="summary-item">
              <h4 class="summary-label">技术问题</h4>
              <p class="summary-text">{{ summaryReport.technicalIssues || '-' }}</p>
            </div>
          </div>
        </el-card>

        <!-- 论文阅读报告空状态 -->
        <el-card v-else class="summary-empty-card">
          <template #header>
            <div class="card-header">
              <el-icon><ChatDotRound /></el-icon>
              <span>论文阅读报告</span>
            </div>
          </template>
          <el-empty description="暂无论文阅读报告">
            <el-button type="primary" @click="generateSummary" :loading="generatingSummary">
              生成论文阅读报告
            </el-button>
          </el-empty>
        </el-card>

        <!-- 论文评审报告 -->
        <el-card v-if="reviewReport" class="review-card">
          <template #header>
            <div class="card-header">
              <el-icon><ChatDotRound /></el-icon>
              <span>论文评审报告</span>
              <el-button type="primary" link @click="generateReview" :loading="generatingReview">
                <el-icon><Refresh /></el-icon>
                重新生成
              </el-button>
            </div>
          </template>

          <div class="review-content">
            <!-- 总体评分 -->
            <div class="overall-score">
              <div class="score-display">
                <span class="score-number">{{ reviewReport.overall_score || 0 }}</span>
                <span class="score-label">总分</span>
              </div>
              <div class="overall-comment" v-if="reviewReport.overall_comment">
                <strong>综合评语：</strong>{{ reviewReport.overall_comment }}
              </div>
            </div>

            <el-divider />

            <!-- 各项评分 -->
            <div class="score-items">
              <div
                v-for="(item, key) in scoreItems"
                :key="key"
                class="score-item"
              >
                <div class="score-header">
                  <span class="score-title">{{ item.label }}</span>
                  <el-rate
                    v-model="item.score"
                    disabled
                    show-score
                    score-template="{value}"
                    :max="10"
                    class="score-rate"
                  />
                </div>
                <div class="score-comment">{{ item.comment }}</div>
              </div>
            </div>

            <el-divider v-if="reviewReport.suggestions && reviewReport.suggestions.length" />

            <!-- 改进建议 -->
            <div v-if="reviewReport.suggestions && reviewReport.suggestions.length" class="suggestions">
              <h4 class="suggestions-title">改进建议</h4>
              <ul class="suggestions-list">
                <li v-for="(suggestion, index) in reviewReport.suggestions" :key="index">
                  {{ suggestion }}
                </li>
              </ul>
            </div>
          </div>
        </el-card>

        <!-- 论文评审报告空状态 -->
        <el-card v-else class="review-empty-card">
          <template #header>
            <div class="card-header">
              <el-icon><ChatDotRound /></el-icon>
              <span>论文评审报告</span>
            </div>
          </template>
          <el-empty description="暂无评审报告">
            <el-button type="primary" @click="generateReview" :loading="generatingReview">
              生成评审报告
            </el-button>
          </el-empty>
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
            <div class="option-item" @click="goToMindMap" :class="{ 'is-disabled': anyGenerating }">
              <div class="option-icon">
                <el-icon :size="32"><Share /></el-icon>
              </div>
              <div class="option-info">
                <h4>思维导图</h4>
                <p>可视化展示论文结构</p>
              </div>
            </div>

            <div class="option-item" @click="goToTimeline" :class="{ 'is-disabled': anyGenerating }">
              <div class="option-icon">
                <el-icon :size="32"><Clock /></el-icon>
              </div>
              <div class="option-info">
                <h4>时间线</h4>
                <p>展示研究演进过程</p>
              </div>
            </div>

            <div class="option-item" @click="goToGraph" :class="{ 'is-disabled': anyGenerating }">
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
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ChatDotRound } from '@element-plus/icons-vue'
import { paperApi, generateApi } from '@/api'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const reparsing = ref(false)
const generatingSummary = ref(false)
const generatingReview = ref(false)
const paper = ref(null)
const summaryReport = ref(null)
const reviewReport = ref(null)

// 计算是否有任何操作正在进行中
const anyGenerating = computed(() => {
  return reparsing.value || generatingSummary.value || generatingReview.value
})

// 评审报告评分项配置
const scoreItemConfig = {
  title_quality: '标题质量',
  abstract_quality: '摘要质量',
  keywords_quality: '关键词质量',
  research_clarity: '研究问题清晰度',
  method_rigor: '方法严谨性',
  experiment_validity: '实验有效性',
  result_reliability: '结果可靠性',
  innovation_level: '创新水平'
}

// 计算属性：评分项列表
const scoreItems = computed(() => {
  if (!reviewReport.value) return []

  return Object.keys(scoreItemConfig).map(key => ({
    key,
    label: scoreItemConfig[key],
    score: reviewReport.value[key]?.score || 5,
    comment: reviewReport.value[key]?.comment || ''
  }))
})

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

const loadSummaryReport = async () => {
  try {
    const res = await generateApi.getGenerateHistory(route.params.id)
    const summaryItem = res.data.list?.find(item => item.type === 'summary')
    if (summaryItem && summaryItem.content) {
      try {
        summaryReport.value = JSON.parse(summaryItem.content)
      } catch (e) {
        console.error('解析报告失败:', e)
      }
    }
  } catch (error) {
    console.error('加载报告失败:', error)
  }
}

const loadReviewReport = async () => {
  try {
    const res = await generateApi.getGenerateHistory(route.params.id)
    const reviewItem = res.data.list?.find(item => item.type === 'review')
    if (reviewItem && reviewItem.content) {
      try {
        reviewReport.value = JSON.parse(reviewItem.content)
      } catch (e) {
        console.error('解析评审报告失败:', e)
      }
    }
  } catch (error) {
    console.error('加载评审报告失败:', error)
  }
}

const generateSummary = async () => {
  generatingSummary.value = true
  try {
    await generateApi.generateSummary({ paperId: route.params.id })
    ElMessage.success('生成成功')
    setTimeout(() => {
      loadSummaryReport()
    }, 1000)
  } catch (error) {
    console.error('生成失败:', error)
    ElMessage.error('生成失败，请重试')
  } finally {
    generatingSummary.value = false
  }
}

const generateReview = async () => {
  generatingReview.value = true
  try {
    const res = await generateApi.generateReview({ paperId: route.params.id })
    ElMessage.success('评审报告生成成功')
    if (res.data.content) {
      reviewReport.value = res.data.content
    }
  } catch (error) {
    console.error('生成评审报告失败:', error)
    ElMessage.error('生成失败，请重试')
  } finally {
    generatingReview.value = false
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

const formatAuthors = (authors) => {
  if (!authors) return '未知'
  if (Array.isArray(authors)) {
    return authors.join(', ')
  }
  // 如果是字符串，尝试解析
  if (typeof authors === 'string') {
    try {
      const parsed = JSON.parse(authors)
      if (Array.isArray(parsed)) {
        return parsed.join(', ')
      }
    } catch (e) {
      // 解析失败，直接返回字符串
    }
  }
  return authors
}

onMounted(() => {
  loadPaperDetail()
  loadSummaryReport()
  loadReviewReport()
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

.option-item.is-disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.option-item.is-disabled:hover {
  border-color: #e4e7ed;
  box-shadow: none;
  transform: none;
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

/* 评审报告样式 */
.review-card,
.review-empty-card {
  margin-bottom: 20px;
}

.review-content {
  padding: 10px 0;
}

.overall-score {
  display: flex;
  align-items: center;
  gap: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
}

.score-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 100px;
}

.score-number {
  font-size: 48px;
  font-weight: bold;
  line-height: 1;
}

.score-label {
  font-size: 14px;
  opacity: 0.9;
  margin-top: 5px;
}

.overall-comment {
  flex: 1;
  font-size: 15px;
  line-height: 1.6;
}

.score-items {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.score-item {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.score-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.score-title {
  font-weight: 600;
  color: #303133;
}

.score-rate {
  flex-shrink: 0;
}

.score-comment {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

.suggestions {
  padding: 15px;
  background: #fff9e6;
  border-left: 4px solid #e6a23c;
  border-radius: 4px;
}

.suggestions-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px;
}

.suggestions-list {
  margin: 0;
  padding-left: 20px;
}

.suggestions-list li {
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
  margin-bottom: 8px;
}

.summary-card,
.summary-empty-card {
  margin-bottom: 20px;
}

.summary-content {
  padding: 10px 0;
}

.summary-item {
  padding: 15px 0;
}

.summary-label {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 10px;
}

.summary-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
  margin: 0;
  white-space: pre-wrap;
}
</style>
