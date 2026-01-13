# 学术阅读助手 - 后端

面向深度学术阅读的结构化内容生成系统后端服务

## 技术栈

- Flask 3.0
- SQLAlchemy (ORM)
- JWT (用户认证)
- PyPDF2 / pdfplumber (PDF解析)
- 智谱AI API (内容生成)
- SQLite (数据库)

## 项目结构

```
backend/
├── app/
│   ├── __init__.py        # 应用初始化
│   ├── models.py          # 数据库模型
│   ├── api/               # API接口
│   │   ├── user.py        # 用户相关API
│   │   ├── paper.py       # 论文相关API
│   │   └── generate.py    # 生成相关API
│   ├── services/          # 业务逻辑
│   │   ├── pdf_parser.py  # PDF解析服务
│   │   └── ai_generator.py # AI生成服务
│   └── utils/             # 工具函数
├── config.py              # 配置文件
├── run.py                 # 应用入口
├── requirements.txt       # 依赖包
└── .env.example           # 环境变量示例
```

## 安装步骤

### 1. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置必要的配置：

```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
ZHIPUAI_API_KEY=your-zhipuai-api-key-here
```

### 4. 初始化数据库

数据库会在首次运行时自动创建。

### 5. 运行应用

```bash
python run.py
```

服务将运行在 `http://localhost:5000`

## API接口文档

### 用户相关 `/api/user`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/login` | 用户登录 |
| POST | `/register` | 用户注册 |
| GET | `/info` | 获取用户信息 |
| PUT | `/info` | 更新用户信息 |
| PUT | `/password` | 修改密码 |

### 论文相关 `/api/paper`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/upload` | 上传论文 |
| GET | `/list` | 获取论文列表 |
| GET | `/<id>` | 获取论文详情 |
| DELETE | `/<id>` | 删除论文 |
| POST | `/<id>/parse` | 重新解析论文 |
| GET | `/<id>/download` | 下载论文 |

### 生成相关 `/api/generate`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/mindmap` | 生成思维导图 |
| POST | `/timeline` | 生成时间线 |
| POST | `/graph` | 生成概念图谱 |
| POST | `/summary` | 生成核心观点 |
| GET | `/history/<paper_id>` | 获取生成历史 |
| POST | `/save` | 保存生成结果 |
| GET | `/record/<id>` | 获取生成记录 |
| DELETE | `/record/<id>` | 删除生成记录 |

## 数据库模型

### User (用户)
- id: 用户ID
- username: 用户名
- email: 邮箱
- password_hash: 密码哈希
- avatar: 头像
- created_at: 创建时间

### Paper (论文)
- id: 论文ID
- user_id: 用户ID
- filename: 文件名
- filepath: 文件路径
- title: 标题
- authors: 作者
- abstract: 摘要
- keywords: 关键词
- sections: 章节
- status: 状态
- upload_time: 上传时间

### GenerateRecord (生成记录)
- id: 记录ID
- user_id: 用户ID
- paper_id: 论文ID
- type: 类型 (mindmap/timeline/graph/summary)
- content: 内容
- status: 状态
- create_time: 创建时间

## 智谱AI配置

1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册账号并获取API Key
3. 在 `.env` 文件中设置 `ZHIPUAI_API_KEY`

注意: 如果不设置API Key，系统会返回模拟数据用于测试。

## 开发说明

- 上传的PDF文件保存在 `uploads/` 目录
- 数据库文件保存在 `instance/app.db`
- 默认端口为5000
- 支持CORS跨域请求

## 常见问题

1. **ModuleNotFoundError**: 确保虚拟环境已激活并安装了依赖
2. **API调用失败**: 检查智谱AI API Key是否正确设置
3. **PDF解析失败**: 确保上传的PDF文件格式正确
