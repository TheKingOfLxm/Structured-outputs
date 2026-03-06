# 免费云平台部署指南

## 部署方案

使用以下免费云平台组合：
- **后端**: Railway（免费 512MB RAM，$5 免费额度/月）
- **前端**: Vercel（无限静态托管，自动 HTTPS）

---

## 第一步：部署后端（Railway）

### 1. 注册 Railway
访问：https://railway.app/

### 2. 创建新项目
1. 点击 **New Project** → **Deploy from GitHub repo**
2. 选择你的 GitHub 仓库
3. 如果还没上传，先点击 **Deploy from CLI** 或先推送到 GitHub

### 3. 配置环境变量
在 Railway 项目设置中添加以下环境变量：

| 变量名 | 值 |
|--------|-----|
| `FLASK_CONFIG` | `production` |
| `SECRET_KEY` | 随机生成（见下方） |
| `JWT_SECRET_KEY` | 随机生成（见下方） |
| `ZHIPUAI_API_KEY` | 你的智谱AI密钥 |

**生成随机密钥**（在 Python 中执行）：
```python
import secrets
print(secrets.token_hex(32))
```

### 4. 获取后端 URL
部署完成后，Railway 会提供一个 URL，例如：
```
https://your-backend.railway.app
```
记下这个地址，下一步会用到。

---

## 第二步：部署前端（Vercel）

### 1. 注册 Vercel
访问：https://vercel.com/

### 2. 导入项目
1. 点击 **Add New** → **Project**
2. 从 GitHub 导入你的仓库
3. Vercel 会自动识别为 Vue/Vite 项目

### 3. 配置环境变量
在 Vercel 项目设置中添加：
| 变量名 | 值 |
|--------|-----|
| `VITE_API_BASE_URL` | 你的后端 Railway URL |

### 4. 更新 API 代理
在 Vercel 设置中，找到 **Rewrites** 或编辑 `vercel.json`，将 `your-backend-url.railway.app` 替换为你的实际后端地址。

### 5. 部署
点击 **Deploy**，等待几分钟即可完成。

---

## 第三步：验证部署

### 1. 检查后端
访问：`https://your-backend.railway.app/api/health`
应该返回：`{"status": "healthy", "database": "connected"}`

### 2. 检查前端
访问 Vercel 提供的域名，例如：
`https://your-app.vercel.app`

---

## 替代方案

### 方案 A: Render（后端替代 Railway）

1. 访问：https://render.com/
2. 创建 **Web Service**
3. 连接 GitHub 仓库
4. 配置：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 run:app`
5. 添加环境变量（同 Railway）

### 方案 B: Fly.io（后端替代 Railway）

1. 安装 Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. 登录: `flyctl auth signup`
3. 部署:
```bash
cd backend
flyctl launch
flyctl deploy
```

---

## 免费额度对比

| 平台 | 免费额度 | 限制 |
|------|----------|------|
| **Vercel** | 无限带宽 | 100GB 构建输出/月 |
| **Railway** | $5/月 | 512MB RAM，休眠后冷启动 |
| **Render** | 750小时/月 | 15分钟无请求休眠 |
| **Fly.io** | 3个轻量应用 | 256MB RAM/应用 |

---

## 常见问题

### 1. 后端休眠问题
免费服务会在无请求时休眠，首次请求会慢一些。可以：
- 使用 **Cron-job.org** 定时 ping 保持唤醒
- 升级到付费计划

### 2. CORS 错误
确保后端 CORS 配置包含 Vercel 域名：
```python
# backend/config.py
CORS_ORIGINS = ['https://your-app.vercel.app']
```

### 3. 文件上传大小限制
Railway 免费版请求体限制，大文件可能失败。建议升级计划。

---

## 更新部署

### 自动部署
推送到 GitHub 主分支后，Vercel 和 Railway 都会自动重新部署。

### 手动触发
- **Railway**: 在控制台点击 "Redeploy"
- **Vercel**: 在控制台点击 "Redeploy"

---

需要其他平台的配置请告诉我！
