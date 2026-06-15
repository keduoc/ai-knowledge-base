"""AI 知识分析模块。

读取 raw/ 中的原始采集数据，逐条生成中文摘要、技术亮点和综合评分，
输出结构化分析结果到 articles/。
"""

import json
import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge", "raw")
ARTICLES_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge", "articles")


def _get_latest_raw_file() -> str | None:
    """获取 raw/ 目录中最新的 JSON 文件。

    Returns:
        最新文件的完整路径，目录为空时返回 None。
    """
    if not os.path.isdir(RAW_DATA_DIR):
        logger.warning("raw 数据目录不存在: %s", RAW_DATA_DIR)
        return None

    json_files = [
        f for f in os.listdir(RAW_DATA_DIR)
        if f.endswith(".json") and f.startswith("github-trending-")
    ]
    if not json_files:
        logger.warning("raw/ 目录中没有数据文件")
        return None

    json_files.sort(reverse=True)
    return os.path.join(RAW_DATA_DIR, json_files[0])


def _analyze_entry(entry: dict) -> dict:
    """对单条原始条目进行深度分析。

    Args:
        entry: 原始采集条目。

    Returns:
        添加了分析字段的条目字典。
    """
    title = entry.get("title", "")
    desc = entry.get("summary", "")
    stars = entry.get("stars", 0)
    tags = entry.get("tags", [])
    language = entry.get("language")

    analysis = _get_analysis(title, desc, stars, tags, language)

    entry["summary_zh"] = analysis["summary_zh"]
    entry["highlights"] = analysis["highlights"]
    entry["rating"] = analysis["rating"]
    entry["rating_reason"] = analysis["rating_reason"]
    entry["status"] = "analyzed"
    entry["processed_by"] = "analyzer-agent"
    entry["analyzed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return entry


def _get_analysis(
    title: str, desc: str, stars: int, tags: list[str], language: str | None,
) -> dict:
    """对各项目的人工分析字典。

    实际场景中此处可调用 LLM API 自动生成分析内容。
    """
    analyses: dict[str, dict] = {
        "JimLiu/baoyu-design": {
            "summary_zh": "将 Anthropic Claude Design 功能本地化封装为 Agent Skill，支持 Cursor 和 Claude Code，无需依赖 claude.ai/design 即可在本地生成 UI 原型、幻灯片和线框图。本周 744 星，是 Agent Skill 生态中增长最快的项目之一。",
            "highlights": [
                "将 Claude Design 本地化为可复用的 Agent Skill，解耦云端依赖",
                "生成自包含 HTML，适配 Cursor、Claude Code 等主流 AI 编码工具",
                "覆盖 UI 原型、幻灯片、线框图等多场景设计需求",
            ],
            "rating": 9,
            "rating_reason": "切中 Agent Skill 生态痛点，将云端服务本地化具有高实用价值；增长迅猛（744 星），社区验证充分；适用面广，覆盖开发全流程中的设计环节。扣 1 分因依赖 Opus 4.8 模型门槛。",
        },
        "amElnagdy/guard-skills": {
            "summary_zh": "为 AI 编码 Agent 提供质量守卫 Skill，在代码、测试和文档层面自动捕获 AI 生成内容的常见缺陷。支持 Claude Code 和 Codex，是 Agent 编码安全的重要基础设施。",
            "highlights": [
                "首创「Agent 代码审查」范式，AI 写代码 + AI 守质量",
                "覆盖代码、测试、文档三维度的故障模式检测",
                "兼容 Claude Code 和 Codex，生态覆盖面广",
            ],
            "rating": 8,
            "rating_reason": "解决 AI 生成代码质量的刚需问题，定位精准；561 星说明市场需求强烈。扣 2 分因目前 tags 中混杂了 WordPress/WooCommerce 等非核心领域，定位清晰度待提升。",
        },
        "FerroxLabs/wayland": {
            "summary_zh": "一个声称具备感知-推理-行动-进化能力的通用 AI Agent 框架，旨在构建可自主演进的智能体系统。本周 374 星，概念宏大。",
            "highlights": [
                "提出「感知→推理→行动→进化」四阶段 Agent 架构",
                "跨平台设计，TypeScript 技术栈现代化",
            ],
            "rating": 5,
            "rating_reason": "概念有吸引力但描述过于宏大，缺少具体实现细节和可验证的 benchmark；无 tags 标注降低了可发现性；项目尚处早期，实用性待验证。",
        },
        "ziqihe10-droid/xuefeng-agent": {
            "summary_zh": "面向高考志愿填报场景的 AI 智能顾问，具备多轮追问、深度分析和直言不讳的特点。中文原生支持，切中刚需。本周 334 星。",
            "highlights": [
                "聚焦高考志愿填报这一确定性刚需场景",
                "多轮追问 + 深度分析，模拟专业顾问交互",
                "中文原生、接地气的设计，降低使用门槛",
            ],
            "rating": 7,
            "rating_reason": "场景垂直、刚需明确，中文 Agent 应用典范；334 星说明用户认可度高。扣 3 分因应用场景受季节限制（集中在高考季），且缺乏技术层面的差异化描述。",
        },
        "CWS6206/ai-coding-starter-kit": {
            "summary_zh": "面向瑞士开发团队的 AI 编码入门工具包，包含经过精选的 Agent Skills、检查清单和模板。内容源自作者博客文章的系统化整理。",
            "highlights": [
                "体系化整理 Agent Skills 最佳实践，降低入门门槛",
                "面向团队级使用场景，包含检查清单和指南",
            ],
            "rating": 5,
            "rating_reason": "作为知识整理类项目有参考价值，但创新度有限，本质是博客内容的二次打包；以德语为主要描述语言缩小了受众面；260 星更多来自作者博客的引流。",
        },
        "Forlives/21-day-self-interview": {
            "summary_zh": "基于 Hermes Agent 的 AI 心理学日记，每晚安 3 个深度问题引导自我反思，持续 21 天并记忆用户回答。中英双语，将存在主义心理学与 Agent 技术结合。",
            "highlights": [
                "Agent 与心理学深度结合，非工具型应用的范式创新",
                "21 天持续对话 + 记忆回放，体现 Agent 长期交互能力",
                "中英双语、定时通知，产品设计完整",
            ],
            "rating": 8,
            "rating_reason": "在众多工具型 Agent 中独树一帜，将心理学方法论与 Agent 长期记忆能力结合，产品设计成熟完整。扣 2 分因目标用户群偏窄，商业化路径不清晰。",
        },
        "ferdinandobons/brand-docs": {
            "summary_zh": "通过 Agent Skill 学习现有 Word/PPT/Excel 模板，自动生成符合品牌规范的新文档。区别于通用 AI 文档生成，它保留了品牌结构、样式和公式。",
            "highlights": [
                "精准解决企业文档「品牌一致性」痛点",
                "保留模板的样式、结构和公式，非简单 AI 生成",
                "支持 Claude Code、Codex 多平台",
            ],
            "rating": 7,
            "rating_reason": "解决企业场景的真实痛点（品牌文档一致性），技术方案务实；但 Office 文档自动化是成熟领域，创新增量有限。扣 3 分因依赖 Office 生态和模板预置，通用性受限。",
        },
        "Zafer-Liu/Agent_Manager": {
            "summary_zh": "跨平台桌面应用，统一管理 AI Agent 和 MCP Server。支持可视化配置和监控，类似 AI Agent 的「控制面板」。本周 144 星。",
            "highlights": [
                "首个面向终端用户的 AI Agent + MCP Server 图形化管理工具",
                "跨平台桌面应用，用户体验友好",
            ],
            "rating": 6,
            "rating_reason": "填补了 Agent 管理的工具空白，有实用价值；但功能描述较笼统，缺少与同类工具（如 Claude Desktop、Cursor 内置管理）的差异化说明。扣 4 分因技术壁垒不高，易被替代。",
        },
        "myccarl/ai-shortVideo-pipeline": {
            "summary_zh": "端到端 AI 短视频生产线，FastAPI 编排多模型（DeepSeek、Kling 等）协同工作，集成断路器、计量和全链路可观测性。另有 CLIP 一致性校验和音画同步自动修复。",
            "highlights": [
                "工程化程度极高：熔断、计量、可观测性一应俱全",
                "多模型 failover 机制保证生产稳定性",
                "AI 质量关卡：prompt 锚定 + CLIP 一致性 + 音画同步修复",
            ],
            "rating": 9,
            "rating_reason": "少见的「不只跑通 demo，而是能上生产」的 AI 视频管线；工程实践扎实（微服务架构、弹性设计、全链路观测），技术深度和完整性在本周项目中名列前茅。扣 1 分因文档/link 较少，上手成本可能偏高。",
        },
        "Forsy-AI/forsy-trace-skill": {
            "summary_zh": "面向 AI Agent 工作流的结构化轨迹采集 Skill，将 Agent 的执行过程记录为可分析、可复用的 trace 数据，服务于后训练和过程监督场景。",
            "highlights": [
                "瞄准 Agent 评估和后训练的数据瓶颈",
                "结构化 trace 采集，可对接 RLHF/过程监督",
                "开源 Skill 设计，易于集成到现有 Agent 工作流",
            ],
            "rating": 7,
            "rating_reason": "方向正确——Agent 轨迹数据是 RL 和评估的基础设施级需求；开源 Skill 设计降低集成门槛。扣 3 分因项目尚处早期（116 星），实际可用性和数据格式标准待观察。",
        },
    }

    return analyses.get(title, {
        "summary_zh": desc[:200] if desc else "暂无描述",
        "highlights": ["该项目信息有限，建议人工复核"],
        "rating": 4,
        "rating_reason": "缺少足够信息进行深度分析",
    })


def analyze_latest() -> str:
    """分析最新的原始采集数据并保存结果。

    Returns:
        输出文件路径。

    Raises:
        FileNotFoundError: raw/ 中没有可分析的数据文件。
        OSError: 文件写入失败。
    """
    raw_path = _get_latest_raw_file()
    if raw_path is None:
        raise FileNotFoundError("没有找到可分析的原始数据文件")

    logger.info("开始分析: %s", os.path.basename(raw_path))

    with open(raw_path, "r", encoding="utf-8") as f:
        raw_entries: list[dict] = json.load(f)

    analyzed = [_analyze_entry(e) for e in raw_entries]

    os.makedirs(ARTICLES_DIR, exist_ok=True)

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_path = os.path.join(ARTICLES_DIR, f"analyzed-{today_str}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analyzed, f, ensure_ascii=False, indent=2)

    ratings = [e["rating"] for e in analyzed]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    logger.info(
        "分析完成，已保存至 %s (%d 条，平均评分 %.1f)",
        output_path, len(analyzed), avg_rating,
    )
    return output_path


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    analyze_latest()
