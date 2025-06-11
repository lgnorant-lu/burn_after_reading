#!/bin/bash

# Burn After Reading - 服务器快速部署脚本
# 使用方法: ./deploy_server.sh your-domain.com

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函数定义
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查参数
if [ $# -eq 0 ]; then
    log_error "请提供域名参数"
    echo "使用方法: $0 your-domain.com"
    exit 1
fi

DOMAIN=$1
APP_DIR="/opt/burn-after-reading"

log_info "开始部署 Burn After Reading 到域名: $DOMAIN"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    log_error "请以root用户身份运行此脚本"
    exit 1
fi

# 1. 更新系统
log_info "更新系统..."
apt update && apt upgrade -y

# 2. 安装Docker
log_info "安装Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
else
    log_info "Docker已安装，跳过"
fi

# 3. 安装Docker Compose
log_info "安装Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    log_info "Docker Compose已安装，跳过"
fi

# 4. 安装Nginx
log_info "安装Nginx..."
if ! command -v nginx &> /dev/null; then
    apt install nginx -y
    systemctl start nginx
    systemctl enable nginx
else
    log_info "Nginx已安装，跳过"
fi

# 5. 安装Certbot
log_info "安装Certbot..."
if ! command -v certbot &> /dev/null; then
    apt install certbot python3-certbot-nginx -y
else
    log_info "Certbot已安装，跳过"
fi

# 6. 配置防火墙
log_info "配置防火墙..."
if command -v ufw &> /dev/null; then
    ufw --force enable
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw reload
else
    log_warn "UFW未安装，请手动配置防火墙"
fi

# 7. 创建应用目录
log_info "创建应用目录..."
mkdir -p $APP_DIR
mkdir -p $APP_DIR/data
mkdir -p $APP_DIR/scripts
mkdir -p /opt/backups/burn-after-reading

# 8. 创建生产环境Docker Compose文件
log_info "创建生产环境配置..."
cat > $APP_DIR/docker-compose.prod.yml << EOF
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: burn-backend-prod
    restart: unless-stopped
    environment:
      - DATABASE_URL=sqlite:///app/data/burn_after_reading.db
      - CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
      - HOST=0.0.0.0
      - PORT=8001
    volumes:
      - ./data:/app/data
      - /etc/localtime:/etc/localtime:ro
    expose:
      - "8001"
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
        - VITE_API_BASE_URL=https://$DOMAIN/api
    container_name: burn-frontend-prod
    restart: unless-stopped
    environment:
      - VITE_API_BASE_URL=https://$DOMAIN/api
    expose:
      - "3000"
    networks:
      - burn-network
    depends_on:
      backend:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:3000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 20s

networks:
  burn-network:
    driver: bridge
    name: burn_after_reading_prod_network

volumes:
  burn_data_prod:
    driver: local
EOF

# 9. 创建Nginx配置
log_info "创建Nginx配置..."
cat > /etc/nginx/sites-available/burn-after-reading << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    # 重定向到HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL证书配置 (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers on;
    ssl_dhparam /etc/nginx/dhparam.pem;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # 文件上传大小限制
    client_max_body_size 6M;

    # 前端静态文件
    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # API后端代理
    location /api/ {
        # 重写URL，去掉/api前缀
        rewrite ^/api/(.*) /\$1 break;
        
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 文件上传支持
        proxy_request_buffering off;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 健康检查端点
    location /health {
        proxy_pass http://127.0.0.1:8001/health;
        access_log off;
    }

    # 安全配置：隐藏Nginx版本
    server_tokens off;

    # 日志配置
    access_log /var/log/nginx/burn-after-reading.access.log;
    error_log /var/log/nginx/burn-after-reading.error.log;
}
EOF

# 10. 生成DH参数
log_info "生成DH参数..."
if [ ! -f /etc/nginx/dhparam.pem ]; then
    openssl dhparam -out /etc/nginx/dhparam.pem 2048
else
    log_info "DH参数已存在，跳过"
fi

# 11. 启用站点
log_info "启用Nginx站点..."
ln -sf /etc/nginx/sites-available/burn-after-reading /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# 12. 创建监控脚本
log_info "创建监控脚本..."
cat > $APP_DIR/scripts/monitor.sh << 'EOF'
#!/bin/bash

COMPOSE_FILE="/opt/burn-after-reading/docker-compose.prod.yml"
LOG_FILE="/var/log/burn-after-reading-monitor.log"

echo "$(date): Starting health check..." >> $LOG_FILE

# 检查Docker服务状态
if ! docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
    echo "$(date): Some services are down, restarting..." >> $LOG_FILE
    docker-compose -f $COMPOSE_FILE restart
fi

# 检查磁盘空间
DISK_USAGE=$(df /opt/burn-after-reading | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): WARNING - Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
fi

echo "$(date): Health check completed." >> $LOG_FILE
EOF

chmod +x $APP_DIR/scripts/monitor.sh

# 13. 创建备份脚本
log_info "创建备份脚本..."
cat > $APP_DIR/scripts/backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/opt/backups/burn-after-reading"
APP_DIR="/opt/burn-after-reading"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
if [ -f $APP_DIR/data/burn_after_reading.db ]; then
    cp $APP_DIR/data/burn_after_reading.db $BACKUP_DIR/burn_after_reading_$DATE.db
fi

# 备份配置文件
tar -czf $BACKUP_DIR/config_$DATE.tar.gz \
    $APP_DIR/docker-compose.prod.yml \
    /etc/nginx/sites-available/burn-after-reading 2>/dev/null || true

# 清理老备份 (保留7天)
find $BACKUP_DIR -name "*.db" -mtime +7 -delete 2>/dev/null || true
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete 2>/dev/null || true

echo "$(date): Backup completed - $DATE" >> /var/log/burn-after-reading-backup.log
EOF

chmod +x $APP_DIR/scripts/backup.sh

# 14. 设置Crontab
log_info "设置定时任务..."
(crontab -l 2>/dev/null; echo "*/5 * * * * $APP_DIR/scripts/monitor.sh") | crontab -
(crontab -l 2>/dev/null; echo "0 2 * * * $APP_DIR/scripts/backup.sh") | crontab -

# 15. 日志轮转配置
log_info "配置日志轮转..."
cat > /etc/logrotate.d/burn-after-reading << EOF
/var/log/nginx/burn-after-reading.*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        if [ -f /var/run/nginx.pid ]; then
            kill -USR1 \`cat /var/run/nginx.pid\`
        fi
    endscript
}

/var/log/burn-after-reading-*.log {
    weekly
    missingok
    rotate 12
    compress
    delaycompress
    notifempty
    create 644 root root
}
EOF

log_info "基础环境配置完成！"
log_warn "接下来需要手动完成以下步骤："
echo ""
echo "1. 将您的代码部署到 $APP_DIR"
echo "   - git clone <您的仓库> $APP_DIR"
echo "   - 或者上传代码文件到该目录"
echo ""
echo "2. 获取SSL证书："
echo "   certbot --nginx -d $DOMAIN -d www.$DOMAIN"
echo ""
echo "3. 构建并启动应用："
echo "   cd $APP_DIR"
echo "   docker-compose -f docker-compose.prod.yml up --build -d"
echo ""
echo "4. 检查服务状态："
echo "   docker-compose -f docker-compose.prod.yml ps"
echo "   docker-compose -f docker-compose.prod.yml logs -f"
echo ""
log_info "部署脚本执行完成！" 