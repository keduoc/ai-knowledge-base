# Analyzer 端到端验证

> GitHub: [#3](https://github.com/keduoc/ai-knowledge-base/issues/3)
> Agent: `.opencode/agents/analyzer.md`

## depends_on

- [#2 Collector 端到端验证](https://github.com/keduoc/ai-knowledge-base/issues/2)

## What to build

读取 collector 产出的原始数据，对每条条目精准打标签（2-5 个），生成中文摘要和质量评分。

## Acceptance

- [ ] 正确读取 collector 输出的 JSON 数据
- [ ] 每条条目输出 2-5 个标签，标签来自预定义标签池
- [ ] 所有标签均来自预定义标签池，无自创标签
- [ ] 每条条目有中文摘要（≤200 字），基于实际内容
- [ ] 每条条目有质量评分 1-10，有合理的 score_reason
- [ ] 已分析条目数与输入一致，无遗漏
- [ ] 低分条目（score ≤ 4）已标注原因
- [ ] 必要时通过 WebFetch 访问原文验证标签准确性

## Output schema

`specs/schemas/analyzer-output.json`
