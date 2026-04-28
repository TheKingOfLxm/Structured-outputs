<template>
  <div class="knowledge-chat-page">
    <!-- 左侧知识库列表 -->
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>知识库</h3>
        <el-button :icon="Plus" size="small" circle @click="openCreateDialog" />
      </div>
      <div class="kb-list">
        <div
          v-for="kb in knowledgeBases"
          :key="kb.id"
          class="kb-item"
          :class="{ active: currentKbId === kb.id }"
          @click="switchKb(kb.id)"
        >
          <div class="kb-icon">
            <el-icon><Collection /></el-icon>
          </div>
          <div class="kb-info">
            <h4 class="kb-name">{{ kb.name }}</h4>
            <p class="kb-meta">{{ kb.paperCount }} 篇论文</p>
          </div>
          <el-dropdown @command="(cmd) => handleKbAction(cmd, kb)" trigger="click">
            <el-icon class="more-btn"><MoreFilled /></el-icon>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="edit">编辑</el-dropdown-item>
                <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <!-- 中间：PDF预览区 -->
    <div class="center-panel">
      <!-- 顶部信息栏 -->
      <div class="center-header">
        <div class="center-header-left">
          <el-icon><Collection /></el-icon>
          <span>{{ currentKb?.name || '选择知识库' }}</span>
          <el-tag size="small" type="info">{{ currentKb?.paperCount || 0 }} 篇论文</el-tag>
        </div>
        <div class="center-header-right">
          <el-button v-if="currentPdf" text @click="currentPdf = null">
            <el-icon><ArrowLeft /></el-icon>返回列表
          </el-button>
        </div>
      </div>

      <!-- PDF预览 -->
      <div v-if="currentPdf" class="center-pdf-viewer">
        <PdfReader :url="pdfPreviewUrl" />
      </div>

      <!-- 论文列表 -->
      <div v-else class="center-paper-list">
        <div v-if="kbPapersLoading" class="center-loading">
          <el-icon class="is-loading" :size="32"><Loading /></el-icon>
          <p>正在加载论文列表...</p>
        </div>
        <div v-else-if="kbPapers.length === 0" class="center-empty">
          <el-empty :description="currentKb ? '该知识库暂无论文' : '请先选择一个知识库'" />
        </div>
        <div v-else class="center-paper-grid">
          <div
            v-for="paper in kbPapers"
            :key="paper.id"
            class="paper-card"
            @click="openPdf(paper)"
          >
            <div class="paper-card-icon">
              <el-icon :size="36"><Document /></el-icon>
            </div>
            <div class="paper-card-body">
              <h4 class="paper-card-title">{{ paper.title || '未命名论文' }}</h4>
              <p class="paper-card-authors">{{ formatAuthors(paper.authors) }}</p>
            </div>
            <div class="paper-card-footer">
              <el-tag size="small" type="primary">点击预览</el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧：AI对话 -->
    <div class="right-sidebar">
      <div class="chat-header">
        <el-icon><ChatDotRound /></el-icon>
        <span>AI 对话</span>
        <el-button v-if="messages.length > 0" link size="small" @click="clearChat">
          <el-icon><Delete /></el-icon>
        </el-button>
      </div>

      <!-- 对话消息列表 -->
      <div class="chat-messages" ref="messagesContainer">
        <div v-if="messages.length === 0" class="chat-welcome">
          <el-icon :size="32" color="#409eff"><ChatDotRound /></el-icon>
          <p>向 AI 提问关于论文的问题</p>
          <div class="quick-questions">
            <el-tag
              v-for="(suggestion, index) in suggestions"
              :key="index"
              class="quick-tag"
              @click="askSuggestion(suggestion.question)"
            >
              {{ suggestion.question }}
            </el-tag>
          </div>
        </div>

        <div
          v-for="(message, index) in messages"
          :key="index"
          class="msg-item"
          :class="message.role"
        >
          <div class="msg-avatar" v-if="message.role === 'assistant'">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="msg-body">
            <div class="msg-bubble" v-html="formatMessage(message.content)"></div>
            <div class="msg-time">{{ formatTime(message.timestamp) }}</div>
          </div>
          <div class="msg-avatar user-avatar" v-if="message.role === 'user'">
            <el-icon><User /></el-icon>
          </div>
        </div>

        <div v-if="loading" class="msg-item assistant">
          <div class="msg-avatar">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="msg-body">
            <div class="msg-bubble loading-dots">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部输入区 -->
      <div class="chat-input-area">
        <div class="chat-input-wrapper">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="1"
            :autosize="{ minRows: 1, maxRows: 3 }"
            placeholder="输入你的问题..."
            @keydown.enter.exact="sendMessage"
            @keydown.enter.shift.prevent
            :disabled="loading || !currentKb?.paperCount"
          />
          <el-button
            type="primary"
            :icon="Promotion"
            @click="sendMessage"
            :loading="loading"
            :disabled="!inputMessage.trim() || !currentKb?.paperCount"
            circle
          />
        </div>
      </div>
    </div>

    <!-- 模型管理弹窗 -->
    <el-dialog v-model="modelDialogVisible" title="模型管理" width="600px">
      <div class="model-manager">
        <div class="model-list">
          <div v-for="(model, index) in aiModels" :key="index" class="model-item">
            <div class="model-info">
              <el-tag :type="model.isDefault ? 'primary' : 'info'" size="small">
                {{ model.isDefault ? '默认' : '' }}
              </el-tag>
              <span class="model-name">{{ model.name }}</span>
              <span class="model-api">{{ model.provider }}</span>
            </div>
            <div class="model-actions">
              <el-button v-if="!model.isDefault" size="small" @click="setDefaultModel(index)">设为默认</el-button>
              <el-button size="small" type="danger" :icon="Delete" @click="deleteModel(index)" />
            </div>
          </div>
        </div>
        <el-divider />
        <h4>添加新模型</h4>
        <el-form :model="newModel" label-width="80px">
          <el-form-item label="模型名称">
            <el-input v-model="newModel.name" placeholder="如：GPT-4" />
          </el-form-item>
          <el-form-item label="服务提供商">
            <el-select v-model="newModel.provider" placeholder="选择提供商">
              <el-option label="OpenAI" value="openai" />
              <el-option label="智谱AI" value="zhipuai" />
              <el-option label="文心一言" value="ernie" />
              <el-option label="通义千问" value="qwen" />
            </el-select>
          </el-form-item>
          <el-form-item label="API密钥">
            <el-input v-model="newModel.apiKey" type="password" placeholder="请输入API密钥" show-password />
          </el-form-item>
          <el-form-item label="API地址">
            <el-input v-model="newModel.apiUrl" placeholder="可选，自定义API地址" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="addModel" :disabled="!newModel.name || !newModel.apiKey">
              添加模型
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-dialog>

    <!-- 创建/编辑知识库弹窗 -->
    <el-dialog
      v-model="createDialogVisible"
      :title="editingKb ? '编辑知识库' : '创建知识库'"
      width="600px"
    >
      <el-form :model="kbForm" label-width="100px" :rules="kbRules" ref="kbFormRef">
        <el-form-item label="知识库名称" prop="name">
          <el-input v-model="kbForm.name" placeholder="输入知识库名称" />
        </el-form-item>
        <el-form-item label="知识库类型" prop="type">
          <el-radio-group v-model="kbForm.type">
            <el-radio label="personal">个人知识库</el-radio>
            <el-radio label="shared">共享知识库</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="选择论文" prop="papers">
          <el-select
            v-model="kbForm.selectedPapers"
            multiple
            collapse-tags
            collapse-tags-tooltip
            placeholder="选择要包含的论文"
            style="width: 100%"
          >
            <el-option
              v-for="paper in allPapers"
              :key="paper.id"
              :label="paper.title"
              :value="paper.id"
            >
              <div class="paper-option">
                <span class="paper-title">{{ paper.title }}</span>
                <span class="paper-category">{{ paper.category || '未分类' }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="kbForm.description" type="textarea" :rows="3" placeholder="描述这个知识库" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveKb" :loading="saving">
            {{ editingKb ? '保存' : '创建' }}
          </el-button>
          <el-button @click="closeCreateDialog">取消</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Collection, User, ChatDotRound, Promotion,
  Delete,
  Plus, MoreFilled, Document, Loading, ArrowLeft
} from '@element-plus/icons-vue'
import { paperApi, chatApi } from '@/api'
import PdfReader from '@/components/PdfReader.vue'

