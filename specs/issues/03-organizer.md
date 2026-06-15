# Organizer 端到端验证

> GitHub: [#4](https://github.com/keduoc/ai-knowledge-base/issues/4)
> Agent: `.opencode/agents/organizer.md`

## depends_on

- [#3 Analyzer 端到端验证](https://github.com/keduoc/ai-knowledge-base/issues/3)

## What to build

读取 analyzer 产出的分析结果，去重后生成每日汇总日报 MD，存入 `knowledge/articles/`。

## Acceptance

- [ ] 正确读取 analyzer 输出的分析结果
- [ ] 去重检测：URL 重复的条目被正确跳过
- [ ] 日报按三档展示：🔥必看（score ≥ 8）、📖值得关注（5-7）、📋其他（≤4）
- [ ] 包含序言（2-3 句趋势概括）
- [ ] 包含标签分布统计表
- [ ] 文件命名格式 `YYYY-MM-DD-daily.md`
- [ ] 文件为合法 UTF-8 Markdown
- [ ] 尾部有 `*由 AI 知识库助手自动生成*` 标记
- [ ] 不存在命名冲突的文件时直接写入，存在时追加数字后缀
