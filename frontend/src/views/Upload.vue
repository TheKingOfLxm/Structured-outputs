<template>
  <div class="upload-page">
    <div class="content-wrapper">
      <el-card class="upload-card">
        <template #header>
          <div class="card-header">
            <el-icon><Upload /></el-icon>
            <span>上传PDF论文</span>
          </div>
        </template>

        <el-upload
          ref="uploadRef"
          class="upload-area"
          drag
          action="#"
          :auto-upload="false"
          :limit="1"
          accept=".pdf"
          :on-change="handleFileChange"
          :on-exceed="handleExceed"
          :on-remove="handleRemove"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将PDF文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              仅支持PDF格式，文件大小不超过50MB
            </div>
          </template>
        </el-upload>

        <div v-if="selectedFile" class="file-info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="文件名">{{ selectedFile.name }}</el-descriptions-item>
            <el-descriptions-item label="文件大小">{{ formatFileSize(selectedFile.size) }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="upload-actions">
          <el-button
            type="primary"
            size="large"
            :loading="uploading"
            :disabled="!selectedFile"
            @click="handleUpload"
          >
            <el-icon><Upload /></el-icon>
            上传并解析
          </el-button>
          <el-button size="large" @click="handleReset">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </div>
      </el-card>

      <!-- 上传说明 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <el-icon><InfoFilled /></el-icon>
            <span>使用说明</span>
          </div>
        </template>

        <div class="info-content">
          <h3>支持的论文类型</h3>
          <ul>
            <li>学术期刊论文</li>
            <li>学位论文（硕士、博士）</li>
            <li>会议论文</li>
            <li>技术报告</li>
          </ul>

          <h3>系统功能</h3>
          <ul>
            <li>自动提取论文元数据（标题、作者、摘要、关键词）</li>
            <li>生成思维导图，展示论文结构</li>
            <li>生成时间线，展示研究演进</li>
            <li>生成概念图谱，展示知识关系</li>
            <li>生成核心观点总结</li>
          </ul>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UploadFilled, InfoFilled } from '@element-plus/icons-vue'
import { paperApi } from '@/api'

const router = useRouter()
const uploadRef = ref(null)
const selectedFile = ref(null)
const uploading = ref(false)

const handleFileChange = (file) => {
  if (file.raw.type !== 'application/pdf') {
    ElMessage.error('只能上传PDF文件')
    uploadRef.value.clearFiles()
    return
  }
  if (file.raw.size > 50 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过50MB')
    uploadRef.value.clearFiles()
    return
  }
  selectedFile.value = file.raw
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个文件，请先删除已上传的文件')
}

const handleRemove = () => {
  selectedFile.value = null
}

const handleUpload = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const res = await paperApi.uploadPaper(formData)
    ElMessage.success('上传成功，正在解析...')

    // 跳转到论文详情页
    setTimeout(() => {
      router.push(`/paper/${res.data.paperId}`)
    }, 1000)
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error(error.message || '上传失败，请重试')
  } finally {
    uploading.value = false
  }
}

const handleReset = () => {
  uploadRef.value?.clearFiles()
  selectedFile.value = null
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}
</script>

<style scoped>
.upload-page {
  height: 100%;
}

.content-wrapper {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.upload-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.upload-area {
  margin: 20px 0;
}

.upload-area :deep(.el-upload-dragger) {
  padding: 60px 20px;
}

.file-info {
  margin: 20px 0;
}

.upload-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}

.info-card h3 {
  font-size: 16px;
  color: #303133;
  margin: 20px 0 10px;
}

.info-card h3:first-child {
  margin-top: 0;
}

.info-card ul {
  list-style: none;
  padding-left: 0;
}

.info-card ul li {
  padding: 8px 0;
  color: #606266;
  position: relative;
  padding-left: 20px;
}

.info-card ul li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #409eff;
  font-size: 18px;
  line-height: 1.5;
}
</style>
