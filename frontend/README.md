# 阅后即焚 - 前端

此目录包含“阅后即焚”应用的前端部分，基于 Vue.js 3 构建。

## 项目设置

请确保您已安装 [Node.js](https://nodejs.org/) (推荐v18或更高版本) 和 [npm](https://www.npmjs.com/)。

1.  进入此目录：
    ```sh
    cd frontend
    ```

2.  安装依赖：
    ```sh
    npm install
    ```

## 开发服务器

启动带热重载功能的开发服务器：

```sh
npm run dev
```

服务通常会在 `http://localhost:5173` 上可用。

## 生产环境构建

构建用于生产环境的应用：

```sh
npm run build
```

适用于生产环境的静态资源文件将会生成在 `dist` 目录中。这些是您需要部署到Web服务器或托管服务上的文件。