const router = useRouter()
const messages = ref([])
const inputMessage = ref('')
const searchQuery = ref('')
const loading = ref(false)
const messagesContainer = ref(null)

// 弹窗状态
const modelDialogVisible = ref(false)
const createDialogVisible = ref(false)
const saving = ref(false)
const editingKb = ref(null)
const kbFormRef = ref(null)

// 知识库数据
const knowledgeBases = ref([])
const currentKbId = ref(null)
const allPapers = ref([])

// 当前知识库
const currentKb = computed(() => {
  return knowledgeBases.value.find(kb => kb.id === currentKbId.value)
})

// AI模型列表
const aiModels = ref([
  { name: 'GLM-4-Flash', provider: '智谱AI', apiKey: '***', isDefault: true },
  { name: 'GPT-3.5', provider: 'OpenAI', apiKey: '***', isDefault: false }
])

// 新模型表单
const newModel = ref({
  name: '',
  provider: 'zhipuai',
  apiKey: '',
  apiUrl: ''
})

// 知识库表单
const kbForm = ref({
  name: '',
  type: 'personal',
  selectedPapers: [],
  description: ''
})

// 中间面板 - 论文列表和PDF预览
const kbPapers = ref([])
const kbPapersLoading = ref(false)
const currentPdf = ref(null)
const pdfPreviewUrl = computed(() => {
  if (!currentPdf.value) return ''
  return paperApi.getPaperViewUrl(currentPdf.value.id)
})

