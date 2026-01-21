# txt2xmind

[![CI/CD Pipeline](https://github.com/OvHaozzZ/txt2xmind/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/OvHaozzZ/txt2xmind/actions/workflows/ci-cd.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

一个强大的工具，可将缩进文本文件转换为多种格式的思维导图和文档。支持命令行界面和 Web 应用程序，并可选择使用 AI 驱动的文本结构化功能。

## 功能特性

- **多格式输出**：支持 XMind、Markdown 等多种输出格式
- **文本转思维导图**：将缩进文本转换为专业的思维导图和结构化文档
- **多种布局**：XMind 支持右侧、思维导图、树形图和组织结构图布局
- **Web 界面**：基于 Vue.js 的用户友好型 Web 应用程序
- **AI 集成**：可选的 OpenAI API 集成，用于自动文本结构化
- **无限层级**：支持深度嵌套结构
- **可扩展架构**：基于格式化器模式，易于添加新的输出格式
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
# 基本用法（默认生成 XMind 格式）
python generate_xmind.py input.txt

# 生成 Markdown 格式
python generate_xmind.py input.txt --format markdown

# 生成 XMind 并指定布局
python generate_xmind.py input.txt --format xmind --layout map

# 列出所有支持的格式
python generate_xmind.py --list-formats

# 查看帮助
python generate_xmind.py --help
```

## 支持的输出格式

| 格式 | 扩展名 | 描述 | 适用场景 |
|------|--------|------|----------|
| **XMind** | `.xmind` | 专业思维导图格式 | 需要可视化思维导图、演示、头脑风暴 |
| **Markdown** | `.md` | 层级列表格式 | 文档编写、GitHub、笔记应用 |

### 如何添加新格式

项目采用可扩展的格式化器架构，添加新格式非常简单：

1. 在 `formatters/` 目录创建新的格式化器类
2. 继承 `BaseFormatter` 抽象基类
3. 实现必需的方法：`format_name`, `file_extension`, `description`, `format()`, `save()`
4. 在 `format_manager.py` 中注册新格式化器

示例代码结构：

```python
from formatters.base import BaseFormatter

class MyFormatter(BaseFormatter):
    @property
    def format_name(self) -> str:
        return "myformat"

    @property
    def file_extension(self) -> str:
        return ".myext"

    # ... 实现其他方法
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

### GET /api/formats

列出所有支持的输出格式。

**响应：**
```json
{
  "formats": [
    {
      "name": "xmind",
      "extension": ".xmind",
      "description": "XMind 思维导图格式"
    },
    {
      "name": "markdown",
      "extension": ".md",
      "description": "Markdown 层级列表格式"
    }
  ]
}
```

### POST /api/generate

从文本生成思维导图文件（支持多种格式）。

**请求体：**
```json
{
  "text": "根节点\n  子节点 1\n  子节点 2",
  "format": "xmind",
  "layout": "right",
  "api_key": "可选的-openai-密钥",
  "base_url": "可选的-api-基础-url",
  "model": "gpt-3.5-turbo"
}
```

**参数说明：**

- `text`：要转换的文本内容（必需）
- `format`：输出格式，可选 `xmind`、`markdown` 等（默认：`xmind`）
- `layout`：XMind 布局类型（仅当 format 为 xmind 时有效，默认：`right`）
- `api_key`：OpenAI API 密钥（可选，用于 AI 文本结构化）
- `base_url`：API 基础 URL（可选）
- `model`：AI 模型名称（默认：`gpt-3.5-turbo`）

**响应：**
```json
{
  "download_url": "/static/mindmap_20240119120000.xmind",
  "structured_text": "根节点\n  子节点 1\n  子节点 2",
  "format": "xmind"
}
```

**XMind 布局选项：**

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
├── generate_xmind.py      # 命令行入口（支持多格式）
├── web_app.py             # FastAPI Web 应用
├── format_manager.py      # 格式管理器
├── core/                  # 核心模块
│   ├── __init__.py
│   └── parser.py          # 文本解析逻辑
├── formatters/            # 格式化器模块
│   ├── __init__.py
│   ├── base.py            # 格式化器抽象基类
│   ├── xmind.py           # XMind 格式化器
│   └── markdown.py        # Markdown 格式化器
├── static/
│   └── index.html         # Vue.js 前端界面
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
