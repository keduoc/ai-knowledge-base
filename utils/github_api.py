"""GitHub API 工具模块。"""

import logging
import os
from typing import Any

import requests

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"


def get_repo_info(owner: str, repo: str) -> dict[str, Any]:
    """获取指定仓库的基本信息。

    Args:
        owner: 仓库所有者用户名。
        repo: 仓库名称。

    Returns:
        包含仓库信息的字典，字段包括 name、full_name、description、
        stargazers_count、forks_count。请求失败时返回空字典。

    Raises:
        ValueError: owner 或 repo 为空字符串。
    """
    if not owner or not repo:
        raise ValueError("owner 和 repo 不能为空")

    token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        logger.exception("获取仓库信息失败: %s/%s", owner, repo)
        return {}

    data: dict[str, Any] = response.json()
    return {
        "name": data.get("name"),
        "full_name": data.get("full_name"),
        "description": data.get("description"),
        "stargazers_count": data.get("stargazers_count"),
        "forks_count": data.get("forks_count"),
    }