const kbRules = {
  name: [{ required: true, message: '请输入知识库名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择知识库类型', trigger: 'change' }]
}

// 问题建议
const suggestions = [
  { question: '这篇论文的核心观点是什么？', icon: 'QuestionFilled' },
  { question: '论文采用了哪些研究方法？', icon: 'Reading' },
  { question: '实验结果如何？', icon: 'TrendCharts' },
  { question: '论文有什么创新点？', icon: 'Star' }
]

// 加载所有论文
const loadAllPapers = async () => {
  try {
    const res = await paperApi.getPaperList({ page: 1, pageSize: 100 })
    allPapers.value = res.data.list.filter(p => p.status === 'parsed')
  } catch (error) {
    console.error('加载论文列表失败:', error)
  }
}

// 加载知识库列表
const loadKnowledgeBases = async () => {
  try {
    const res = await chatApi.getKnowledgeBases()
    knowledgeBases.value = res.data.list
    if (!currentKbId.value && knowledgeBases.value.length > 0) {
      currentKbId.value = knowledgeBases.value[0].id
    }
  } catch (error) {
    console.error('加载知识库列表失败:', error)
  }
}

// 切换知识库
const switchKb = (kbId) => {
  currentKbId.value = kbId
  currentPdf.value = null
  clearChat()
  loadKbPapers()
  ElMessage.success(`已切换到"${currentKb.value?.name}"`)
}

// 加载知识库论文列表
const loadKbPapers = async () => {
  if (!currentKb.value?.paperIds?.length) {
    kbPapers.value = []
    return
  }
  kbPapersLoading.value = true
  try {
    const promises = currentKb.value.paperIds.map(id => paperApi.getPaperDetail(id))
    const results = await Promise.all(promises)
    kbPapers.value = results.map(res => res.data)
  } catch (error) {
    console.error('加载知识库论文失败:', error)
    ElMessage.error('加载论文列表失败')
  } finally {
    kbPapersLoading.value = false
  }
}

// 打开PDF预览
const openPdf = (paper) => {
  currentPdf.value = paper
}

// 格式化作者
const formatAuthors = (authors) => {
  if (!authors) return '未知作者'
  if (Array.isArray(authors)) return authors.join(', ')
  if (typeof authors === 'string') {
    try {
      const parsed = JSON.parse(authors)
      if (Array.isArray(parsed)) return parsed.join(', ')
    } catch (e) { /* ignore */ }
  }
  return authors
}

// 知识库操作
const handleKbAction = async (command, kb) => {
  if (command === 'edit') {
    openEditDialog(kb)
  } else if (command === 'delete') {
    try {
      await ElMessageBox.confirm(`确定要删除知识库"${kb.name}"吗？`, '提示', {
        type: 'warning'
      })
      await chatApi.deleteKnowledgeBase(kb.id)
      await loadKnowledgeBases()
      if (currentKbId.value === kb.id) {
        currentKbId.value = knowledgeBases.value[0]?.id || null
      }
      ElMessage.success('删除成功')
    } catch {
      // 取消删除
    }
  }
}

// 打开创建弹窗
const openCreateDialog = () => {
  editingKb.value = null
  kbForm.value = {
    name: '',
    type: 'personal',
    selectedPapers: [],
    description: ''
  }
  createDialogVisible.value = true
}

