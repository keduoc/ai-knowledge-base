# AI 知识库助手

## 项目概述

自动采集 GitHub Trending 和 Hacker News 等平台中 AI/LLM/Agent 领域的技术动态，经 AI 分析后结构化存储为 JSON 条目，最后通过 Telegram 和飞书多渠道分发输出。

## 技术栈

- **语言**: Python 3.12
- **AI 编排**: OpenCode + 国产大模型、LangGraph、OpenClaw

## 编码规范

- 遵循 PEP 8 风格指南
- 变量与函数使用 `snake_case`，类名使用 `PascalCase`
- 所有公共函数使用 Google 风格 docstring
- 使用 `logging` 模块输出日志，**禁止裸 `print()`**

## 项目结构

```
ai-knowledge-base/
├── .opencode/
│   ├── agents/          # Agent 定义与配置
│   └── skills/          # Skill 定义与配置
├── knowledge/
│   ├── raw/             # 原始采集数据
│   └── articles/        # 分析后的结构化文章 JSON
├── AGENTS.md
└── README.md
```

## 知识条目 JSON 格式

```json
{
  "id": "uuid-v4",
  "title": "文章标题",
  "source_url": "https://github.com/...",
  "source_name": "github-trending",
  "summary": "AI 生成的中文摘要，200 字以内",
  "tags": ["LLM", "Agent", "Open Source"],
  "published_at": "2024-01-01T00:00:00Z",
  "fetched_at": "2024-01-01T12:00:00Z",
  "status": "pending",
  "processed_by": "analyzer-agent"
}
```

字段说明：
| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `str` | UUID v4 唯一标识 |
| `title` | `str` | 原始标题 |
| `source_url` | `str` | 文章来源链接 |
| `source_name` | `str` | 来源名称（`github-trending` / `hackernews`） |
| `summary` | `str` | AI 摘要（中文，≤200 字） |
| `tags` | `list[str]` | 标签列表 |
| `published_at` | `str` | 文章发布日期（ISO 8601） |
| `fetched_at` | `str` | 采集日期（ISO 8601） |
| `status` | `str` | `pending` → `analyzed` → `distributed` |
| `processed_by` | `str` | 处理该条目的 Agent 名称 |

## Agent 角色概览

| 角色 | Agent 名称 | 职责 | 输入 | 输出 |
|------|-----------|------|------|------|
| 采集 | `collector-agent` | 从 GitHub Trending / Hacker News 抓取 AI 相关条目，去重后写入 `knowledge/raw/` | API 数据流 | 原始 JSON（`raw/`） |
| 分析 | `analyzer-agent` | 对原始条目进行 AI 摘要、打标签、判定质量，生成结构化条目 | `raw/` 目录 | 结构化 JSON（`articles/`） |
| 整理 | `distributor-agent` | 将已分析条目推送到 Telegram 频道和飞书群 | `articles/` 目录（status=analyzed） | 多渠道消息 |

## 红线

- **禁止**在代码中硬编码 API Key / Token / Webhook URL，必须从环境变量或配置文件读取
- **禁止**将 `knowledge/raw/` 和 `knowledge/articles/` 中的 JSON 文件提交到 Git（已配置 `.gitignore`）
- **禁止**裸 `print()`，所有输出走 `logging`
- **禁止**对第三方 API 进行高频轮询（间隔 ≥ 60s），避免触发限流
- **禁止**采集非技术类或无关领域（娱乐、政治等）的内容
- **禁止**推送未经验证的 URL 到外部渠道
