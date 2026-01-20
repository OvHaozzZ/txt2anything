# txt2xmind

[![CI/CD Pipeline](https://github.com/OvHaozzZ/txt2xmind/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/OvHaozzZ/txt2xmind/actions/workflows/ci-cd.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

一个强大的工具，可将缩进文本文件转换为 XMind 思维导图。支持命令行界面和 Web 应用程序，并可选择使用 AI 驱动的文本结构化功能。

## 功能特性

- **文本转 XMind**：将缩进文本转换为专业的 XMind 思维导图
- **多种布局**：支持右侧、思维导图、树形图和组织结构图布局
- **Web 界面**：基于 Vue.js 的用户友好型 Web 应用程序
- **AI 集成**：可选的 OpenAI API 集成，用于自动文本结构化
- **无限层级**：支持深度嵌套结构
- **Docker 支持**：使用 Docker 和 docker-compose 轻松部署
- **CI/CD 就绪**：通过 GitHub Actions 实现自动化测试和部署

## 快速开始

### 使用 Docker（推荐）

```bash
# 从 GitHub Container Registry 拉取镜像
docker pull ghcr.io/OvHaozzZ/txt2xmind:latest

# 运行容器
docker run -d -p 8000:8000 ghcr.io/OvHaozzZ/txt2xmind:latest

# 或使用 docker-compose
docker-compose up -d
```

在浏览器中访问 `http://localhost:8000`。

### 本地安装

```bash
# 克隆仓库
git clone https://github.com/OvHaozzZ/txt2xmind.git
cd txt2xmind

# 安装依赖
pip install -r requirements.txt

# 运行 Web 应用
python web_app.py
```

在浏览器中访问 `http://localhost:8000`。

### 命令行使用

```bash
# 基本用法
python generate_xmind.py input.txt

# 使用自定义布局
python generate_xmind.py input.txt --layout map
```

## 输入格式

创建一个具有缩进结构的文本文件（每级 2 个空格或 1 个制表符）：

```
项目计划
  阶段 1：规划
    定义需求
    创建时间表
  阶段 2：开发
    后端开发
    前端开发
  阶段 3：测试
    单元测试
    集成测试
```

## API 文档

### POST /api/generate

从文本生成 XMind 文件。

**请求体：**
```json
{
  "text": "根节点\n  子节点 1\n  子节点 2",
  "layout": "right",
  "api_key": "可选的-openai-密钥",
  "base_url": "可选的-api-基础-url",
  "model": "gpt-3.5-turbo"
}
```

**响应：**
```json
{
  "download_url": "/static/mindmap_20240119120000.xmind",
  "structured_text": "根节点\n  子节点 1\n  子节点 2"
}
```

**布局选项：**
- `right`：右对齐逻辑图（默认）
- `map`：中心辐射思维导图
- `tree`：树形图
- `org`：组织结构图（向下）

## 开发

### 设置开发环境

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/ -v

# 运行覆盖率测试
pytest tests/ --cov=. --cov-report=html

# 代码质量检查
flake8 .
pylint generate_xmind.py web_app.py
```

### 项目结构

```
txt2xmind/
├── generate_xmind.py      # 核心 XMind 生成逻辑
├── web_app.py             # FastAPI Web 应用
├── static/
│   └── index.html         # Vue.js 前端
├── tests/                 # 测试套件
│   ├── test_generate_xmind.py
│   └── test_web_app.py
├── requirements.txt       # 生产依赖
├── requirements-dev.txt   # 开发依赖
├── Dockerfile            # Docker 配置
├── docker-compose.yml    # Docker Compose 配置
└── .github/
    └── workflows/        # GitHub Actions 工作流
```

## CI/CD

本项目使用 GitHub Actions 进行持续集成和部署：

- **CI/CD 流水线**：在推送到 main 分支时运行测试并构建 Docker 镜像
- **手动部署**：允许手动部署到不同环境

### 设置 CI/CD

1. 在 GitHub 上创建仓库
2. 将代码推送到仓库
3. GitHub Actions 将自动运行测试并构建 Docker 镜像
4. Docker 镜像发布到 GitHub Container Registry (ghcr.io)

### 仓库设置

确保在 GitHub 仓库中进行以下设置：

1. 转到 Settings → Actions → General
2. 将"Workflow permissions"设置为"Read and write permissions"
3. 启用"Allow GitHub Actions to create and approve pull requests"

## Docker 部署

### 本地构建

```bash
# 构建镜像
docker build -t txt2xmind:local .

# 运行容器
docker run -d -p 8000:8000 txt2xmind:local
```

### 使用 Docker Compose

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 环境变量

- `PYTHONUNBUFFERED`：设置为 1 以获得无缓冲的 Python 输出
- `OPENAI_API_KEY`：（可选）AI 功能的默认 OpenAI API 密钥

## 贡献

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件。

## 致谢

- 使用 [FastAPI](https://fastapi.tiangolo.com/) 构建
- 前端由 [Vue.js](https://vuejs.org/) 驱动
- 使用 [Tailwind CSS](https://tailwindcss.com/) 样式化
- XMind 格式规范

## 支持

如果您遇到任何问题或有疑问，请在 GitHub 上[提交 issue](https://github.com/OvHaozzZ/txt2xmind/issues)。
