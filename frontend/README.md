# 学术阅读助手 - 前端

面向深度学术阅读的结构化内容生成系统前端项目

## 技术栈

- Vue 3
- Vite
- Vue Router 4
- Element Plus
- Axios
- ECharts

## 项目结构

```
frontend/
├── src/
│   ├── api/                # API接口
│   ├── assets/             # 静态资源
│   ├── components/         # 组件
│   ├── router/             # 路由配置
│   ├── utils/              # 工具函数
│   ├── views/              # 页面组件
│   ├── App.vue
│   └── main.js
├── index.html
├── package.json
└── vite.config.js
```

## 功能模块

### 1. 用户模块
- 用户注册/登录
- 个人信息管理
- 密码修改

### 2. 论文管理
- PDF论文上传
- 论文列表查看
- 论文详情展示
- 论文解析结果展示

### 3. 内容生成
- 思维导图生成
- 时间线生成
- 概念图谱生成
- 核心观点总结

## 开发指南

### 安装依赖
```bash
npm install
```

### 启动开发服务器
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

## 路由说明

| 路径 | 组件 | 说明 |
|------|------|------|
| /login | 登录页面 |
| /register | 注册页面 |
| /upload | 上传论文 |
| /papers | 论文列表 |
| /paper/:id | 论文详情 |
| /generate/:id | 内容生成 |
| /mindmap/:id | 思维导图 |
| /timeline/:id | 时间线 |
| /graph/:id | 概念图谱 |
| /profile | 个人中心 |
