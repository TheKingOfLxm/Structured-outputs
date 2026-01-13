<template>
  <div class="paper-list-page">
    <div class="content-wrapper">
      <el-card class="list-card">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <el-icon><Document /></el-icon>
              <span>我的论文</span>
            </div>
            <el-button type="primary" @click="goToUpload">
              <el-icon><Upload /></el-icon>
              上传论文
            </el-button>
          </div>
        </template>

        <!-- 搜索筛选 -->
        <div class="filter-bar">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索论文标题"
            clearable
            style="width: 300px"
            @clear="loadPaperList"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
        </div>

        <!-- 论文列表 -->
        <div v-loading="loading" class="paper-list">
          <el-empty v-if="!loading && paperList.length === 0" description="暂无论文，快去上传吧" />

          <div v-for="paper in paperList" :key="paper.id" class="paper-item" @click="goToDetail(paper.id)">
            <div class="paper-icon">
              <el-icon :size="40"><Document /></el-icon>
            </div>
            <div class="paper-content">
              <h3 class="paper-title">{{ paper.title || '未命名论文' }}</h3>
              <div class="paper-meta">
                <span class="meta-item">
                  <el-icon><User /></el-icon>
                  {{ paper.authors || '未知作者' }}
                </span>
                <span class="meta-item">
                  <el-icon><Calendar /></el-icon>
                  {{ formatDate(paper.uploadTime) }}
                </span>
              </div>
              <p v-if="paper.abstract" class="paper-abstract">
                {{ paper.abstract.substring(0, 150) }}...
              </p>
              <div class="paper-tags">
                <el-tag v-if="paper.status === 'parsed'" type="success" size="small">已解析</el-tag>
                <el-tag v-else-if="paper.status === 'parsing'" type="warning" size="small">解析中</el-tag>
                <el-tag v-else type="info" size="small">待解析</el-tag>
              </div>
            </div>
            <div class="paper-actions">
              <el-button type="primary" link @click.stop="goToGenerate(paper.id)">
                <el-icon><MagicStick /></el-icon>
                生成内容
              </el-button>
              <el-button type="danger" link @click.stop="handleDelete(paper)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="total > 0" class="pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadPaperList"
            @current-change="loadPaperList"
          />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { paperApi } from '@/api'

const router = useRouter()
const loading = ref(false)
const paperList = ref([])
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const loadPaperList = async () => {
  loading.value = true
  try {
    const res = await paperApi.getPaperList({
      page: currentPage.value,
      pageSize: pageSize.value,
      keyword: searchKeyword.value
    })
    paperList.value = res.data.list || []
    total.value = res.data.total || 0
  } catch (error) {
    console.error('加载失败:', error)
    ElMessage.error('加载论文列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadPaperList()
}

const goToUpload = () => {
  router.push('/upload')
}

const goToDetail = (id) => {
  router.push(`/paper/${id}`)
}

const goToGenerate = (id) => {
  router.push(`/generate/${id}`)
}

const handleDelete = (paper) => {
  ElMessageBox.confirm(
    `确定要删除论文《${paper.title}》吗？删除后将无法恢复。`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await paperApi.deletePaper(paper.id)
      ElMessage.success('删除成功')
      loadPaperList()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

const formatDate = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

onMounted(() => {
  loadPaperList()
})
</script>

<style scoped>
.paper-list-page {
  height: 100%;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.list-card {
  min-height: calc(100vh - 120px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.paper-list {
  min-height: 400px;
}

.paper-item {
  display: flex;
  gap: 20px;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.paper-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.1);
}

.paper-icon {
  color: #409eff;
  flex-shrink: 0;
}

.paper-content {
  flex: 1;
  min-width: 0;
}

.paper-title {
  font-size: 18px;
  color: #303133;
  margin: 0 0 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.paper-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 10px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #909399;
}

.paper-abstract {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin: 10px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.paper-tags {
  margin-top: 10px;
}

.paper-actions {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 10px;
  flex-shrink: 0;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
