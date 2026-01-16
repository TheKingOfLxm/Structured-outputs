import request from '@/utils/request'

// 用户相关接口
export const userApi = {
  // 登录
  login(data) {
    return request({
      url: '/user/login',
      method: 'post',
      data
    })
  },

  // 注册
  register(data) {
    return request({
      url: '/user/register',
      method: 'post',
      data
    })
  },

  // 获取用户信息
  getUserInfo() {
    return request({
      url: '/user/info',
      method: 'get'
    })
  },

  // 更新用户信息
  updateUserInfo(data) {
    return request({
      url: '/user/info',
      method: 'put',
      data
    })
  },

  // 修改密码
  changePassword(data) {
    return request({
      url: '/user/password',
      method: 'put',
      data
    })
  }
}

// 论文相关接口
export const paperApi = {
  // 上传论文
  uploadPaper(formData) {
    return request({
      url: '/paper/upload',
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 获取论文列表
  getPaperList(params) {
    return request({
      url: '/paper/list',
      method: 'get',
      params
    })
  },

  // 获取论文详情
  getPaperDetail(id) {
    return request({
      url: `/paper/${id}`,
      method: 'get'
    })
  },

  // 删除论文
  deletePaper(id) {
    return request({
      url: `/paper/${id}`,
      method: 'delete'
    })
  },

  // 解析论文
  parsePaper(id) {
    return request({
      url: `/paper/${id}/parse`,
      method: 'post'
    })
  }
}

// 内容生成相关接口
export const generateApi = {
  // 生成思维导图
  generateMindMap(data) {
    return request({
      url: '/generate/mindmap',
      method: 'post',
      data
    })
  },

  // 生成时间线
  generateTimeline(data) {
    return request({
      url: '/generate/timeline',
      method: 'post',
      data
    })
  },

  // 生成概念图谱
  generateGraph(data) {
    return request({
      url: '/generate/graph',
      method: 'post',
      data
    })
  },

  // 生成核心观点
  generateSummary(data) {
    return request({
      url: '/generate/summary',
      method: 'post',
      data
    })
  },

  // 生成论文评审报告
  generateReview(data) {
    return request({
      url: '/generate/review',
      method: 'post',
      data
    })
  },

  // 获取生成历史
  getGenerateHistory(paperId) {
    return request({
      url: `/generate/history/${paperId}`,
      method: 'get'
    })
  },

  // 保存生成结果
  saveGenerateResult(data) {
    return request({
      url: '/generate/save',
      method: 'post',
      data
    })
  }
}

// 导出相关接口
export const exportApi = {
  // 导出思维导图
  exportMindMap(id) {
    return request({
      url: `/export/mindmap/${id}`,
      method: 'get',
      responseType: 'blob'
    })
  },

  // 导出时间线
  exportTimeline(id) {
    return request({
      url: `/export/timeline/${id}`,
      method: 'get',
      responseType: 'blob'
    })
  },

  // 导出概念图谱
  exportGraph(id) {
    return request({
      url: `/export/graph/${id}`,
      method: 'get',
      responseType: 'blob'
    })
  }
}
