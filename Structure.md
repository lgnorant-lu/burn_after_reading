# 项目结构

本文档提供了 "Burn After Reading" 应用的详细文件和目录结构，旨在帮助开发者快速理解项目布局和各模块的功能。

-   `[completed]` - 功能已完成且稳定。
-   `[in-progress]` - 正在开发中。
-   `[planned]` - 已规划但尚未开始。
-   `[needs-refinement]` - 功能已实现但需要重构或优化。

## 根目录

```
.
├── .dockerignore              # [completed] 定义在构建Docker镜像时应忽略的文件和目录。
├── .gitignore                 # [completed] 定义Git应忽略的文件和目录。
├── .vscode/                   # [completed] VSCode编辑器特定配置。
├── Dockerfile                 # [completed] 用于构建后端FastAPI服务的Dockerfile。
├── docker-compose.yml         # [completed] Docker Compose文件，用于编排所有服务。
├── entrypoint.sh              # [completed] 后端容器的入口点脚本，用于处理数据库迁移等启动任务。
├── frontend/                  # [completed] 包含所有前端Vue.js应用代码的目录。
├── pyproject.toml             # [completed] Python项目配置文件，使用uv进行依赖管理。
├── scripts/                   # [completed] 存放辅助脚本，如部署脚本。
├── src/                       # [completed] 存放所有后端FastAPI应用的核心源代码。
├── uv.lock                    # [completed] `uv`的锁定文件，确保依赖版本一致。
├── .env.example               # [completed] 生产环境变量的示例文件。
├── burn_after_reading.db      # [completed] (本地开发用) SQLite数据库文件。
└── README.md                  # [completed] 项目主说明文档。
```

## `src/` - 后端源代码

```
src/
├── __init__.py                # [completed] 将目录标记为Python包。
├── crud.py                    # [completed] 包含与数据库进行CRUD操作的核心函数。
├── database.py                # [completed] 数据库连接和会话管理。
├── main.py                    # [completed] FastAPI应用主入口，定义所有API路由和应用逻辑。
├── models.py                  # [completed] SQLAlchemy数据模型，定义数据库表结构。
├── schemas.py                 # [completed] Pydantic模型，用于API数据验证和序列化。
└── utils.py                   # [completed] 存放通用工具函数，如密码哈希。
```

## `frontend/` - 前端源代码

```
frontend/
├── .gitignore                 # [completed] 前端目录特定的Git忽略配置。
├── Dockerfile                 # [completed] 用于构建前端Vue.js应用并将其打包到Nginx镜像的Dockerfile。
├── index.html                 # [completed] 单页应用的主HTML文件。
├── nginx.conf                 # [completed] 前端容器内Nginx服务的配置文件。
├── package.json               # [completed] 定义前端项目依赖和脚本。
├── postcss.config.js          # [completed] PostCSS配置文件。
├── src/                       # [completed] 存放所有前端Vue组件和逻辑。
├── tailwind.config.js         # [completed] Tailwind CSS配置文件。
├── tsconfig.json              # [completed] TypeScript配置文件。
└── vite.config.ts             # [completed] Vite构建工具的配置文件。
```

## `scripts/` - 辅助脚本

```
scripts/
└── deploy_server.sh           # [completed] 一键式服务器部署脚本，适配Debian 12和宝塔面板。
```

## 核心项目文档

除了代码文件，项目根目录还包含一系列重要的Markdown文档，用于项目管理和知识沉淀。

-   `Context.md`: [completed] 项目即时记忆与上下文快照。
-   `Plan.md`: [in-progress] 宏观计划文档。
-   `Thread.md`: [in-progress] 任务进程文档。
-   `Design.md`: [in-progress] 系统设计文档。
-   `Issues.md`: [in-progress] 问题追踪文档。
-   `Log.md`: [planned] 变更日志索引。
-   `Diagrams.md`: [planned] 绘图日志与索引。
-   `Decisions.md`: [planned] 重要决策日志。
-   `DEPLOYMENT.md`: [completed] **权威的、详细的生产环境部署指南。** 