// 打开编辑弹窗
const openEditDialog = (kb) => {
  editingKb.value = kb
  kbForm.value = {
    name: kb.name,
    type: kb.type,
    selectedPapers: [...(kb.paperIds || [])],
    description: kb.description || ''
  }
  createDialogVisible.value = true
}

// 关闭弹窗
const closeCreateDialog = () => {
  createDialogVisible.value = false
  editingKb.value = null
  kbForm.value = { name: '', type: 'personal', selectedPapers: [], description: '' }
}

// 保存知识库
const saveKb = async () => {
  if (!kbForm.value.name) {
    ElMessage.warning('请输入知识库名称')
    return
  }

  if (kbForm.value.selectedPapers.length === 0) {
    ElMessage.warning('请选择至少一篇论文')
    return
  }

  saving.value = true
  try {
    if (editingKb.value) {
      await chatApi.updateKnowledgeBase(editingKb.value.id, {
        name: kbForm.value.name,
        type: kbForm.value.type,
        paperIds: kbForm.value.selectedPapers,
        description: kbForm.value.description
      })
      ElMessage.success('知识库已更新')
    } else {
      await chatApi.createKnowledgeBase({
        name: kbForm.value.name,
        type: kbForm.value.type,
        paperIds: kbForm.value.selectedPapers,
        description: kbForm.value.description
      })
      ElMessage.success(`知识库"${kbForm.value.name}"创建成功`)
    }
    await loadKnowledgeBases()
    closeCreateDialog()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '操作失败')
  } finally {
    saving.value = false
  }
}

// 发送消息
const sendMessage = async () => {
  const question = inputMessage.value.trim()
  if (!question || loading.value || !currentKb.value?.paperCount) return

  messages.value.push({
    role: 'user',
    content: question,
    timestamp: new Date()
  })

  inputMessage.value = ''
  loading.value = true

  await nextTick()
  scrollToBottom()

  try {
    const history = messages.value.slice(0, -1).map(m => ({ role: m.role, content: m.content }))

    // 根据当前知识库筛选论文
    let papersToUse = allPapers.value
    if (currentKb.value?.paperIds && currentKb.value.paperIds.length > 0) {
      papersToUse = allPapers.value.filter(p => currentKb.value.paperIds.includes(p.id))
    }

    const papersInfo = papersToUse.map(p => ({
      title: p.title,
      abstract: p.abstract,
      keywords: p.keywords
    }))

    const res = await chatApi.chatWithPapers({
      question,
      history,
      paperIds: currentKb.value?.paperIds || []
    })

    messages.value.push({
      role: 'assistant',
      content: res.data.answer,
      timestamp: new Date()
    })

    await nextTick()
    scrollToBottom()
  } catch (error) {
    console.error('对话失败:', error)
    ElMessage.error(error.response?.data?.message || '对话失败，请重试')
  } finally {
    loading.value = false
  }
}

// 搜索功能
const handleSearch = () => {
  if (searchQuery.value.trim()) {
    inputMessage.value = `关于"${searchQuery.value}"，这些论文讲了什么？`
    sendMessage()
    searchQuery.value = ''
  }
}

// 点击建议问题
const askSuggestion = (question) => {
  inputMessage.value = question
  sendMessage()
}

// 清空对话
const clearChat = () => {
  messages.value = []
}

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 格式化消息
const formatMessage = (content) => {
  if (!content) return ''
  let formatted = content.replace(/\n/g, '<br>')
  formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  return formatted
}

// 格式化时间
const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

// 模型管理方法
const setDefaultModel = (index) => {
  aiModels.value.forEach((m, i) => m.isDefault = i === index)
  ElMessage.success('已设置默认模型')
}

const deleteModel = (index) => {
  aiModels.value.splice(index, 1)
  ElMessage.success('已删除模型')
}

const addModel = () => {
  if (!newModel.value.name || !newModel.value.apiKey) {
    ElMessage.warning('请填写模型名称和API密钥')
    return
  }

  aiModels.value.push({
    name: newModel.value.name,
    provider: newModel.value.provider === 'zhipuai' ? '智谱AI' :
            newModel.value.provider === 'openai' ? 'OpenAI' :
            newModel.value.provider === 'ernie' ? '文心一言' : '通义千问',
    apiKey: newModel.value.apiKey,
    isDefault: false
  })

  ElMessage.success('模型添加成功')
  newModel.value = { name: '', provider: 'zhipuai', apiKey: '', apiUrl: '' }
}

