import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const request = axios.create({
  baseURL: 'http://localhost:5000/api', // 后端API地址
  timeout: 30000 // 30秒超时，AI快速提取在20秒内完成
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    // 登录和注册请求不携带token（这是新的认证请求）
    const isAuthRequest = config.url?.includes('/login') || config.url?.includes('/register')

    if (token && !isAuthRequest) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    return res
  },
  error => {
    console.error('请求错误:', error)

    // 处理超时错误
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      ElMessage.error('请求超时，请检查网络连接后重试')
      return Promise.reject(error)
    }

    if (error.response) {
      const { status, data } = error.response
      switch (status) {
        case 400:
          ElMessage.error(data?.message || '请求参数错误')
          break
        case 401:
          // 登录失败：显示后端返回的具体错误消息
          if (data?.message) {
            ElMessage.error(data.message)
          } else {
            // Token过期：只有在非登录页才跳转
            ElMessage.error('登录已过期，请重新登录')
            if (!window.location.pathname.includes('/login')) {
              localStorage.removeItem('token')
              window.location.href = '/login'
            }
          }
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 404:
          ElMessage.error(data?.message || '请求的资源不存在')
          break
        case 408:
          ElMessage.error('请求超时，请检查网络连接后重试')
          break
        case 409:
          ElMessage.error(data?.message || '操作冲突，请稍后再试')
          break
        case 500:
          ElMessage.error(data?.message || '服务器错误，请稍后重试')
          break
        case 502:
        case 503:
        case 504:
          ElMessage.error('服务暂时不可用，请稍后重试')
          break
        default:
          ElMessage.error(data?.message || '请求失败')
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      ElMessage.error('网络连接失败，请检查网络')
    } else {
      // 请求配置错误
      ElMessage.error(error.message || '请求配置错误')
    }

    return Promise.reject(error)
  }
)

export default request
