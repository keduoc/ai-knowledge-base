"""GitHub Trending 采集模块。

通过 GitHub Search API 搜索本周 AI/LLM/Agent 领域的热门仓库。
使用 curl 作为 HTTP 客户端以避免系统 Python SSL 证书问题。
"""

import json
import logging
import os
import subprocess
import uuid
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge", "raw")

AI_KEYWORDS = [
    "ai agent",
    "llm",
    "large language model",
    "RAG",
    "MCP server",
    "AI workflow",
]


def _build_curl_cmd(url: str) -> list[str]:
    """构建 curl 命令及参数。

    Args:
        url: 请求地址。

    Returns:
        curl 命令行参数列表。
    """
    cmd = [
        "curl", "-s", "--connect-timeout", "10", "--max-time", "15",
        "-H", "Accept: application/vnd.github+json",
        "-H", "User-Agent: ai-knowledge-base-collector/1.0",
    ]
    token = os.getenv("GITHUB_TOKEN")
    if token:
        cmd.extend(["-H", f"Authorization: Bearer {token}"])
    cmd.append(url)
    return cmd


def _api_request(url: str, retries: int = 3) -> dict | None:
    """通过 curl 发送 GitHub API 请求，带重试逻辑。

    Args:
        url: 请求地址。
        retries: 最大重试次数，默认 3。

    Returns:
        解析后的 JSON 字典，失败返回 None。
    """
    import time
    for attempt in range(retries):
        try:
            result = subprocess.run(
                _build_curl_cmd(url),
                capture_output=True, text=True, timeout=20,
            )
            if result.returncode != 0:
                logger.warning("curl 返回非零 (%d/%d): %s", attempt + 1, retries, result.stderr.strip())
                time.sleep(2 ** attempt)
                continue

            data: dict = json.loads(result.stdout)
            return data
        except json.JSONDecodeError:
            logger.warning("JSON 解析失败 (%d/%d), 可能触发限流", attempt + 1, retries)
            time.sleep(2 ** attempt)
        except subprocess.TimeoutExpired:
            logger.warning("请求超时 (%d/%d)", attempt + 1, retries)
            time.sleep(2 ** attempt)
    return None


def _fetch_trending_repos(limit: int = 10) -> list[dict]:
    """从 GitHub Search API 获取本周 AI 领域热门仓库。

    Args:
        limit: 返回的最大仓库数量，默认 10。

    Returns:
        仓库信息列表，按 stars 降序排列。
    """
    since_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    all_repos: dict[str, dict] = {}

    for keyword in AI_KEYWORDS:
        query = f"{keyword} created:>={since_date}"
        url = (
            f"{GITHUB_API_BASE}/search/repositories"
            f"?q={query.replace(' ', '+')}"
            f"&sort=stars&order=desc&per_page=10"
        )
        data = _api_request(url)
        if data is None:
            continue

        for item in data.get("items", [])[:10]:
            full_name = item.get("full_name", "")
            if full_name in all_repos:
                continue
            all_repos[full_name] = {
                "name": item.get("name"),
                "full_name": full_name,
                "description": item.get("description"),
                "stargazers_count": item.get("stargazers_count", 0),
                "forks_count": item.get("forks_count", 0),
                "language": item.get("language"),
                "html_url": item.get("html_url"),
                "topics": item.get("topics", []),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
            }

    sorted_repos = sorted(
        all_repos.values(),
        key=lambda r: r["stargazers_count"],
        reverse=True,
    )
    return sorted_repos[:limit]


def collect_github_trending(output_dir: str | None = None) -> str:
    """采集本周 GitHub Trending AI 仓库并保存为 JSON。

    Args:
        output_dir: 输出目录，默认使用 knowledge/raw/。

    Returns:
        输出文件的路径。

    Raises:
        OSError: 文件写入失败。
    """
    logger.info("开始采集 GitHub Trending AI 仓库...")

    repos = _fetch_trending_repos(limit=10)
    logger.info("采集到 %d 个 AI 相关仓库", len(repos))

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "..", "knowledge", "raw")
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(
        output_dir, f"github-trending-{today_str}.json"
    )

    entries = []
    for repo in repos:
        entry = {
            "id": str(uuid.uuid4()),
            "title": repo.get("full_name", repo.get("name", "")),
            "source_url": repo.get("html_url", ""),
            "source_name": "github-trending",
            "summary": repo.get("description") or "",
            "tags": repo.get("topics", []),
            "published_at": repo.get("created_at") or now_iso,
            "fetched_at": now_iso,
            "status": "pending",
            "processed_by": "collector-agent",
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "language": repo.get("language"),
        }
        entries.append(entry)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    logger.info("数据已保存至 %s (%d 条)", output_path, len(entries))
    return output_path


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    collect_github_trending()
