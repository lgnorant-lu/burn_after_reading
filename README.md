# 阅后即焚

🔐 一个安全的"阅后即焚"风格消息服务，用于分享自毁便笺和文件。

**GitHub仓库地址:** [https://github.com/lgnorant-lu/burn_after_reading](https://github.com/lgnorant-lu/burn_after_reading)

---

## 🚀 项目概述

本项目提供了一个生产级的Web服务，允许用户通过一次性使用的链接安全地分享敏感文本或文件。它强调隐私和安全，提供了诸如可选的密码保护和多种过期策略等功能。

## ✨ 核心功能

- **自毁消息**: 文本便笺在被阅读一次后将自动删除。
- **灵活的过期策略**: 可设置便笺在阅读一次、1小时、24小时或7天后过期。
- **安全文件共享**: 上传和分享文件（最大5MB），文件在被访问后同样会被删除。
- **密码保护**: 为您的便笺添加一层额外的安全保障，密码使用bcrypt进行哈希处理。
- **RESTful API**: 定义良好的API，用于创建、检索和管理便笺。
- **现代化前端**: 使用Vue.js和Tailwind CSS构建的响应式、用户友好的界面。
- **容器化**: 已准备好通过Docker进行部署。

## 🚀 部署

本项目推荐使用 Docker 进行生产环境部署。我们提供了一个强大的一键部署脚本，能够自动化处理绝大部分部署任务，特别针对 **Debian 12 + 宝塔面板** 环境进行了深度优化。

关于完整的、包含架构图、步骤详解和"避坑指南"的部署文档，请务必查阅：

**[➡️ 点击查看详细的生产环境部署指南](./DEPLOYMENT.md)**

### 快速开始

1.  克隆仓库到服务器的 `/opt` 目录:
    ```bash
    git clone https://github.com/lgnorant-lu/burn_after_reading.git /opt/burn_after_reading
    cd /opt/burn_after_reading
    ```
2.  赋予部署脚本执行权限:
    ```bash
    chmod +x scripts/deploy_server.sh
    ```
3.  以 root 权限执行脚本 (将 `your-domain.com` 替换为你的域名):
    ```bash
    sudo bash scripts/deploy_server.sh your-domain.com
    ```
脚本将自动处理依赖安装、Docker环境配置、Nginx反向代理、SSL证书申请及应用容器的构建与启动。

## 🛠️ 技术栈

- **后端**: Python, FastAPI, SQLAlchemy
- **前端**: Vue.js, TypeScript, Vite, Tailwind CSS
- **数据库**: SQLite (默认), 兼容 PostgreSQL
- **部署**: Docker, Nginx (推荐)

## 📦 快速开始

### Docker (生产环境)
```bash
# 构建并运行容器
docker build -t burn-after-reading .
docker run -d -p 8000:8000 --name burn-app burn-after-reading
```

### 本地开发

**后端:**
```bash
# 安装依赖 (推荐使用 uv)
uv pip sync
# 运行开发服务器
uv run uvicorn src.main:app --reload --port 8001
```

**前端:**
```bash
cd frontend
npm install
npm run dev
```

## 📚 项目文档

- **[Docker部署指南](./DEPLOYMENT.md)**: 使用Docker部署应用程序的详细说明。
- **[服务器部署指南](./SERVER_DEPLOYMENT.md)**: 用于设置生产服务器的自动化脚本和指南。

---

*本项目遵循 **RIPER-5+ 多维思维协议**进行系统化开发，以确保高质量交付。*
