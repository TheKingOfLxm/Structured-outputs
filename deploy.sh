#!/bin/bash

# 云服务器一键部署脚本
# 使用方法: ./deploy.sh

set -e

echo "========================================"
echo "  学术论文阅读系统 - 云服务器部署"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker
echo -e "${YELLOW}检查 Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker 未安装，正在安装...${NC}"
    curl -fsSL https://get.docker.com | bash
    sudo systemctl start docker
    sudo systemctl enable docker
else
    echo -e "${GREEN}Docker 已安装${NC}"
fi

# 检查 Docker Compose
echo -e "${YELLOW}检查 Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Docker Compose 未安装${NC}"
    exit 1
else
    echo -e "${GREEN}Docker Compose 已安装${NC}"
fi

# 检查环境变量文件
echo -e "${YELLOW}检查环境配置...${NC}"
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}创建环境配置文件...${NC}"
    cp .env.production backend/.env

    # 生成随机密钥
    SECRET_KEY=$(openssl rand -hex 32)
    JWT_SECRET_KEY=$(openssl rand -hex 32)

    # 替换密钥（Linux/Mac）
    if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i "s/请修改为随机生成的密钥/$SECRET_KEY/g" backend/.env
        sed -i "s/请修改为随机生成的JWT密钥/$JWT_SECRET_KEY/g" backend/.env
    fi

    echo -e "${GREEN}环境配置文件已创建${NC}"
    echo -e "${YELLOW}请编辑 backend/.env 文件，配置 ZHIPUAI_API_KEY${NC}"
    echo -e "  nano backend/.env"
    read -p "配置完成后按回车继续..."
fi

# 检查智谱AI密钥
echo -e "${YELLOW}验证智谱AI配置...${NC}"
if grep -q "请替换为你的智谱AI密钥" backend/.env; then
    echo -e "${RED}错误：智谱AI密钥未配置！${NC}"
    echo -e "请编辑 backend/.env 文件，设置 ZHIPUAI_API_KEY"
    exit 1
fi

# 创建必要的目录
echo -e "${YELLOW}创建数据目录...${NC}"
mkdir -p nginx/ssl backend/instance backend/uploads

# 停止旧容器
echo -e "${YELLOW}停止旧容器...${NC}"
docker compose down 2>/dev/null || true

# 构建镜像
echo -e "${YELLOW}构建 Docker 镜像...${NC}"
docker compose build

# 启动服务
echo -e "${YELLOW}启动服务...${NC}"
docker compose up -d

# 等待服务启动
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 10

# 检查服务状态
echo -e "${YELLOW}检查服务状态...${NC}"
docker compose ps

# 显示访问地址
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "访问地址："
echo "  前端: http://localhost"
if docker compose ps nginx | grep -q "Up"; then
    echo "  HTTPS: https://your-domain.com"
fi
echo ""
echo "常用命令："
echo "  查看日志: docker compose logs -f"
echo "  重启服务: docker compose restart"
echo "  停止服务: docker compose stop"
echo ""
