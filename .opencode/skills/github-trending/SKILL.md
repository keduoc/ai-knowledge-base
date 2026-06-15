---
name: github-trending
description: 抓取 GitHub Trending 页面获取热门 AI/LLM/Agent 项目列表，输出结构化 JSON。Use when 用户提到 GitHub Trending、趋势榜、热榜、排行榜、热门仓库、今日/本周最火，或需要采集/抓取/拉取/爬/看看/查一下 GitHub 上的 AI/LLM/Agent/大模型项目，或问最近有什么新的/火的 AI 开源项目、看看趋势、有什么好项目、trending repos、what's trending on GitHub 时。覆盖中文和英文的多种表达。
user-invocable: true
---

# GitHub Trending 采集技能

## 使用场景

- 采集 GitHub 每日/每周热门项目，获取 AI/LLM/Agent 领域最新开源动态
- 生成结构化的热门项目列表，供下游分析使用
- 定时触发，自动汇总技术趋势

## 执行步骤

### 第 1 步：搜索热门仓库

调用 GitHub Search API 获取近期热门仓库：

- 搜索关键词：`AI OR LLM OR Agent OR RAG OR machine-learning`
- 排序方式：`stars`（按星标数降序）
- 时间范围：近 7 天创建或更新的仓库
- 每页 `per_page=30`，最多取 3 页

API 端点：

```url
https://api.github.com/search/repositories?q=AI+OR+LLM+OR+Agent+OR+RAG+OR+machine-learning&sort=stars&order=desc&per_page=30
```

对于热门仓库还需获取其详细信息和 Topics 标签：

```url
https://api.github.com/repos/{owner}/{repo}
```

### 第 2 步：提取信息

从 API 返回结果中提取以下字段：

| 字段     | API 来源路径             |
|----------|--------------------------|
| name     | `full_name`              |
| url      | `html_url`               |
| stars    | `stargazers_count`       |
| language | `language`               |
| topics   | `topics`（需单独请求）   |
| 描述     | `description`            |

### 第 3 步：过滤

**纳入规则**（满足任一即保留）：

- 项目领域为 AI/LLM/Agent/RAG/Machine Learning/Deep Learning/NLP/CV 等
- 标题或描述中出现上述关键词
- topics 中包含 AI 相关标签

**排除规则**（满足任一即丢弃）：

- Awesome 列表、教程合集、面试题集合等精选类仓库
- 非技术类项目（娱乐、政治、财经等）
- 已 archived / deprecated 的项目
- 纯基础设施类且与 AI 无直接关联的（如通用 CI/CD 工具）

### 第 4 步：去重

- 以 `full_name` 为唯一键去重（同一仓库多次请求只保留一条）
- 同一仓库的不同 API 版本（如 rest vs graphql）视为重复

### 第 5 步：撰写中文摘要

为每个项目撰写一句话中文摘要，公式：

> **项目名** + 做什么（一句话概括核心功能） + 为什么值得关注（技术亮点/独特性）

要求：
- 基于仓库 description 和 topics 实际内容撰写，不凭空捏造
- 控制在 60 字以内
- 突出 AI/LLM/Agent 领域相关特性
- 如 description 不存在或信息不足，注明「暂无描述」

示例：
> **LangChain**：LLM 应用开发框架，提供链式调用和 Agent 编排能力，生态丰富适合快速构建原型。

### 第 6 步：排序取 Top 15

- 按 stars 降序排列所有筛选后的条目
- 截取前 15 名作为最终输出
- 若不足 15 条，保留全部并在日志中记录原因

### 第 7 步：输出 JSON

将最终结果写入文件：
- 路径：`knowledge/raw/github-trending-YYYY-MM-DD.json`
- 日期为当前采集日期（UTC）
- 编码：UTF-8
- 格式：单行 JSON（`indent=2`）

## 注意事项

1. **API 频率限制**：GitHub Search API 未认证每分钟 10 次，认证后 30 次。两次请求间隔 ≥ 2 秒。
2. **重试机制**：API 请求失败时最多重试 3 次，指数退避（1s / 2s / 4s）。
3. **数据完整性**：topics 需单独请求 `/repos/{owner}/{repo}` 接口获取，不在搜索 API 返回结果中。
4. **日期处理**：所有日期使用 UTC 时区，格式 `YYYY-MM-DD`。
5. **信息真实性**：所有摘要基于仓库实际描述撰写，禁止编造功能或特性。

## 输出格式

```json
{
  "source": "github-trending",
  "skill": "github-trending",
  "collected_at": "2026-06-15T00:00:00Z",
  "items": [
    {
      "name": "owner/repo",
      "url": "https://github.com/owner/repo",
      "summary": "项目名：一句话中文摘要，≤60 字",
      "stars": 12345,
      "language": "Python",
      "topics": ["llm", "agent", "open-source"]
    }
  ]
}
```

| 字段           | 类型        | 说明                                   |
|----------------|-------------|----------------------------------------|
| source         | string      | 固定 `"github-trending"`               |
| skill          | string      | 固定 `"github-trending"`               |
| collected_at   | string      | 采集时间（ISO 8601，UTC）              |
| items[].name   | string      | 仓库全名 `owner/repo`                  |
| items[].url    | string      | 仓库链接                               |
| items[].summary | string     | 中文摘要，≤60 字                        |
| items[].stars  | integer     | Star 数量                               |
| items[].language | string    | 主要编程语言                           |
| items[].topics | list[str]   | 仓库主题标签                           |
