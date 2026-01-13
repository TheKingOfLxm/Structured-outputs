<template>
  <div class="profile-page">
    <div class="content-wrapper">
      <el-card class="profile-card">
        <template #header>
          <div class="card-header">
            <el-icon><User /></el-icon>
            <span>个人中心</span>
          </div>
        </template>

        <el-tabs v-model="activeTab">
          <!-- 基本信息 -->
          <el-tab-pane label="基本信息" name="info">
            <div class="info-section">
              <div class="avatar-section">
                <el-avatar :size="100" :src="userInfo.avatar || defaultAvatar" />
                <el-button type="primary" link @click="handleAvatarChange">
                  <el-icon><Edit /></el-icon>
                  修改头像
                </el-button>
              </div>

              <el-form :model="userForm" :rules="rules" ref="userFormRef" label-width="100px">
                <el-form-item label="用户名" prop="username">
                  <el-input v-model="userForm.username" disabled />
                </el-form-item>

                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="userForm.email" />
                </el-form-item>

                <el-form-item>
                  <el-button type="primary" @click="handleUpdateInfo" :loading="updating">
                    保存修改
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>

          <!-- 修改密码 -->
          <el-tab-pane label="修改密码" name="password">
            <div class="password-section">
              <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
                <el-form-item label="当前密码" prop="oldPassword">
                  <el-input
                    v-model="passwordForm.oldPassword"
                    type="password"
                    show-password
                    placeholder="请输入当前密码"
                  />
                </el-form-item>

                <el-form-item label="新密码" prop="newPassword">
                  <el-input
                    v-model="passwordForm.newPassword"
                    type="password"
                    show-password
                    placeholder="请输入新密码"
                  />
                </el-form-item>

                <el-form-item label="确认密码" prop="confirmPassword">
                  <el-input
                    v-model="passwordForm.confirmPassword"
                    type="password"
                    show-password
                    placeholder="请再次输入新密码"
                  />
                </el-form-item>

                <el-form-item>
                  <el-button type="primary" @click="handleChangePassword" :loading="changing">
                    修改密码
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>

          <!-- 使用统计 -->
          <el-tab-pane label="使用统计" name="stats">
            <div class="stats-section">
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="stat-item">
                    <div class="stat-icon" style="background: #ecf5ff; color: #409eff;">
                      <el-icon :size="32"><Document /></el-icon>
                    </div>
                    <div class="stat-info">
                      <div class="stat-value">{{ stats.paperCount || 0 }}</div>
                      <div class="stat-label">上传论文</div>
                    </div>
                  </div>
                </el-col>

                <el-col :span="8">
                  <div class="stat-item">
                    <div class="stat-icon" style="background: #f0f9ff; color: #67c23a;">
                      <el-icon :size="32"><MagicStick /></el-icon>
                    </div>
                    <div class="stat-info">
                      <div class="stat-value">{{ stats.generateCount || 0 }}</div>
                      <div class="stat-label">生成次数</div>
                    </div>
                  </div>
                </el-col>

                <el-col :span="8">
                  <div class="stat-item">
                    <div class="stat-icon" style="background: #fef0f0; color: #f56c6c;">
                      <el-icon :size="32"><Clock /></el-icon>
                    </div>
                    <div class="stat-info">
                      <div class="stat-value">{{ stats.loginDays || 0 }}</div>
                      <div class="stat-label">使用天数</div>
                    </div>
                  </div>
                </el-col>
              </el-row>

              <div class="usage-chart">
                <h3>最近使用情况</h3>
                <div ref="chartRef" style="width: 100%; height: 300px;"></div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { userApi } from '@/api'

const activeTab = ref('info')
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const userInfo = ref({
  username: '',
  email: '',
  avatar: ''
})

const userForm = reactive({
  username: '',
  email: ''
})

const userFormRef = ref(null)
const updating = ref(false)

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const passwordFormRef = ref(null)
const changing = ref(false)

const stats = ref({
  paperCount: 0,
  generateCount: 0,
  loginDays: 0
})

const chartRef = ref(null)
let chart = null

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为6-20个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const loadUserInfo = async () => {
  try {
    const res = await userApi.getUserInfo()
    userInfo.value = res.data
    userForm.username = res.data.username
    userForm.email = res.data.email
  } catch (error) {
    console.error('加载失败:', error)
  }
}

const handleAvatarChange = () => {
  ElMessage.info('头像上传功能开发中')
}

const handleUpdateInfo = async () => {
  const valid = await userFormRef.value.validate().catch(() => false)
  if (!valid) return

  updating.value = true
  try {
    await userApi.updateUserInfo({
      email: userForm.email
    })
    ElMessage.success('保存成功')
    loadUserInfo()
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    updating.value = false
  }
}

const handleChangePassword = async () => {
  const valid = await passwordFormRef.value.validate().catch(() => false)
  if (!valid) return

  changing.value = true
  try {
    await userApi.changePassword({
      oldPassword: passwordForm.oldPassword,
      newPassword: passwordForm.newPassword
    })
    ElMessage.success('密码修改成功，请重新登录')
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    window.location.href = '/login'
  } catch (error) {
    console.error('修改失败:', error)
  } finally {
    changing.value = false
  }
}

const renderChart = () => {
  if (!chartRef.value) return

  if (chart) {
    chart.dispose()
  }

  chart = echarts.init(chartRef.value)

  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '生成次数',
        type: 'bar',
        data: [2, 4, 1, 3, 5, 2, 1],
        itemStyle: {
          color: '#409eff'
        }
      }
    ]
  }

  chart.setOption(option)
}

onMounted(() => {
  loadUserInfo()

  window.addEventListener('resize', () => {
    chart?.resize()
  })
})

// 监听tab切换，渲染图表
watch(activeTab, (newVal) => {
  if (newVal === 'stats') {
    nextTick(() => {
      renderChart()
    })
  }
})

onUnmounted(() => {
  if (chart) {
    chart.dispose()
  }
})
</script>

<style scoped>
.profile-page {
  height: 100%;
}

.content-wrapper {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.profile-card {
  min-height: calc(100vh - 120px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.info-section {
  max-width: 500px;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 40px;
}

.password-section {
  max-width: 500px;
}

.stats-section {
  padding: 20px 0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 30px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.stat-icon {
  width: 70px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.usage-chart {
  margin-top: 40px;
}

.usage-chart h3 {
  font-size: 16px;
  color: #303133;
  margin: 0 0 20px;
}
</style>
