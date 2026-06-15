# Collector 端到端验证

> GitHub: [#2](https://github.com/keduoc/ai-knowledge-base/issues/2)
> Agent: `.opencode/agents/collector.md`

## depends_on

- [#1 项目脚手架](https://github.com/keduoc/ai-knowledge-base/issues/1)

## What to build

调用 collector agent 从 GitHub Trending 和 Hacker News 抓取 AI 相关内容，
经筛选后输出结构化 JSON。

## Acceptance

- [ ] 成功抓取 GitHub Trending（日榜 + 周榜）
- [ ] 成功抓取 Hacker News 首页
- [ ] 筛选后仅保留 AI/LLM/Agent 领域内容
- [ ] 条目数量 ≥ 15 条
- [ ] 每条 title、url、source、popularity、summary 五字段齐全
- [ ] 所有 url 为实际抓取到的链接，未编造
- [ ] 所有 summary 为中文，基于页面实际内容
- [ ] 条目已按 popularity 降序排列
- [ ] 来源标识准确（`github-trending` / `hackernews`）

## Output schema

`specs/schemas/collector-output.json`
