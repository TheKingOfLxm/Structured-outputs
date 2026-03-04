<template>
  <div class="paper-assistant-page">
    <div class="content-wrapper">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-icon class="is-loading" :size="40"><Loading /></el-icon>
        <p>正在加载论文信息...</p>
      </div>

      <!-- 空状态 -->
      <el-empty v-else-if="!paper" description="论文不存在或已被删除">
        <el-button type="primary" @click="goBack">返回论文列表</el-button>
      </el-empty>

      <!-- 论文助手主界面 -->
      <div v-else class="assistant-container">
        <!-- 顶部信息栏 -->
        <el-card class="info-card">
          <div class="paper-header">
            <div class="paper-info">
              <h1 class="paper-title">{{ paper.title || '未命名论文' }}</h1>
              <div class="paper-meta">
                <span class="meta-item">
                  <el-icon><User /></el-icon>
                  {{ formatAuthors(paper.authors) }}
                </span>
                <span class="meta-item">
                  <el-icon><Calendar /></el-icon>
                  {{ paper.publishDate || '-' }}
                </span>
                <span class="meta-item">
                  <el-icon><Collection /></el-icon>
                  {{ paper.category || '未分类' }}
                </span>
              </div>
            </div>
            <el-button @click="goBack">
              <el-icon><ArrowLeft /></el-icon>
              返回
            </el-button>
          </div>
        </el-card>

        <!-- 功能区域 -->
        <div class="function-container">
          <!-- 左侧工具栏 -->
          <div class="sidebar">
            <div class="sidebar-section">
              <h3>阅读工具</h3>
              <div class="tool-buttons">
                <el-button type="primary" :icon="Reading" @click="showPdfReader = true" :disabled="pdfLoading">
                  {{ pdfLoading ? '加载中...' : '阅读PDF' }}
                </el-button>
              </div>
            </div>

            <el-divider />

            <div class="sidebar-section">
              <h3>翻译工具</h3>
              <div class="translate-options">
                <el-radio-group v-model="translateTarget" :disabled="translating">
                  <el-radio label="zh">英译中</el-radio>
                  <el-radio label="en">中译英</el-radio>
                </el-radio-group>
                <el-button
                  type="success"
                  :icon="Switch"
                  @click="handleTranslate"
                  :loading="translating"
                  :disabled="translating"
                  style="width: 100%; margin-top: 10px;"
                >
                  {{ translating ? '翻译中...' : '开始翻译' }}
                </el-button>
              </div>
            </div>
          </div>

          <!-- 右侧内容区域 -->
          <div class="main-content">
            <!-- PDF阅读器 -->
            <div v-if="showPdfReader" class="pdf-reader-wrapper">
              <div class="reader-header">
                <span class="reader-title">PDF阅读器</span>
                <el-button :icon="Close" @click="showPdfReader = false" circle />
              </div>
              <div class="reader-content">
                <PdfReader :url="pdfReaderUrl" />
              </div>
            </div>

            <!-- 翻译结果 - 对照翻译 -->
            <div v-else-if="translationResult" class="translation-wrapper">
              <div class="reader-header">
                <span class="reader-title">对照翻译 ({{ translateTarget === 'zh' ? '英译中' : '中译英' }})</span>
                <el-button :icon="Edit" @click="handleTranslate" :loading="translating" circle title="重新翻译" />
              </div>
              <div class="translation-content">
                <div class="parallel-container">
                  <!-- 左侧原文 -->
                  <div class="parallel-panel original-panel">
                    <div class="panel-header">原文</div>
                    <div class="panel-content" ref="originalContentRef">
                      <div class="paper-section" v-for="(section, index) in paperSections" :key="'orig-' + index">
                        <div class="section-title">{{ section.title }}</div>
                        <div class="section-content">{{ section.content }}</div>
                      </div>
                    </div>
                  </div>
                  <!-- 右侧译文 -->
                  <div class="parallel-panel translated-panel">
                    <div class="panel-header">译文 ({{ translateTarget === 'zh' ? '中文' : '英文' }})</div>
                    <div class="panel-content" ref="translatedContentRef">
                      <div class="paper-section" v-for="(section, index) in translatedSections" :key="'trans-' + index">
                        <div class="section-title">{{ section.title }}</div>
                        <div class="section-content">{{ section.content }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 默认欢迎页面 -->
            <div v-else class="welcome-wrapper">
              <div class="welcome-content">
                <el-icon :size="80" color="#409eff"><Reading /></el-icon>
                <h2>论文助手</h2>
                <p>请从左侧选择工具开始使用</p>
                <div class="feature-list">
                  <div class="feature-item">
                    <el-icon :size="32"><Document /></el-icon>
                    <div>
                      <h4>PDF阅读</h4>
                      <p>在线阅读原始PDF论文</p>
                    </div>
                  </div>
                  <div class="feature-item">
                    <el-icon :size="32"><Switch /></el-icon>
                    <div>
                      <h4>智能翻译</h4>
                      <p>AI驱动的论文翻译</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  User, Calendar, Collection, Reading, Switch, Edit, Close, Document,
  ArrowLeft, Loading
} from '@element-plus/icons-vue'
import { paperApi, chatApi, generateApi } from '@/api'
import PdfReader from '@/components/PdfReader.vue'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const pdfLoading = ref(false)
const translating = ref(false)
const paper = ref(null)
const translationResult = ref(null)
const originalSections = ref([])  // 存储从翻译API返回的原文分段

