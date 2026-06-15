# AI 知识库助手

自动采集 GitHub Trending 和 Hacker News 等平台中 AI/LLM/Agent 领域的技术动态，经 AI 分析后结构化存储，最后通过 Telegram 和飞书多渠道分发。

## 工作流

```
GitHub Trending / Hacker News
        │
        ▼
  collector-agent      ← 采集，筛选 AI 相关条目，写入 knowledge/raw/
        │
        ▼
  analyzer-agent       ← AI 摘要、标签打标、质量评分，写入 knowledge/articles/
        │
        ▼
  distributor-agent    ← 推送到 Telegram 频道和飞书群
```

## 技术栈

- **语言**: Python 3.12
- **AI 编排**: OpenCode + 国产大模型

## 项目结构

```
ai-knowledge-base/
├── .opencode/
│   ├── agents/          # Agent 定义（collector / analyzer / organizer）
│   └── skills/          # 技能定义（github-trending / tech-summary 等）
├── knowledge/
│   ├── raw/             # 原始采集数据
│   └── articles/        # 分析后的结构化条目
├── utils/               # Python 工具模块
├── specs/               # 需求规格文档
├── AGENTS.md            # AI 助手指令
└── README.md
```

## 快速开始

### 环境要求

- Python 3.12+
- OpenCode CLI
- Telegram Bot Token / 飞书 Webhook URL（分发用）

### 安装

```bash
# 克隆仓库
git clone https://github.com/keduoc/ai-knowledge-base.git
cd ai-knowledge-base

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入必要的 API Key 和 Webhook URL
```

### 运行

```bash
# 采集 GitHub Trending AI 项目
opencode skill github-trending

# 分析原始数据
opencode agent analyzer

# 推送到分发渠道
opencode agent organizer
```

## 知识条目格式

```json
{
  "id": "uuid-v4",
  "title": "文章标题",
  "source_url": "https://github.com/...",
  "source_name": "github-trending",
  "summary": "AI 生成的中文摘要",
  "tags": ["LLM", "Agent", "Open Source"],
  "published_at": "2024-01-01T00:00:00Z",
  "fetched_at": "2024-01-01T12:00:00Z",
  "status": "pending",
  "processed_by": "analyzer-agent"
}
```

## Agent 角色

| 角色 | Agent | 职责 |
|------|-------|------|
| 采集 | `collector-agent` | 从 GitHub Trending / Hacker News 抓取 AI 条目 |
| 分析 | `analyzer-agent` | AI 摘要、标签、质量评分 |
| 分发 | `distributor-agent` | 推送到 Telegram / 飞书多渠道 |

## 开发规范

详见 [AGENTS.md](./AGENTS.md)，摘要：

- Python 3.12+，遵循 `snake_case` / `PascalCase` / `UPPER_SNAKE_CASE` 命名
- 所有函数须有 Google 风格 docstring 和类型注解
- 使用 `logging` 模块，禁止 `print()`
- API Key 等敏感配置从环境变量读取，禁止硬编码
- Commit 遵循 Conventional Commits 格式

## License

MIT
