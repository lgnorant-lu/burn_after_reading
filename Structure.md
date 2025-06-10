# 项目结构文档

本文档概述了"Burn After Reading"项目的文件和目录结构。

## 文件结构树

```
/
|-- .gitignore               # [已完成] Git忽略文件配置
|-- .dockerignore            # [已完成] Docker构建排除文件
|-- Dockerfile               # [已完成] 容器构建配置
|-- README.md                # [已完成] 项目概述和功能说明
|-- Plan.md                  # [已完成] 高级开发计划和项目阶段
|-- Structure.md             # [已完成] 项目结构文档(本文件)
|-- Context.md               # [已完成] 项目即时上下文和记忆快照
|-- pyproject.toml           # [已完成] 项目元数据和依赖管理(v0.2.0)
|-- uv.lock                  # [已完成] uv依赖锁定文件
|-- final_review_gate.py     # [已完成] 交互式审查会话脚本
|-- migrate_to_v2.py         # [已完成] 数据库迁移脚本(v1→v2)
|-- test_phase2_api.py       # [已完成] 第二阶段API综合测试套件
|-- burn_after_reading.db    # [运行时] SQLite数据库(v2架构)
|-- .tasks/                  # [已完成] 任务管理目录
|
`-- src/                     # 源代码包
    |-- __init__.py          # [已完成] Python包标识文件
    |-- main.py              # [已完成] FastAPI应用程序(7个API端点, v0.2.0)
    |-- database.py          # [已完成] SQLAlchemy数据库配置
    |-- models.py            # [已完成] 数据库模型(包含第二阶段扩展)
    |-- schemas.py           # [已完成] Pydantic V2数据验证模型
    |-- crud.py              # [已完成] 增强的CRUD操作(安全功能)
    `-- utils.py             # [已完成] 工具函数(密码哈希、过期处理)
```

## 核心组件说明

### 顶级文件
- **`README.md`**: 项目主要入口文档，功能概述
- **`Plan.md`**: 分阶段开发路线图  
- **`Context.md`**: 项目当前状态快照
- **`.tasks/`**: 任务管理markdown文件目录
- **`pyproject.toml`**: uv项目配置和依赖定义

### 源代码目录 (`src/`)
- **`main.py`**: FastAPI应用程序 v0.2.0
  - 7个API端点：创建、上传、访问、下载、信息查询、健康检查、清理
- **`models.py`**: SQLAlchemy ORM模型
  - 支持密码保护、多种过期类型、文件存储
- **`schemas.py`**: Pydantic V2数据验证
- **`crud.py`**: 数据库操作层
  - 密码验证、过期检查、文件处理
- **`utils.py`**: 核心工具函数
  - bcrypt密码哈希、过期时间计算、文件格式化

## 第二阶段功能扩展

- **安全特性**: bcrypt密码哈希、输入验证、文件大小限制
- **文件支持**: 二进制文件上传下载，5MB限制
- **过期控制**: 4种过期类型(阅后即焚、1小时、24小时、7天)
- **数据库迁移**: `migrate_to_v2.py`自动化v1→v2架构升级
- **全面测试**: `test_phase2_api.py`验证所有功能
- **容器就绪**: Docker生产环境部署配置

## 即将开始 - 第三阶段

**前端开发准备就绪**:
- 后端API v0.2.0已完成
- 技术栈确定: Vue.js + Vite + TailwindCSS
- 任务文件: `.tasks/2025-06-10_3_frontend-development.md` 