---
name: tech-summary
description: 当需要对采集的技术内容进行深度分析总结时使用此技能
user-invocable: true
---

# 技术深度分析技能

## 使用场景

- 对 `knowledge/raw/` 中已采集的 GitHub 热门项目进行深度分析
- 生成每条项目的中文摘要、技术亮点、质量评分和标签建议
- 发现趋势：识别本期项目的共同主题和新兴概念

## 执行步骤

### 第 1 步：读取最新采集文件

使用 Glob 扫描 `knowledge/raw/` 目录，找到最新日期的采集文件（以 `github-trending-` 开头），
使用 Read 读取其 JSON 内容，提取 `items` 数组。

### 第 2 步：逐条深度分析

对每条项目执行以下分析动作：

#### 2.1 撰写中文摘要

- 基于项目 description、topics、README 等信息撰写，≤ **50 字**
- 公式：**项目名 + 核心功能 + 技术亮点**，不添加主观评价
- 信息不足时使用 WebFetch 访问仓库页面补充上下文

#### 2.2 提炼技术亮点

- 列出 **2-3 个**具体技术亮点，用事实说话
- 好例子：「支持 100+ 种 LLM 统一调用接口」「基于 MoE 架构，推理速度提升 3 倍」
- 坏例子：「功能强大」「很好用」「值得关注」
- 亮点必须可验证，能从仓库 README / 代码中找到依据

#### 2.3 质量评分

按 1-10 分打分，附评分理由：

| 分数 | 等级       | 含义                                           |
|------|------------|------------------------------------------------|
| 9-10 | 改变格局   | 可能改变技术格局的成果（突破性架构、新范式）    |
| 7-8  | 直接有帮助 | 可直接落地使用的工具/方法                       |
| 5-6  | 值得了解   | 有一定参考价值，值得技术人了解                  |
| 1-4  | 可略过     | 价值一般、信息量少                              |

评分维度：创新性、实用性、完整性、社区影响力。

约束：每批次 15 个项目中，**9-10 分不超过 2 个**。

#### 2.4 标签建议

从以下标签池中选择 2-5 个最匹配的标签：

| 分类     | 可选标签                                                    |
|----------|-------------------------------------------------------------|
| 模型技术 | LLM, VLM, SLM, MoE, RAG, Fine-tuning, Prompt-Engineering    |
| 应用场景 | Agent, Copilot, Chatbot, Code-Generation, Search            |
| 基础设施 | Vector-DB, Inference-Framework, MLOps, Data-Pipeline        |
| 开源状态 | Open-Source, Open-Weights, Proprietary                      |
| 领域     | NLP, CV, Speech, Multimodal, Robotics                       |
| 语言支持 | Chinese, English, Multilingual                              |
| 其他     | Benchmark, Survey, Tutorial, Paper                          |

### 第 3 步：趋势发现

对全部 15 条项目进行横向归纳：

- **共同主题**：出现 3 次以上的技术词汇或方向（如「Agent 框架」「推理优化」），用 2-3 句话概括
- **新概念**：首次出现或近期兴起的技术概念（如新架构名称、新型工具范式），列出 1-3 个
- 趋势描述必须基于本期项目内容，不得凭空编造

### 第 4 步：输出分析结果 JSON

将分析结果写入文件：
- 路径：`knowledge/raw/tech-summary-YYYY-MM-DD.json`
- 日期为分析日期（UTC）
- 编码：UTF-8，缩进 2 空格

## 注意事项

1. **摘要长度**：严格 ≤ 50 字，超长会截断。
2. **评分克制**：9-10 分是「改变格局」级别，每批最多 2 个，宁少勿滥。
3. **亮点具体**：避免空泛描述，每条亮点必须有事实支撑。
4. **标签来源**：所有标签必须来自预定义标签池，禁止自创。
5. **趋势真实**：趋势发现基于本期实际项目，不得臆测。
6. **信息验证**：必要时通过 WebFetch 访问原文，确保分析准确。

## 输出格式

```json
{
  "source": "tech-summary",
  "skill": "tech-summary",
  "analyzed_at": "2026-06-15T00:00:00Z",
  "trends": {
    "common_themes": "本期以 Agent 框架和推理优化为主，多个项目聚焦多 Agent 协作与低延迟推理部署。",
    "new_concepts": ["MCP 协议集成", "边缘端 LLM 推理"]
  },
  "items": [
    {
      "name": "owner/repo",
      "url": "https://github.com/owner/repo",
      "summary": "项目名：一句话中文摘要，≤50 字",
      "highlights": [
        "基于 MoE 架构，在单张 GPU 上实现 70B 模型推理",
        "支持 OpenAI 兼容 API，零迁移成本"
      ],
      "score": 8,
      "score_reason": "架构创新实用，落地门槛低，社区活跃度高",
      "tags": ["LLM", "Inference-Framework", "Open-Source"]
    }
  ]
}
```

| 字段                   | 类型        | 说明                                   |
|------------------------|-------------|----------------------------------------|
| source                 | string      | 固定 `"tech-summary"`                  |
| skill                  | string      | 固定 `"tech-summary"`                  |
| analyzed_at            | string      | 分析时间（ISO 8601，UTC）              |
| trends.common_themes   | string      | 本期共同主题，2-3 句话                 |
| trends.new_concepts    | list[str]   | 新概念列表，1-3 个                     |
| items[].name           | string      | 仓库全名 `owner/repo`                  |
| items[].url            | string      | 仓库链接                               |
| items[].summary        | string      | 中文摘要，≤50 字                        |
| items[].highlights     | list[str]   | 2-3 个技术亮点                          |
| items[].score          | integer     | 质量评分 1-10，9-10 分每批 ≤ 2 个       |
| items[].score_reason   | string      | 评分依据，1 句话                       |
| items[].tags           | list[str]   | 2-5 个标签，来自预定义标签池            |
