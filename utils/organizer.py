"""知识条目整理模块。

从 analyzed JSON 中提取条目，按标准格式重整、去重，
每个条目单独保存为一个 JSON 文件。
"""

import json
import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

ARTICLES_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge", "articles")


def _get_latest_analyzed_file() -> str | None:
    """获取 articles/ 目录中最新的 analyzed JSON 文件。

    Returns:
        最新文件的完整路径，无文件时返回 None。
    """
    if not os.path.isdir(ARTICLES_DIR):
        logger.warning("articles 目录不存在: %s", ARTICLES_DIR)
        return None

    json_files = [
        f for f in os.listdir(ARTICLES_DIR)
        if f.endswith(".json") and f.startswith("analyzed-")
    ]
    if not json_files:
        logger.warning("articles/ 目录中没有 analyzed 文件")
        return None

    json_files.sort(reverse=True)
    return os.path.join(ARTICLES_DIR, json_files[0])


def _normalize_entry(entry: dict) -> dict:
    """将分析条目重整为标准知识条目格式。

    Args:
        entry: analyzed JSON 中的单条记录。

    Returns:
        符合 AGENTS.md 标准格式的知识条目。
    """
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "id": entry["id"],
        "title": entry["title"],
        "source_url": entry["source_url"],
        "source_name": entry["source_name"],
        "summary": entry.get("summary_zh", entry.get("summary", "")),
        "tags": entry.get("tags", []),
        "published_at": entry.get("published_at", now_iso),
        "fetched_at": entry.get("fetched_at", now_iso),
        "status": "organized",
        "processed_by": "organizer-agent",
        "organized_at": now_iso,
        "rating": entry.get("rating"),
        "rating_reason": entry.get("rating_reason", ""),
        "highlights": entry.get("highlights", []),
    }


def _deduplicate(entries: list[dict]) -> list[dict]:
    """按 source_url 去重，保留第一条。

    Args:
        entries: 原始条目列表。

    Returns:
        去重后的条目列表。
    """
    seen: set[str] = set()
    result: list[dict] = []
    for entry in entries:
        url = entry.get("source_url", "")
        if url in seen:
            logger.warning("重复条目已跳过: %s", url)
            continue
        seen.add(url)
        result.append(entry)
    return result


def organize_latest() -> str:
    """整理最新的分析结果，去重后每个条目存为独立 JSON。

    Returns:
        输出目录路径。

    Raises:
        FileNotFoundError: articles/ 中没有可整理的 analyzed 文件。
    """
    analyzed_path = _get_latest_analyzed_file()
    if analyzed_path is None:
        raise FileNotFoundError("没有找到可整理的 analyzed 文件")

    logger.info("开始整理: %s", os.path.basename(analyzed_path))

    with open(analyzed_path, "r", encoding="utf-8") as f:
        analyzed_entries: list[dict] = json.load(f)

    normalized = [_normalize_entry(e) for e in analyzed_entries]
    deduped = _deduplicate(normalized)
    logger.info("整理 %d 条，去重后 %d 条", len(normalized), len(deduped))

    os.makedirs(ARTICLES_DIR, exist_ok=True)

    saved = 0
    for entry in deduped:
        entry_id = entry["id"]
        file_path = os.path.join(ARTICLES_DIR, f"{entry_id}.json")

        if os.path.exists(file_path):
            logger.warning("文件已存在，跳过: %s.json", entry_id)
            continue

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False, indent=2)
        saved += 1

    logger.info("整理完成，保存 %d 个独立条目至 %s/", saved, ARTICLES_DIR)
    return ARTICLES_DIR


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    organize_latest()