// UI状态
const showPdfReader = ref(false)
const translateTarget = ref('zh')  // zh=英译中, en=中译英

// 对照翻译数据
const originalContentRef = ref(null)
const translatedContentRef = ref(null)

// 原文分段
const paperSections = computed(() => {
  // 如果有翻译返回的原文分段，优先使用
  if (originalSections.value && originalSections.value.length > 0) {
    return originalSections.value
  }

  // 否则使用数据库中的论文信息
  if (!paper.value) return []
  const sections = []

  // 添加标题和作者
  if (paper.value.title) {
    sections.push({
      title: '论文标题',
      content: paper.value.title
    })
  }

  // 添加摘要
  if (paper.value.abstract) {
    sections.push({
      title: '摘要',
      content: paper.value.abstract
    })
  }

  // 添加关键词
  if (paper.value.keywords && paper.value.keywords.length) {
    const keywordsText = Array.isArray(paper.value.keywords)
      ? paper.value.keywords.join(', ')
      : paper.value.keywords
    sections.push({
      title: '关键词',
      content: keywordsText
    })
  }

  // 添加章节内容
  if (paper.value.sections && paper.value.sections.length) {
    paper.value.sections.forEach(section => {
      if (section.title || section.content) {
        sections.push({
          title: section.number ? `${section.number} ${section.title}` : section.title,
          content: section.content || ''
        })
      }
    })
  }

  return sections
})

