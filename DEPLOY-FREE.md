# 免费云平台部署指南

## 部署方案

使用以下免费云平台组合：
- **后端**: Railway（免费 512MB RAM，$5 免费额度/月）
- **前端**: Vercel（无限静态托管，自动 HTTPS）

---

## 第一步：部署后端（Railway）

### 1. 注册 Railway
访问：https://railway.app/ 并登录

### 2. 创建新项目
1. 点击 **New Project**
2. 选择 **Deploy from GitHub repo**
3. 授权并选择你的 GitHub 仓库

### 3. 配置 Root Directory（重要！）
在部署前，必须设置构建目录：

1. 在项目页面点击你的服务名称
2. 点击 **Settings** 标签
3. 找到 **Root Directory** 设置
4. 输入 `backend`
5. 点击 **Save**

![Railway Root Directory 设置](https://railway.app/docs/assets/root-directory.png)

### 4. 配置环境变量
在 **Variables** 标签页添加以下环境变量：

| 变量名 | 值 |
|--------|-----|
| `FLASK_CONFIG` | `production` |
| `SECRET_KEY` | 随机生成的32位密钥 |
| `JWT_SECRET_KEY` | 随机生成的32位密钥 |
| `ZHIPUAI_API_KEY` | 你的智谱AI密钥 |

**生成随机密钥**（在 Python 中执行）：
```python
import secrets
print(secrets.token_hex(32))
```

获取智谱AI密钥：https://open.bigmodel.cn/

### 5. 触发部署
配置完成后，点击 **Deployments** 标签，点击 **Redeploy** 按钮。

### 6. 获取后端 URL
部署成功后，点击 **View Logs** 上方的域名，例如：
```
https://xxx.up.railway.app
```

**验证后端**：访问 `https://xxx.up.railway.app/api/health`
应该返回：`{"status": "healthy", "database": "connected"}`

---

## 第二步：部署前端（Vercel）

### 1. 注册 Vercel
访问：https://vercel.com/ 并登录

### 2. 导入项目
1. 点击 **Add New** → **Project**
2. 从 GitHub 导入你的仓库
3. Vercel 会自动识别为 Vue/Vite 项目

### 3. 配置环境变量
在项目设置页面：
1. 找到 **Environment Variables** 部分
2. 添加以下变量：

| 变量名 | 值 |
|--------|-----|
| `VITE_API_BASE_URL` | 你的后端 Railway URL + `/api` |

例如：`https://xxx.up.railway.app/api`

### 4. 配置重写规则（可选）
如果需要 API 代理，在项目设置中：
1. 找到 **Rewrites** 部分
2. 添加规则：
   - Source: `/api/:path*`
   - Destination: `你的后端URL/api/:path*`

### 5. 部署
点击 **Deploy** 按钮，等待 1-2 分钟。

### 6. 获取前端 URL
部署成功后，Vercel 会提供一个域名，例如：
```
https://your-app.vercel.app
```

---

## 第三步：验证部署

### 1. 检查后端健康状态
访问：`https://xxx.up.railway.app/api/health`
预期返回：`{"status": "healthy", "database": "connected"}`

### 2. 检查前端
访问：`https://your-app.vercel.app`
应该能看到登录页面

### 3. 测试登录
1. 注册一个新账号
2. 登录成功即可正常使用

---

## 替代方案：使用 Render 部署后端

如果 Railway 有问题，可以使用 Render：

### 1. 注册 Render
访问：https://render.com/

### 2. 创建 Web Service
1. 点击 **New** → **Web Service**
2. 连接 GitHub 仓库
3. 配置：
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 run:app`
4. 选择 **Free** 计划
5. 点击 **Create Web Service**

### 3. 配置环境变量
在 Render 控制台添加：
| 变量名 | 值 |
|--------|-----|
| `FLASK_CONFIG` | `production` |
| `SECRET_KEY` | 随机生成 |
| `JWT_SECRET_KEY` | 随机生成 |
| `ZHIPUAI_API_KEY` | 你的智谱AI密钥 |

---

## 免费额度对比

| 平台 | 免费额度 | 限制 |
|------|----------|------|
| **Vercel** | 无限带宽 | 100GB 构建输出/月 |
| **Railway** | $5/月 | 512MB RAM，休眠后冷启动 |
| **Render** | 750小时/月 | 15分钟无请求休眠 |

---

## 常见问题

### 1. 后端无法启动
**检查**：
- Root Directory 是否设置为 `backend`
- 环境变量是否正确配置
- 查看部署日志

### 2. 前端无法连接后端
**检查**：
- `VITE_API_BASE_URL` 是否正确
- 后端健康检查是否正常
- CORS 配置是否包含前端域名

### 3. 后端休眠问题
免费服务会在无请求时休眠，首次请求会慢一些。

**解决方案**：
- 使用 https://cron-job.org 定时 ping 保持唤醒
- 升级到付费计划

### 4. CORS 错误
确保后端配置允许前端域名。在 `backend/config.py` 中：
```python
CORS_ORIGINS = ['https://your-app.vercel.app', 'http://localhost:5173']
```

---

## 更新部署

### 自动部署
推送到 GitHub 主分支后，平台会自动重新部署。

### 手动触发
- **Railway**: 点击 Deployments → Redeploy
- **Vercel**: 点击 Deployments → Redeploy

---

## 项目文件说明

```
项目根目录/
├── backend/              # 后端代码
│   ├── Dockerfile        # Docker 配置（可选）
│   ├── Procfile         # 进程配置（Railway 自动检测）
│   └── requirements.txt  # Python 依赖
├── frontend/            # 前端代码
│   ├── package.json     # Node 依赖
│   └── .env.production  # 生产环境变量
└── DEPLOY-FREE.md       # 本文档
```

---

需要帮助？请查看：
- [Railway 文档](https://docs.railway.app/)
- [Vercel 文档](https://vercel.com/docs)
