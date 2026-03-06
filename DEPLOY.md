# 云服务器部署指南

## 项目概述
这是一个前后端分离的学术论文阅读辅助系统：
- 前端：Vue 3 + Element Plus
- 后端：Flask + SQLite
- AI服务：智谱AI

---

## 一、服务器环境要求

### 最低配置
- CPU: 2核
- 内存: 4GB
- 磁盘: 40GB
- 系统: Ubuntu 20.04+ / CentOS 7+ / Debian 10+

### 软件要求
- Docker 20.10+
- Docker Compose 2.0+
- 域名（可选，用于HTTPS）

---

## 二、服务器准备

### 1. 安装 Docker 和 Docker Compose

**Ubuntu/Debian:**
```bash
# 安装 Docker
curl -fsSL https://get.docker.com | bash

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 安装 Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

**CentOS:**
```bash
# 安装 Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. 验证安装
```bash
docker --version
docker compose version
```

### 3. 配置防火墙
```bash
# 开放必要端口
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 22/tcp    # SSH
sudo ufw enable
```

---

## 三、项目部署

### 1. 上传项目文件
```bash
# 在本地执行（替换为你的服务器IP）
scp -r 结构化内容生成系统/ user@your-server-ip:/home/user/

# 或使用 Git 克隆
git clone <your-repo-url> /home/user/academic-reading-system
cd /home/user/academic-reading-system
```

### 2. 配置环境变量

**复制并编辑配置文件：**
```bash
cp .env.production backend/.env
```

**编辑配置（关键）：**
```bash
nano backend/.env
```

**必须修改的配置：**
```bash
# 1. 生成随机密钥
SECRET_KEY=随机生成的32位十六进制字符串
JWT_SECRET_KEY=随机生成的32位十六进制字符串

# 2. 配置智谱AI密钥（必填）
ZHIPUAI_API_KEY=你的智谱AI密钥
```

**生成随机密钥（Python）：**
```python
import secrets
print(secrets.token_hex(32))
```

### 3. 配置域名（可选）

编辑 `nginx/nginx.conf`，将 `your-domain.com` 替换为你的域名：
```bash
nano nginx/nginx.conf
```

如果没有域名，可以注释掉 SSL 部分，只使用 HTTP。

### 4. 构建并启动服务

**开发测试（不使用 HTTPS）：**
```bash
# 修改 docker-compose.yml，注释掉 nginx 服务
docker compose up -d backend frontend
```

**生产部署（使用 HTTPS）：**
```bash
# 1. 准备 SSL 证书
mkdir -p nginx/ssl
# 将证书文件放到 nginx/ssl/ 目录
# - cert.pem (证书文件)
# - key.pem (私钥文件)

# 2. 启动所有服务
docker compose up -d
```

### 5. 查看服务状态
```bash
# 查看容器状态
docker compose ps

# 查看后端日志
docker compose logs backend

# 查看前端日志
docker compose logs frontend
```

---

## 四、获取 SSL 证书（Let's Encrypt）

如果使用域名和 HTTPS：

```bash
# 1. 安装 Certbot
sudo apt-get install certbot

# 2. 生成证书
sudo certbot certonly --standalone -d your-domain.com

# 3. 复制证书到项目目录
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem

# 4. 设置权限
sudo chmod 644 nginx/ssl/cert.pem
sudo chmod 600 nginx/ssl/key.pem
```

---

## 五、常用管理命令

### 服务管理
```bash
# 启动服务
docker compose up -d

# 停止服务
docker compose stop

# 重启服务
docker compose restart

# 查看日志
docker compose logs -f

# 更新并重启
docker compose pull
docker compose up -d --build
```

### 数据备份
```bash
# 备份数据库
docker exec academic-backend cp /app/instance/app.db /app/instance/app.db.backup
docker cp academic-backend:/app/instance/app.db.backup ./backup/

# 备份上传文件
docker cp academic-backend:/app/uploads ./backup/
```

---

## 六、访问地址

- HTTP: http://your-server-ip 或 http://your-domain.com
- HTTPS: https://your-domain.com

---

## 七、故障排查

### 后端无法启动
```bash
# 检查日志
docker compose logs backend

# 常见问题：
# 1. 智谱AI密钥未配置或无效
# 2. 数据库文件权限问题
# 3. 端口被占用
```

### 前端无法访问
```bash
# 检查 Nginx 配置
docker compose logs frontend

# 检查构建是否成功
docker exec academic-frontend ls -la /usr/share/nginx/html
```

### API 请求失败
```bash
# 检查后端健康状态
curl http://localhost:5000/api/health

# 检查 Nginx 代理配置
docker compose logs nginx
```

---

## 八、安全建议

1. 修改默认密钥（SECRET_KEY, JWT_SECRET_KEY）
2. 配置 HTTPS（使用 SSL 证书）
3. 定期更新系统和 Docker 镜像
4. 限制数据库文件权限
5. 配置防火墙规则
6. 定期备份数据

---

## 九、性能优化

### 后端优化
- 增加Gunicorn worker数量（根据CPU核心数）
- 使用PostgreSQL替代SQLite（高并发场景）
- 配置Redis缓存

### 前端优化
- 启用CDN加速静态资源
- 配置浏览器缓存策略

---

如有问题，请查看日志文件或联系技术支持。