// 译文分段
const translatedSections = computed(() => {
  if (!translationResult.value) return []

  // 解析翻译结果，按【标题】分段
  const content = typeof translationResult.value === 'string'
    ? translationResult.value
    : String(translationResult.value)

  const sections = []
  // 改进正则表达式，按【标题】分段（支持多种换行格式）
  const regex = /【([^】]+)】\s*\n([\s\S]*?)(?=\s*\n【|$)/g
  let match
  let index = 0

  while ((match = regex.exec(content)) !== null) {
    sections.push({
      title: match[1].trim(),
      content: match[2].trim()
    })
    index++
  }

  // 如果没有匹配到分段格式，尝试更宽松的匹配
  if (sections.length === 0) {
    const relaxedRegex = /【([^】]+)】([^\[]*?)(?=【|$)/g
    while ((match = relaxedRegex.exec(content)) !== null) {
      const title = match[1].trim()
      let content_part = match[2].trim()
      // 清理可能的序号前缀
      content_part = content_part.replace(/^\d+\.?\s*/, '')
      if (title && content_part) {
        sections.push({ title, content: content_part })
      }
    }
  }

  // 如果还是没有匹配到，按原文分段数平均分配
  if (sections.length === 0 && paperSections.value.length > 0) {
    const lines = content.split('\n').filter(line => line.trim())
    const linesPerSection = Math.ceil(lines.length / paperSections.value.length)

    paperSections.value.forEach((origSection, index) => {
      const startIdx = index * linesPerSection
      const endIdx = startIdx + linesPerSection
      const sectionContent = lines.slice(startIdx, endIdx).join('\n').trim()

      sections.push({
        title: origSection.title,
        content: sectionContent || '（翻译处理中...）'
      })
    })
  }

  // 如果译文段数少于原文，补充缺失的部分
  while (sections.length < paperSections.value.length) {
    const missingSection = paperSections.value[sections.length]
    if (missingSection) {
      sections.push({
        title: missingSection.title,
        content: '（此部分未翻译）'
      })
    } else {
      break
    }
  }

  return sections
})

// PDF阅读器URL
const pdfReaderUrl = computed(() => {
  return paperApi.getPaperViewUrl(route.params.id)
})

// 加载论文详情
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

// 翻译论文
const handleTranslate = async () => {
  translating.value = true
  try {
    const res = await chatApi.translatePaper({
      paperId: route.params.id,
      targetLang: translateTarget.value
    })
    ElMessage.success('翻译成功')
    // 存储原文分段和翻译内容
    originalSections.value = res.data.originalSections || []
    translationResult.value = res.data.translatedContent || res.data.content
    showPdfReader.value = false
  } catch (error) {
    console.error('翻译失败:', error)
    ElMessage.error(error.response?.data?.message || '翻译失败，请重试')
  } finally {
    translating.value = false
  }
}

const goBack = () => {
  router.push('/papers')
}

const formatAuthors = (authors) => {
  if (!authors) return '未知'
  if (Array.isArray(authors)) {
    return authors.join(', ')
  }
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
})
</script>

<style scoped>
.paper-assistant-page {
  height: 100%;
}

.content-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}

.loading-container p {
  margin-top: 20px;
}

.assistant-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 信息卡片 */
.info-card {
  margin-bottom: 20px;
}

.paper-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.paper-info {
  flex: 1;
}

.paper-title {
  font-size: 20px;
  color: #303133;
  margin: 0 0 12px;
  line-height: 1.5;
}

.paper-meta {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
  font-size: 14px;
}

/* 功能区域 */
.function-container {
  flex: 1;
  display: flex;
  gap: 20px;
  overflow: hidden;
}

/* 侧边栏 */
.sidebar {
  width: 280px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sidebar-section {
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.sidebar-section h3 {
  font-size: 16px;
  color: #303133;
  margin: 0 0 16px;
}

.tool-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tool-buttons .el-button {
  width: 100%;
}

.translate-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.reader-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.reader-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.pdf-reader-wrapper,
.translation-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.reader-content {
  flex: 1;
  overflow: hidden;
}

.translation-content {
  flex: 1;
  overflow: hidden;
  background: #f5f7fa;
}

/* 对照翻译容器 */
.parallel-container {
  display: flex;
  height: 100%;
  gap: 1px;
  background: #e4e7ed;
}

.parallel-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  overflow: hidden;
}

.panel-header {
  padding: 12px 20px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  font-weight: 600;
  color: #303133;
  text-align: center;
  position: sticky;
  top: 0;
  z-index: 10;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.panel-content::-webkit-scrollbar {
  width: 8px;
}

.panel-content::-webkit-scrollbar-track {
  background: #f5f7fa;
}

.panel-content::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 4px;
}

.panel-content::-webkit-scrollbar-thumb:hover {
  background: #c0c4cc;
}

.paper-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px dashed #e4e7ed;
}

.paper-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
  margin: 0 0 12px;
}

.section-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
}

.original-panel .section-title {
  color: #909399;
}

.translated-panel .section-title {
  color: #409eff;
}

/* 欢迎页面 */
.welcome-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.welcome-content {
  text-align: center;
  padding: 40px;
}

.welcome-content h2 {
  font-size: 24px;
  color: #303133;
  margin: 20px 0 10px;
}

.welcome-content p {
  color: #909399;
  margin: 0 0 40px;
}

.feature-list {
  display: flex;
  gap: 40px;
  justify-content: center;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  min-width: 200px;
}

.feature-item h4 {
  margin: 0 0 5px;
  font-size: 16px;
  color: #303133;
}

.feature-item p {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

:deep(.el-divider) {
  margin: 16px 0;
}
</style>
