# AI 知识库助手

## 项目概述

自动采集 GitHub Trending 和 Hacker News 等平台中 AI/LLM/Agent 领域的技术动态，经 AI 分析后结构化存储为 JSON 条目，最后通过 Telegram 和飞书多渠道分发输出。

## 技术栈

- **语言**: Python 3.12
- **AI 编排**: OpenCode + 国产大模型、LangGraph、OpenClaw

## 编码规范

### Naming

- 变量、函数、方法: `snake_case`
- 类、异常: `PascalCase`
- 常量: `UPPER_SNAKE_CASE`
- 模块名: 简短全小写，必要时加下划线
- 私有成员: 前缀单下划线 `_internal_method`（不用双下划线）

### Style

- 行宽上限 100 字符（URL 和路径字符串允许例外）
- 缩进 4 空格（禁止 Tab）
- 文件末尾一个换行符
- 导入顺序: 标准库 → 第三方库 → 本地模块，每组之间空一行
- 避免 `from module import *`

### Docstrings

- 所有函数/类/方法（含私有）必须有 docstring
- 使用 Google 风格

```python
def fetch_data(url: str, timeout: int = 10) -> dict:
    """从指定 URL 获取 JSON 数据。

    Args:
        url: 请求地址。
        timeout: 超时秒数，默认 10。

    Returns:
        解析后的 JSON 字典。

    Raises:
        requests.RequestException: 网络请求失败。
    """
```

### Logging

- 使用 `logging` 模块，**禁止裸 `print()`**
- 日志级别: `DEBUG`（调试）、`INFO`（关键节点）、`WARNING`（可恢复异常）、`ERROR`（不可恢复异常）
- 每个模块定义独立的 logger: `logger = logging.getLogger(__name__)`
- 默认输出到 stderr，后续按需添加文件 handler

### Type Hints

- 所有公共函数必须有类型注解
- 全程使用 Python 3.10+ 语法: `str | None`、`dict[str, Any]`、`list[int]`，不用 `Optional`、`Union`、`List`
- 复杂类型用 `TypeAlias` 定义别名

### Error Handling

- 不吞异常，至少记录日志
- 不裸 `except:`，必须指定异常类型
- 外部 API 调用必须包裹 try/except 并记录日志
- 关键采集 API: 3 次重试 + 指数退避；下游分析/分发 API: 仅记日志不重试

### Configuration

- API Key / Token / Webhook URL 必须从环境变量或 `.env` 文件读取，禁止硬编码
- 配置常量集中在 `config.py` 中
- 关键配置（Token、Webhook URL）缺了就报错退出，非关键配置（timeout、log_level）可给默认值

### Git

- Commit message 遵循 Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- 分支命名: `<type>/<short-desc>`（如 `feat/add-retry-logic`、`fix/api-timeout`）
- PR 标题也遵循 Conventional Commits 格式
- 每个 commit 只做一件事
- 不提交 `.env`、`__pycache__`、`*.pyc`、`knowledge/raw/`、`knowledge/articles/`

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