onMounted(() => {
  loadAllPapers()
  loadKnowledgeBases()
})
</script>

<style scoped>
/* ===== 三栏布局 ===== */
.knowledge-chat-page {
  height: 100%;
  display: flex;
  background: #f5f7fa;
}

/* ===== 左侧：知识库列表 ===== */
.sidebar {
  width: 240px;
  background: white;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 15px;
  color: #303133;
}

.kb-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.kb-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 4px;
}

.kb-item:hover {
  background: #f5f7fa;
}

.kb-item.active {
  background: #ecf5ff;
  border: 1px solid #409eff;
}

.kb-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ecf5ff;
  border-radius: 8px;
  color: #409eff;
  flex-shrink: 0;
}

.kb-info {
  flex: 1;
  min-width: 0;
}

.kb-name {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  margin: 0 0 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.kb-meta {
  font-size: 11px;
  color: #909399;
  margin: 0;
}

.more-btn {
  color: #909399;
  cursor: pointer;
  padding: 2px;
  border-radius: 4px;
}

.more-btn:hover {
  background: #e4e7ed;
}

/* ===== 中间：PDF预览区 ===== */
.center-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-right: 1px solid #e4e7ed;
}

.center-header {
  padding: 12px 20px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 48px;
}

.center-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.center-header-left .el-icon {
  color: #409eff;
}

.center-pdf-viewer {
  flex: 1;
  overflow: hidden;
}

.center-paper-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.center-loading,
.center-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}

.center-loading p {
  margin-top: 12px;
  font-size: 14px;
}

.center-paper-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.paper-card {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 10px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.paper-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.12);
  transform: translateY(-2px);
}

.paper-card-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ecf5ff;
  border-radius: 10px;
  color: #409eff;
}

.paper-card-body {
  flex: 1;
  min-width: 0;
}

.paper-card-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin: 0 0 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.4;
}

.paper-card-authors {
  font-size: 12px;
  color: #909399;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.paper-card-footer {
  display: flex;
  justify-content: flex-end;
}

/* ===== 右侧：AI对话 ===== */
.right-sidebar {
  width: 360px;
  background: white;
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.chat-header .el-icon {
  color: #409eff;
}

.chat-header span {
  flex: 1;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.chat-welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 16px;
  gap: 12px;
}

.chat-welcome p {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

.quick-questions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.quick-tag {
  cursor: pointer;
  width: 100%;
  text-align: center;
  justify-content: center;
  font-size: 12px;
}

.msg-item {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  align-items: flex-start;
}

.msg-item.user {
  flex-direction: row-reverse;
}

.msg-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: #ecf5ff;
  color: #409eff;
  font-size: 14px;
}

.msg-avatar.user-avatar {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.msg-body {
  max-width: 85%;
}

.msg-item.user .msg-body {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.msg-bubble {
  padding: 10px 14px;
  border-radius: 12px;
  line-height: 1.6;
  word-break: break-word;
  font-size: 13px;
}

.msg-item.user .msg-bubble {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-bottom-right-radius: 4px;
}

.msg-item.assistant .msg-bubble {
  background: #f5f7fa;
  color: #303133;
  border-bottom-left-radius: 4px;
}

.loading-dots {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #409eff;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.msg-time {
  font-size: 11px;
  color: #c0c4cc;
  margin-top: 4px;
}

.msg-item.user .msg-time {
  text-align: right;
}

.chat-input-area {
  padding: 12px;
  border-top: 1px solid #e4e7ed;
}

.chat-input-wrapper {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.chat-input-wrapper .el-textarea {
  flex: 1;
}

.chat-input-wrapper :deep(.el-textarea__inner) {
  border-radius: 16px;
  padding: 8px 14px;
  resize: none;
  font-size: 13px;
}

.chat-input-wrapper .el-button {
  flex-shrink: 0;
}

/* ===== 弹窗通用 ===== */
.model-list {
  max-height: 200px;
  overflow-y: auto;
}

.model-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 8px;
}

.model-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.model-name { font-weight: 500; color: #303133; }
.model-api { font-size: 12px; color: #909399; }
.model-actions { display: flex; gap: 8px; }

.paper-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.paper-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.paper-category {
  font-size: 12px;
  color: #909399;
  margin-left: 12px;
}

/* ===== 响应式 ===== */
@media (max-width: 1024px) {
  .center-paper-grid {
    grid-template-columns: 1fr;
  }
}
</style>
