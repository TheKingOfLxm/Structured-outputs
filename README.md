# 面向深度学术阅读的结构化内容生成系统

一个基于AI的学术阅读辅助系统，帮助用户快速理解学术论文的结构和核心内容。

## 系统功能

- **PDF论文上传与解析**: 自动提取论文标题、作者、摘要、关键词、章节等信息
- **思维导图生成**: 可视化展示论文结构
- **时间线生成**: 展示研究发展脉络
- **概念图谱生成**: 展示概念之间的知识关系
- **核心观点总结**: AI提炼论文主要贡献

## 技术栈

### 前端
- Vue 3
- Vite
- Element Plus
- Vue Router
- Axios
- ECharts

### 后端
- Flask 3.0
- SQLAlchemy
- JWT认证
- PyPDF2/pdfplumber
- 智谱AI API
- SQLite

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd 结构化内容生成系统
```

### 2. 启动后端

```bash
cd backend
# 方式1: 使用启动脚本（Windows）
start.bat

# 方式2: 手动启动
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python run.py
```

后端服务将运行在 `http://localhost:5000`

### 3. 启动前端

```bash
cd frontend
# 方式1: 使用启动脚本（Windows）
start.bat

# 方式2: 手动启动
npm install
npm run dev
```

前端服务将运行在 `http://localhost:5173`

### 4. 配置智谱AI密钥（可选）

编辑 `backend/.env` 文件：

```env
ZHIPUAI_API_KEY=your-api-key-here
```

获取API Key: https://open.bigmodel.cn/

> 如果不设置API Key，系统会使用模拟数据用于测试

## 使用指南

### 注册登录

1. 访问 `http://localhost:5173`
2. 点击"立即注册"创建账号
3. 使用用户名和密码登录

### 上传论文

1. 登录后进入"上传论文"页面
2. 拖拽或点击选择PDF文件
3. 点击"上传并解析"
4. 系统自动提取论文信息

### 生成内容

1. 在论文详情页点击"生成内容"
2. 选择生成类型：思维导图/时间线/概念图谱/核心观点
3. 等待AI生成结果
4. 可导出或保存生成结果

## 项目结构

```
结构化内容生成系统/
├── frontend/              # 前端项目
│   ├── src/
│   │   ├── api/          # API接口
│   │   ├── components/   # 组件
│   │   ├── router/       # 路由
│   │   ├── views/        # 页面
│   │   └── utils/        # 工具
│   ├── package.json
│   └── vite.config.js
│
├── backend/              # 后端项目
│   ├── app/
│   │   ├── api/          # API接口
│   │   ├── models.py     # 数据库模型
│   │   └── services/     # 业务逻辑
│   ├── config.py         # 配置
│   ├── requirements.txt  # 依赖
│   └── run.py           # 入口
│
└── README.md
```

## API文档

详细的API文档请查看：
- [前端README](./frontend/README.md)
- [后端README](./backend/README.md)

## 注意事项

1. **Python版本**: 需要Python 3.8或更高版本
2. **Node.js版本**: 需要Node.js 16或更高版本
3. **文件大小**: 单个PDF文件最大50MB
4. **API限流**: 智谱AI有调用频率限制

## 常见问题

**Q: 前端无法连接后端？**
A: 确保后端服务运行在 `http://localhost:5000`

**Q: PDF解析失败？**
A: 确保PDF是文本格式，扫描版PDF可能无法解析

**Q: AI生成失败？**
A: 检查智谱AI API Key是否正确设置

## 许可证

MIT License
