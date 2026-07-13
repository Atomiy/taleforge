# TaleForge - AI 智能故事生成器

基于 DeepSeek 大模型的多智能体协作故事生成系统。输入主题，一键生成高质量叙事内容。

## 快速开始

```bash
git clone https://github.com/Atomiy/taleforge.git
cd taleforge
python start.py          # 或双击 start.bat
```

首次运行自动创建虚拟环境、安装依赖、引导配置 API Key。  
浏览器打开 `http://127.0.0.1:8080`

## 核心功能

| 功能 | 说明 |
|------|------|
| **AI 故事生成** | 多智能体协作（策划→角色→写作→润色），SSE 实时流式输出 |
| **Markdown 渲染** | 生成内容支持标题、粗体、代码块等格式，即时预览 |
| **编辑/预览切换** | 类似 Obsidian 的源码/预览双模式，编辑时实时预览 |
| **多体裁风格** | 短篇/中篇/科幻/奇幻/悬疑/童话/诗歌等 10+ 体裁，10 种风格 |
| **角色系统** | 模板库 15 个预设角色 + 自定义添加，含外貌/性格/背景/动机 |
| **世界观 & 伏笔** | 自定义世界设定，显式伏笔管理，AI 自动埋设与回收 |
| **创作模板** | 8 套预设模板（英雄之旅、悬疑推理、都市爱情等），一键套用 |
| **作品管理** | 卷/章结构、跨章角色出场表、批量生成、概要生成 |
| **续写** | 基于前作上下文自动延续，保持人物和情节连贯 |
| **AI 灵感** | 根据设定智能推荐剧情方向、伏笔和角色 |
| **历史管理** | 搜索、分页、体裁筛选、收藏标记、编辑、导出 Markdown/TXT |
| **一键启动** | `start.py` 自动检查环境、安装依赖、配置密钥、启动服务 |

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 3 (CDN) + Tailwind CSS + Font Awesome |
| 后端 | FastAPI + Uvicorn (Python) |
| AI | DeepSeek API (Chat Completions) |
| 数据 | JSON 文件存储 |
| Markdown | 自研纯 JS 渲染器（零依赖） |

## 智能体流程

```mermaid
flowchart LR
    Input["用户输入"] --> P["Planner<br/>策划大纲"]
    P --> C["Character<br/>角色深化"]
    C --> W["Writer<br/>流式写作"]
    W --> Pol["Polisher<br/>润色整合"]
    Pol --> Output["输出故事"]
```

## 环境要求

- Python 3.9+
- DeepSeek API Key（[获取地址](https://platform.deepseek.com)）

## 项目结构

```
taleforge/
├── start.py              # 一键启动器（自动配置环境）
├── start.bat             # Windows 双击启动
├── requirements.txt      # Python 依赖
├── backend/
│   ├── agents/           # 智能体（Planner/Character/Writer/Polisher）
│   ├── routers/          # API 路由（story/history/config/works）
│   ├── services/         # 服务层（LLM客户端/编排器/历史管理）
│   ├── models/           # 数据模型
│   └── config.py         # 配置管理
├── frontend/
│   ├── index.html        # 单页应用（Vue 3）
│   ├── components/       # Vue 组件
│   └── assets/           # 静态资源
└── docs/                 # 文档
```

## License

MIT
