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

    <!-- 右侧主内容区 -->
    <div class="main-content">
      <!-- 顶部状态栏 -->
      <div class="status-bar">
        <div class="current-kb">
          <el-icon><Collection /></el-icon>
          <span>{{ currentKb?.name || '默认知识库' }}</span>
          <el-tag size="small" type="info">{{ currentKb?.paperCount || 0 }} 篇论文</el-tag>
        </div>
        <div class="action-buttons">
          <el-button :icon="Setting" @click="modelDialogVisible = true">模型管理</el-button>
        </div>
      </div>

      <!-- 聊天内容区 -->
      <div class="chat-content">
        <!-- 欢迎页/问题建议 -->
        <div v-if="messages.length === 0" class="welcome-container">
          <!-- 搜索框 -->
          <div class="search-box">
            <el-input
              v-model="searchQuery"
              size="large"
              placeholder="搜索论文中的知识点..."
              :prefix-icon="Search"
              @keyup.enter="handleSearch"
              clearable
            />
          </div>

          <!-- 问题建议 -->
          <div class="suggestions-container">
            <h3 class="suggestions-title">你可以问：</h3>
            <div class="suggestions-grid">
              <div
                v-for="(suggestion, index) in suggestions"
                :key="index"
                class="suggestion-card"
                @click="askSuggestion(suggestion.question)"
              >
                <div class="suggestion-icon">
                  <el-icon>
                    <component :is="suggestion.icon" />
                  </el-icon>
                </div>
                <div class="suggestion-text">{{ suggestion.question }}</div>
              </div>
            </div>
          </div>

          <!-- 空状态提示 -->
          <div v-if="currentKb?.paperCount === 0" class="empty-state">
            <el-icon :size="60"><DocumentDelete /></el-icon>
            <p>此知识库暂无论文</p>
            <el-button type="primary" @click="openCreateDialog">添加论文</el-button>
          </div>
        </div>

        <!-- 对话消息列表 -->
        <div v-else class="messages-container" ref="messagesContainer">
          <div
            v-for="(message, index) in messages"
            :key="index"
            class="message-item"
            :class="message.role"
          >
            <div class="message-avatar" v-if="message.role === 'user'">
              <el-icon><User /></el-icon>
            </div>
            <div class="message-content">
              <div class="message-bubble" v-html="formatMessage(message.content)"></div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
            <div class="message-avatar" v-if="message.role === 'assistant'">
              <el-icon><ChatDotRound /></el-icon>
            </div>
          </div>

          <!-- 加载中 -->
          <div v-if="loading" class="message-item assistant">
            <div class="message-avatar">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="message-content">
              <div class="message-bubble loading">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部输入区 -->
      <div class="input-area">
        <div class="input-wrapper">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="1"
            :autosize="{ minRows: 1, maxRows: 4 }"
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
            size="large"
          />
        </div>
        <div class="input-footer">
          <span class="hint">按 Enter 发送，Shift + Enter 换行</span>
          <el-button v-if="messages.length > 0" link type="danger" @click="clearChat">
            <el-icon><Delete /></el-icon>
            清空对话
          </el-button>
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
  Collection, Search, User, ChatDotRound, Promotion,
  Delete, DocumentDelete, Reading, TrendCharts, Star, QuestionFilled,
  Setting, Plus, MoreFilled
} from '@element-plus/icons-vue'
import { paperApi, chatApi } from '@/api'

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
const knowledgeBases = ref([
  { id: 1, name: '默认知识库', paperCount: 4, type: 'personal', paperIds: [] },
  { id: 2, name: '机器学习论文', paperCount: 2, type: 'personal', paperIds: [] }
])
const currentKbId = ref(1)
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
    // 更新默认知识库的论文数量
    knowledgeBases.value[0].paperCount = allPapers.value.length
  } catch (error) {
    console.error('加载论文列表失败:', error)
  }
}

// 切换知识库
const switchKb = (kbId) => {
  currentKbId.value = kbId
  clearChat()
  ElMessage.success(`已切换到"${currentKb.value?.name}"`)
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
      const index = knowledgeBases.value.findIndex(k => k.id === kb.id)
      knowledgeBases.value.splice(index, 1)
      if (currentKbId.value === kb.id) {
        currentKbId.value = knowledgeBases.value[0]?.id
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

  setTimeout(() => {
    if (editingKb.value) {
      // 编辑现有知识库
      const index = knowledgeBases.value.findIndex(k => k.id === editingKb.value.id)
      if (index !== -1) {
        knowledgeBases.value[index] = {
          ...knowledgeBases.value[index],
          name: kbForm.value.name,
          type: kbForm.value.type,
          paperCount: kbForm.value.selectedPapers.length,
          paperIds: kbForm.value.selectedPapers,
          description: kbForm.value.description
        }
      }
      ElMessage.success('知识库已更新')
    } else {
      // 创建新知识库
      const newId = Math.max(...knowledgeBases.value.map(k => k.id)) + 1
      knowledgeBases.value.push({
        id: newId,
        name: kbForm.value.name,
        type: kbForm.value.type,
        paperCount: kbForm.value.selectedPapers.length,
        paperIds: kbForm.value.selectedPapers,
        description: kbForm.value.description
      })
      ElMessage.success(`知识库"${kbForm.value.name}"创建成功`)
    }

    closeCreateDialog()
    saving.value = false
  }, 500)
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
      history
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
})
</script>

