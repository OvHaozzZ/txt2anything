# txt2anything Frontend

基于 Next.js 14 + TypeScript + Tailwind CSS 重构的现代化前端。

## 技术栈

- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **动画**: Framer Motion
- **图标**: Lucide React

## 项目结构

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── globals.css         # 全局样式
│   │   ├── layout.tsx          # 根布局
│   │   └── page.tsx            # 主页面
│   ├── components/             # React 组件
│   │   ├── ui/                 # 基础 UI 组件
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   ├── select.tsx
│   │   │   └── textarea.tsx
│   │   ├── file-upload.tsx     # 文件上传组件
│   │   ├── header.tsx          # 页头组件
│   │   ├── result-card.tsx     # 结果展示组件
│   │   └── settings-panel.tsx  # 设置面板组件
│   └── lib/                    # 工具库
│       ├── api.ts              # API 服务
│       ├── types.ts            # TypeScript 类型
│       └── utils.ts            # 工具函数
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── next.config.js
```

## 开发

```bash
# 安装依赖
npm install

# 启动开发服务器 (需要后端运行在 localhost:8000)
npm run dev

# 类型检查
npm run type-check

# 构建生产版本
npm run build
```

## 特性

- **组件化架构**: 可复用的 UI 组件库
- **类型安全**: 完整的 TypeScript 类型定义
- **响应式设计**: 适配桌面和移动设备
- **流畅动画**: 使用 Framer Motion 实现
- **无障碍访问**: 遵循 WCAG 标准
- **性能优化**:
  - 字体优化 (next/font)
  - 图片优化 (next/image)
  - 代码分割
