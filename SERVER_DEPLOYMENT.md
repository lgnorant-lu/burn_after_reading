# 服务器生产环境部署指南 - 阅后即焚

**项目主页:** [`README.md`](./README.md)  
**项目仓库地址:** [https://github.com/lgnorant-lu/burn_after_reading](https://github.com/lgnorant-lu/burn_after_reading)

---

## 1. 概述

本指南详细介绍了如何在生产服务器（如 Ubuntu 22.04）上从零开始部署 "阅后即焚" 应用。我们将使用 Docker 和 Docker Compose 进行容器化部署，并配置 Nginx 作为反向代理和使用 Let's Encrypt 获取免费的 SSL 证书。

**自动化脚本:** 为简化安装过程，我们提供了一个自动化部署脚本。熟悉手动步骤后，您可直接使用该脚本快速部署。
- **脚本位置**: `scripts/deploy_server.sh`
- **使用方法**: `bash scripts/deploy_server.sh your_domain.com`

---

## 2. 服务器初始设置

### 2.1 先决条件
- 一台拥有root权限的服务器 (推荐 Ubuntu 22.04)。
- 一个已注册的域名，并已将其 DNS A 记录指向您服务器的 IP 地址。

### 2.2 安装基础软件
连接到您的服务器并执行以下命令来安装 Docker, Docker Compose, Git 和 Nginx。

```bash
# 更新软件包列表
sudo apt update && sudo apt upgrade -y

# 安装 Docker
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker

# 安装 Docker Compose
sudo apt install -y docker-compose

# 安装 Nginx 和 Git
sudo apt install -y nginx git

# 安装 Certbot (用于SSL证书)
sudo apt install -y certbot python3-certbot-nginx
```

---

## 3. 手动部署步骤

### 步骤 1: 克隆项目仓库
```bash
# 在您选择的目录下克隆项目
git clone https://github.com/lgnorant-lu/burn_after_reading.git
cd burn_after_reading
```

### 步骤 2: 创建生产环境配置文件
我们将为生产环境创建一个专门的 `.env.prod` 文件，以覆盖 `docker-compose.yml` 中的默认设置。

**重要**: 请勿将此文件命名为 `.env`，因为 `.env` 文件通常用于本地开发，并且可能已被 `.gitignore` 忽略。

```bash
# 创建并编辑 .env.prod 文件
nano .env.prod
```

将以下内容粘贴到文件中，并替换为您自己的值：

```ini
# .env.prod

# [General]
# 生产模式
APP_ENV=production

# [Security]
# 使用 'openssl rand -hex 32' 生成一个强密钥
SECRET_KEY=您生成的超长随机安全密钥

# [Database]
# 推荐使用PostgreSQL。确保数据库已创建且网络可访问。
# 示例: SQLALCHEMY_DATABASE_URL="postgresql://user:password@db_host:5432/burn_db"
SQLALCHEMY_DATABASE_URL="sqlite:///./sql_app.db" # 如果您坚持在生产中使用SQLite，请确保备份

# [CORS]
# 生产环境中，应仅允许您的前端域名访问
CORS_ORIGINS=https://your_domain.com

# [Application]
APP_VERSION=1.0.0-prod
```

### 步骤 3: 配置 Nginx
我们将创建一个 Nginx 配置文件来代理到我们的 Docker 服务。

```bash
# 创建新的Nginx配置文件
sudo nano /etc/nginx/sites-available/burn_after_reading
```

粘贴以下配置，并将 `your_domain.com` 替换为您的域名：

```nginx
server {
    listen 80;
    server_name your_domain.com;

    # 用于 Let's Encrypt 验证
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    location / {
        # 重定向所有HTTP流量到HTTPS
        return 301 https://$host$request_uri;
    }
}
```

**启用该配置:**
```bash
# 创建软链接以启用站点
sudo ln -s /etc/nginx/sites-available/burn_after_reading /etc/nginx/sites-enabled/

# 测试Nginx配置是否有语法错误
sudo nginx -t

# 重启Nginx使配置生效
sudo systemctl reload nginx
```

### 步骤 4: 获取 SSL 证书
使用 Certbot 为您的域名自动获取并配置 SSL 证书。

```bash
# Certbot将自动修改您的Nginx配置以启用HTTPS
sudo certbot --nginx -d your_domain.com
```
按照提示操作。完成后，Certbot 会自动更新您的 Nginx 配置文件，并设置定时任务来自动续订证书。

### 步骤 5: 构建并启动应用
现在我们可以使用 Docker Compose 启动应用了。

```bash
# --env-file 指定使用我们的生产配置文件
# --build 确保构建最新的镜像
# -d 在后台运行
sudo docker-compose --env-file .env.prod up --build -d
```

### 步骤 6: 验证
- 在浏览器中访问 `https://your_domain.com`，您应该能看到应用界面。
- 检查 Docker 服务状态: `sudo docker-compose ps`
- 查看实时日志: `sudo docker-compose logs -f`

---

## 4. 维护

### 更新应用
当有新的代码提交时，您可以这样更新：
```bash
# 进入项目目录
cd burn_after_reading

# 拉取最新代码
git pull origin main # 或者您的主分支

# 重新构建并重启服务
sudo docker-compose --env-file .env.prod up --build -d
```

### 停止服务
```bash
sudo docker-compose down
```

### 数据备份 (重要!)
如果使用 SQLite，数据库文件 (`sql_app.db`) 将在项目根目录下。请定期备份此文件。如果使用 PostgreSQL，请使用 `pg_dump` 等工具进行数据库备份。 