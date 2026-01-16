# 面向深度学术阅读的结构化内容生成系统

一个基于AI的学术阅读辅助系统，帮助用户快速理解学术论文的结构和核心内容。

![学术阅读助手](https://img.shields.io/badge/Academic-Reading-blue) ![Vue 3](https://img.shields.io/badge/Vue-3.0-brightgreen) ![Flask](https://img.shields.io/badge/Flask-3.0-red)

## 系统功能

- **PDF论文上传与解析**: 自动提取论文标题、作者、摘要、关键词等信息
- **论文阅读报告**: AI生成包含8个学术要素的阅读报告
  - 摘要、关键词、研究问题、方法、结果、讨论、创新点、技术问题
- **论文评审报告**: 基于学术要素完整性进行评分
  - 标题质量、摘要质量、关键词质量、研究问题清晰度
  - 方法严谨性、实验有效性、结果可靠性、创新水平
- **思维导图生成**: 可视化展示论文结构
- **时间线生成**: 展示研究发展脉络
- **概念图谱生成**: 展示概念之间的知识关系

## 系统要求

### 环境依赖

| 组件 | 最低版本 | 推荐版本 |
|------|---------|---------|
| Python | 3.8+ | 3.10+ |
| Node.js | 16+ | 18+ |
| npm | 8+ | 10+ |

### 可选服务

- **智谱AI API Key**: 用于AI内容生成（[获取地址](https://open.bigmodel.cn/)）
  - 不配置时系统会使用模拟数据

## 快速开始

### 方式一：使用启动脚本（推荐，Windows）

#### 1. 启动后端服务

```bash
cd backend
start.bat
```

脚本会自动完成以下操作：
- 创建Python虚拟环境
- 安装所有依赖
- 创建配置文件 `.env`
- 启动后端服务

后端服务将运行在 `http://localhost:5000`

#### 2. 启动前端服务

打开新的命令行窗口：

```bash
cd frontend
start.bat
```

前端服务将运行在 `http://localhost:5173`

### 方式二：手动启动（跨平台）

#### 1. 启动后端

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（首次运行）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖（首次运行）
pip install -r requirements.txt

# 创建配置文件（首次运行）
# 复制 .env.example 为 .env 并编辑
cp .env.example .env  # Linux/Mac
copy .env.example .env  # Windows

# 启动服务
python run.py
```

后端服务将运行在 `http://localhost:5000`

#### 2. 启动前端

打开新的命令行窗口：

```bash
# 进入前端目录
cd frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

前端服务将运行在 `http://localhost:5173`

### 3. 配置智谱AI密钥

编辑 `backend/.env` 文件：

```env
# 基础配置（已自动生成）
SECRET_KEY=dev-secret-key
JWT_SECRET_KEY=dev-jwt-secret-key

# 智谱AI配置（需要手动填写）
ZHIPUAI_API_KEY=your-api-key-here
```

获取API Key: https://open.bigmodel.cn/

> **注意**: 不设置API Key时，系统会使用模拟数据用于测试

### 4. 访问系统

打开浏览器访问：`http://localhost:5173`

## 使用指南

### 注册登录

1. 访问 `http://localhost:5173`
2. 点击"立即注册"创建账号
3. 输入用户名和密码进行注册
4. 使用注册的账号密码登录

### 上传论文

1. 登录后进入"论文管理"页面
2. 点击"上传论文"按钮
3. 选择PDF文件（支持拖拽上传）
4. 点击"上传并解析"
5. 系统自动提取论文信息

### 查看论文详情

1. 在论文列表中点击论文标题
2. 查看论文基本信息（标题、作者、摘要、关键词）
3. 查看论文阅读报告（八元组）
4. 查看论文评审报告（评分）

### 生成内容

在论文详情页可以生成以下内容：

| 功能 | 说明 | 耗时 |
|------|------|------|
| 思维导图 | 可视化展示论文结构 | ~15秒 |
| 时间线 | 展示研究发展脉络 | ~15秒 |
| 概念图谱 | 展示概念知识关系 | ~20秒 |
| 阅读报告 | 提炼核心观点（八元组） | ~20秒 |
| 评审报告 | 学术要素完整性评分 | ~20秒 |

## 项目结构

```
结构化内容生成系统/
├── frontend/                    # 前端项目（Vue 3 + Vite）
│   ├── src/
│   │   ├── api/                # API接口封装
│   │   ├── components/         # 可复用组件
│   │   ├── router/             # 路由配置
│   │   ├── views/              # 页面组件
│   │   │   ├── Login.vue       # 登录页
│   │   │   ├── PaperList.vue   # 论文列表
│   │   │   ├── PaperDetail.vue # 论文详情
│   │   │   ├── Generate.vue    # 内容生成
│   │   │   └── ...
│   │   └── utils/              # 工具函数
│   ├── public/                 # 静态资源
│   │   └── logo.svg            # 网站图标
│   ├── package.json
│   └── vite.config.js
│
├── backend/                     # 后端项目（Flask）
│   ├── app/
│   │   ├── api/                # API路由
│   │   │   ├── user.py         # 用户接口
│   │   │   ├── paper.py        # 论文接口
│   │   │   ├── generate.py     # 生成接口
│   │   │   └── __init__.py
│   │   ├── models.py           # 数据库模型
│   │   ├── services/           # 业务逻辑
│   │   │   ├── pdf_parser.py   # PDF解析
│   │   │   └── ai_generator.py # AI生成
│   │   └── utils.py            # 工具函数
│   ├── config.py               # 配置文件
│   ├── requirements.txt        # Python依赖
│   ├── start.bat               # Windows启动脚本
│   ├── .env.example            # 环境变量示例
│   └── run.py                  # 应用入口
│
└── README.md                    # 本文档
```

## API接口说明

### 认证接口

- `POST /api/user/register` - 用户注册
- `POST /api/user/login` - 用户登录
- `GET /api/user/info` - 获取用户信息

### 论文接口

- `POST /api/paper/upload` - 上传论文
- `GET /api/paper/list` - 获取论文列表
- `GET /api/paper/{id}` - 获取论文详情
- `DELETE /api/paper/{id}` - 删除论文
- `POST /api/paper/{id}/parse` - 解析论文

### 生成接口

- `POST /api/generate/mindmap` - 生成思维导图
- `POST /api/generate/timeline` - 生成时间线
- `POST /api/generate/graph` - 生成概念图谱
- `POST /api/generate/summary` - 生成阅读报告
- `POST /api/generate/review` - 生成评审报告
- `GET /api/generate/history/{paperId}` - 获取生成历史

## 常见问题

### 启动相关

**Q: 后端启动失败，提示"Python not found"？**
A: 请确保已安装Python 3.8或更高版本，并添加到系统PATH环境变量中。

**Q: 前端启动失败，提示"npm not found"？**
A: 请确保已安装Node.js 16或更高版本，并添加到系统PATH环境变量中。

**Q: start.bat 运行后出现编码错误？**
A: 确保命令行使用UTF-8编码，在CMD中执行 `chcp 65001`。

### 功能相关

**Q: 前端无法连接后端，显示网络错误？**
A:
1. 确保后端服务正在运行（访问 http://localhost:5000 测试）
2. 检查前端配置 `frontend/src/utils/request.js` 中的baseURL
3. 确保防火墙没有阻止5000端口

**Q: PDF上传后解析失败？**
A:
1. 确保PDF是文本格式，扫描版PDF无法解析
2. 检查PDF文件是否损坏
3. 尝试重新解析（点击"重新解析"按钮）

**Q: AI生成内容失败或超时？**
A:
1. 检查智谱AI API Key是否正确设置
2. 检查网络连接是否正常
3. 检查API额度是否充足
4. 论文内容过长可能导致超时，建议分段生成

**Q: 登录后提示"未登录"或频繁退出？**
A:
1. 清除浏览器缓存和Cookie
2. 检查后端JWT配置是否正确
3. 确保后端服务正常运行

### 性能相关

**Q: PDF解析速度慢？**
A: 这是正常现象，取决于PDF文件大小和复杂度，一般需要5-30秒。

**Q: AI生成速度慢？**
A:
- 阅读报告：~20秒
- 评审报告：~20秒
- 思维导图：~15秒
- 时间线：~15秒
- 概念图谱：~20秒

## 技术栈

### 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.3+ | 渐进式JavaScript框架 |
| Vite | 5.0+ | 前端构建工具 |
| Element Plus | 2.4+ | UI组件库 |
| Vue Router | 4.2+ | 路由管理 |
| Pinia | 2.1+ | 状态管理 |
| Axios | 1.6+ | HTTP客户端 |
| ECharts | 5.4+ | 数据可视化 |

### 后端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Flask | 3.0+ | Web框架 |
| SQLAlchemy | 2.0+ | ORM框架 |
| Flask-JWT-Extended | 4.6+ | JWT认证 |
| PyPDF2 | 3.0+ | PDF解析 |
| pdfplumber | 0.10+ | PDF文本提取 |
| zhipuai | 最新 | 智谱AI SDK |

## 开发计划

- [ ] 支持批量上传论文
- [ ] 添加论文标注功能
- [ ] 支持导出Markdown格式
- [ ] 添加论文对比功能
- [ ] 支持多用户协作

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交Issue或Pull Request。
