# Docker 部署指南 - 阅后即焚

**项目主页:** [`README.md`](./README.md)  
**项目仓库地址:** [https://github.com/lgnorant-lu/burn_after_reading](https://github.com/lgnorant-lu/burn_after_reading)

---

## 1. 简介

本指南为 "阅后即焚" 应用提供了详细的Docker部署说明。Docker是生产环境推荐的部署方式，因为它将应用程序及其所有依赖项封装到一个标准化的软件开发单元中。

## 2. 先决条件

在开始之前，请确保您的系统中已安装以下软件：
- [Docker](https://docs.docker.com/get-docker/) (版本 20.10.0 或更高)
- [Docker Compose](https://docs.docker.com/compose/install/) (版本 1.29.0 或更高，通常随Docker Desktop提供)
- [Git](https://git-scm.com/downloads/) (用于克隆项目)

## 3. 架构概览

部署架构包含三个主要组件：
1.  **Nginx (反向代理)**: 作为前端静态文件和后端API的入口点，处理所有传入的HTTP/HTTPS请求，并负责提供SSL终止。
2.  **FastAPI (后端服务)**: 运行在Uvicorn服务器上的Python应用，提供核心的API逻辑。
3.  **Vue.js (前端应用)**: 一个编译后的单页应用(SPA)，由Nginx作为静态文件提供服务。

## 4. 部署步骤

### 步骤 1: 获取源代码
```bash
git clone https://github.com/lgnorant-lu/burn_after_reading.git
cd burn_after_reading
```

### 步骤 2: 配置环境变量

在项目根目录创建一个 `.env` 文件。这个文件将用于存储敏感信息和环境特定的配置。

```env
# .env

# 安全密钥，用于内部加密操作。请使用一个长且随机的字符串。
# 可以使用命令 `openssl rand -hex 32` 生成
SECRET_KEY=在此处输入您生成的安全密钥

# 数据库URL
# 默认使用SQLite。对于生产环境，推荐使用PostgreSQL。
# SQLALCHEMY_DATABASE_URL="sqlite:///./sql_app.db"
SQLALCHEMY_DATABASE_URL="postgresql://user:password@host:port/database"

# CORS (跨域资源共享) 设置
# 如果您的前端和后端部署在不同的域名下，请配置允许的前端源。
# 使用逗号分隔多个源，例如 "http://localhost:5173,https://your.frontend.domain"
CORS_ORIGINS="http://localhost:5173,http://localhost:80"

# 应用版本
APP_VERSION="1.0.0"
```

### 步骤 3: 构建并运行Docker容器

我们使用 `docker-compose.yml` 文件来编排服务的构建和运行。

```bash
# 构建并以分离模式（在后台运行）启动所有服务
docker-compose up --build -d
```

此命令将完成以下操作：
- 拉取或构建 `nginx`, `backend`, `frontend` 服务的镜像。
- 创建并启动容器。
- 建立服务间的网络连接。

### 步骤 4: 验证部署

- **后端健康检查**:
  ```bash
  curl http://localhost/api/health
  # 预期输出: {"status":"healthy","version":"1.0.0"}
  ```
- **访问前端**:
  在您的浏览器中打开 `http://localhost`。您应该能看到阅后即焚应用的主页。

## 5. Docker Compose 服务详解

文件: `docker-compose.yml`

- **`backend` 服务**:
  - **构建上下文**: 项目根目录。
  - **Dockerfile**: `backend.Dockerfile`
  - **环境变量**: 从 `.env` 文件加载。
  - **端口**: 不直接暴露给主机，通过Nginx进行通信。

- **`frontend` 服务**:
  - **构建上下文**: `frontend` 目录。
  - **Dockerfile**: `frontend.Dockerfile`
  - **阶段**: 多阶段构建，首先安装依赖并构建静态文件，然后将产物复制到一个轻量级的 `nginx` 镜像中。

- **`nginx` 服务**:
  - **镜像**: 使用官方 `nginx:stable-alpine` 镜像。
  - **端口映射**: 将主机的80端口映射到容器的80端口。
  - **卷挂载**:
    - `nginx.conf`: Nginx的主配置文件。
    - `sites-enabled/`: 虚拟主机配置文件。
    - `logs/`: 用于存储Nginx的访问和错误日志。
  - **依赖**: 依赖 `backend` 和 `frontend` 服务，确保它们先于Nginx启动。

## 6. 日志与监控

- **查看实时日志**:
  ```bash
  # 查看所有服务的日志
  docker-compose logs -f

  # 查看特定服务的日志 (例如 backend)
  docker-compose logs -f backend
  ```
- **日志文件**: Nginx的日志被挂载到项目根目录下的 `logs/` 文件夹中，方便持久化存储和分析。

## 7. 停止与清理

- **停止并移除容器**:
  ```bash
  docker-compose down
  ```
- **移除镜像 (可选)**:
  如果想彻底清理，可以移除 `docker-compose up` 构建的镜像。
  ```bash
  docker-compose down --rmi all
  ```

## 8. 故障排查

- **容器无法启动**:
  - 检查 `docker-compose logs <service_name>` 查看具体错误。
  - 确认 `.env` 文件配置正确，特别是 `SECRET_KEY` 和 `SQLALCHEMY_DATABASE_URL`。
- **Nginx `502 Bad Gateway` 错误**:
  - 这通常意味着Nginx无法连接到后端服务。
  - 检查后端服务的日志 (`docker-compose logs backend`)，确认它是否已成功启动且没有错误。
- **前端资源加载失败 (404)**:
  - 确认 `nginx.conf` 中的路径配置是否正确。
  - 检查前端容器的构建日志，确保静态文件已成功生成并复制到正确位置。

## 9. 功能测试

### 自动化测试脚本

项目包含了完整的部署测试脚本，验证所有核心功能：

**Windows PowerShell:**
```powershell
.\test_docker_deployment.ps1
```

### 手动功能测试

#### 1. 文本消息测试
```bash
# 创建阅后即焚消息
curl -X POST "http://localhost:8001/create" \
  -H "Content-Type: application/json" \
  -d '{"expiration_type":"read_once","content":"测试消息"}'

# 返回示例: {"id":"abc123","expires_at":null}

# 访问消息 (注意：访问后会立即删除)
curl "http://localhost:8001/note/abc123"
```

#### 2. 文件上传测试
```bash
# 上传文件
curl -X POST "http://localhost:8001/upload" \
  -F "file=@test.txt" \
  -F "expiration_type=read_once"

# 下载文件 (注意：下载后会立即删除)
curl "http://localhost:8001/note/file_id" --output downloaded_file.txt
```

## 10. 配置说明

### 环境变量

#### 后端环境变量
```bash
# 数据库配置
DATABASE_URL=sqlite:///app/data/burn_after_reading.db

# 服务器配置
HOST=0.0.0.0
PORT=8001

# CORS配置
CORS_ORIGINS=http://localhost:3001,http://127.0.0.1:3001

# 文件上传配置 (在应用代码中硬编码)
# 最大文件大小: 5MB
# 上传目录: 存储在数据库中，不使用文件系统
```

#### 前端环境变量
```bash
# API配置 (Docker构建时设置)
VITE_API_BASE_URL=http://localhost:8001

# 注意：前端使用Vite构建，开发环境端口为5173，生产环境通过Docker暴露为3001
```

### 实际的Docker Compose配置

项目中的`docker-compose.yml`配置：

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: burn-backend
    restart: unless-stopped
    environment:
      - DATABASE_URL=sqlite:///app/data/burn_after_reading.db
      - CORS_ORIGINS=http://localhost:3001,http://127.0.0.1:3001
      - HOST=0.0.0.0
      - PORT=8001
    volumes:
      - ./data:/app/data
    ports:
      - "8001:8001"
    networks:
      - burn-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - VITE_API_BASE_URL=http://localhost:8001
    container_name: burn-frontend
    restart: unless-stopped
    environment:
      - VITE_API_BASE_URL=http://localhost:8001
    ports:
      - "3001:3000"  # 容器内Nginx运行在3000端口，映射到主机3001端口
    networks:
      - burn-network
    depends_on:
      backend:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 20s

networks:
  burn-network:
    driver: bridge
    name: burn_after_reading_network

volumes:
  burn_data:
    driver: local
```

## 11. 安全考虑

### 生产环境部署建议

1. **HTTPS配置**: 在生产环境中务必使用HTTPS
2. **环境变量**: 敏感配置通过环境变量管理，不要硬编码
3. **文件大小限制**: 当前硬编码为5MB，在上传端点中验证
4. **访问日志**: 启用访问日志监控
5. **备份策略**: 虽然是"阅后即焚"，但建议定期备份配置

### 数据安全

- 所有note在访问后会立即删除
- 上传的文件存储在数据库中（不使用文件系统）
- 数据库连接使用参数化查询防止SQL注入
- 文件上传包含类型和大小验证

## 12. 性能优化

### 生产环境优化建议

1. **前端优化**:
   - 启用Nginx gzip压缩 (已在nginx.conf中配置)
   - 配置静态资源缓存
   - 使用CDN加速

2. **后端优化**:
   - 配置适当的worker数量
   - 启用数据库连接池
   - 配置API响应缓存

3. **系统优化**:
   - 配置反向代理(Nginx/Apache)
   - 设置负载均衡
   - 监控系统资源使用

## 13. API文档

详细的API文档可通过以下方式访问：
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

### 主要API端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/create` | POST | 创建文本消息 |
| `/upload` | POST | 上传文件 |
| `/note/{note_id}` | GET | 获取并删除note (兼容旧版本，无密码) |
| `/note/{note_id}/info` | GET | 获取note信息(不删除) |
| `/note/{note_id}` | POST | 访问文本note(带密码验证，访问后删除) |
| `/note/{note_id}/download` | POST | 下载文件note(带密码验证，下载后删除) |
| `/cleanup` | POST | 清理过期note |

## 14. 维护和更新

### 应用更新
```bash
# 拉取最新代码
git pull origin main

# Docker环境更新
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 本地环境更新
# 后端
uv pip install --system .

# 前端
cd frontend
npm install
npm run build
```

### 数据清理
```bash
# 手动清理过期notes
curl -X POST http://localhost:8001/cleanup

# 数据库维护
sqlite3 burn_after_reading.db "VACUUM;"
```

## 15. 支持与贡献

- **问题反馈**: 请在GitHub Issues中提交
- **功能建议**: 欢迎提交Feature Request
- **代码贡献**: 请遵循项目的代码风格和提交规范

---

**注意**: 本应用实现了真正的"阅后即焚"功能，所有note在访问后会立即删除，请用户在使用时注意数据的重要性。 