<style scoped>
.knowledge-chat-page {
  height: 100%;
  display: flex;
  background: #f5f7fa;
}

/* 左侧边栏 */
.sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.kb-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.kb-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 8px;
  position: relative;
}

.kb-item:hover {
  background: #f5f7fa;
}

.kb-item.active {
  background: #ecf5ff;
  border: 1px solid #409eff;
}

.kb-icon {
  width: 40px;
  height: 40px;
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
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin: 0 0 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.kb-meta {
  font-size: 12px;
  color: #909399;
  margin: 0;
}

.more-btn {
  color: #909399;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.more-btn:hover {
  background: #e4e7ed;
}

/* 右侧主内容 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 状态栏 */
.status-bar {
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.current-kb {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #606266;
}

.current-kb .el-icon {
  color: #409eff;
  font-size: 18px;
}

/* 聊天内容区 */
.chat-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 欢迎容器 */
.welcome-container {
  flex: 1;
  overflow-y: auto;
  padding: 40px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.search-box {
  width: 100%;
  max-width: 600px;
  margin-bottom: 40px;
}

.search-box :deep(.el-input__wrapper) {
  border-radius: 24px;
  padding: 8px 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.search-box :deep(.el-input__inner) {
  font-size: 15px;
}

.suggestions-container {
  width: 100%;
  max-width: 800px;
}

.suggestions-title {
  font-size: 16px;
  color: #303133;
  margin: 0 0 20px;
  text-align: center;
}

.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.suggestion-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.suggestion-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.15);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.suggestion-card:hover .suggestion-icon,
.suggestion-card:hover .suggestion-text {
  color: white;
}

.suggestion-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ecf5ff;
  border-radius: 12px;
  color: #409eff;
  font-size: 24px;
  flex-shrink: 0;
  transition: all 0.3s;
}

.suggestion-text {
  font-size: 15px;
  color: #303133;
  font-weight: 500;
  transition: all 0.3s;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 60px;
  color: #909399;
}

.empty-state .el-icon {
  color: #c0c4cc;
  margin-bottom: 20px;
}

.empty-state p {
  font-size: 15px;
  margin: 0 0 20px;
}

/* 消息容器 */
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.message-item {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  align-items: flex-start;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-item.user .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.message-item.assistant .message-avatar {
  background: #ecf5ff;
  color: #409eff;
}

.message-content {
  max-width: 70%;
}

.message-item.user .message-content {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-bubble {
  padding: 14px 18px;
  border-radius: 16px;
  line-height: 1.7;
  word-break: break-word;
  font-size: 15px;
}

.message-item.user .message-bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 6px;
}

.message-item.assistant .message-bubble {
  background: white;
  color: #303133;
  border-bottom-left-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.message-bubble.loading {
  display: flex;
  gap: 6px;
  padding: 18px 24px;
}

.message-bubble.loading span {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #409eff;
  animation: bounce 1.4s infinite ease-in-out both;
}

.message-bubble.loading span:nth-child(1) {
  animation-delay: -0.32s;
}

.message-bubble.loading span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
}

.message-item.user .message-time {
  text-align: right;
}

/* 输入区 */
.input-area {
  padding: 16px 24px 20px;
  background: white;
  border-top: 1px solid #e4e7ed;
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  margin-bottom: 8px;
}

.input-wrapper .el-textarea {
  flex: 1;
}

.input-wrapper :deep(.el-textarea__inner) {
  border-radius: 20px;
  padding: 12px 16px;
  resize: none;
}

.input-wrapper .el-button {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 4px;
}

.hint {
  font-size: 12px;
  color: #909399;
}

/* 模型管理 */
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

.model-name {
  font-weight: 500;
  color: #303133;
}

.model-api {
  font-size: 12px;
  color: #909399;
}

.model-actions {
  display: flex;
  gap: 8px;
}

/* 论文选项 */
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

/* 响应式 */
@media (max-width: 768px) {
  .suggestions-grid {
    grid-template-columns: 1fr;
  }

  .message-content {
    max-width: 85%;
  }
}
</style>
