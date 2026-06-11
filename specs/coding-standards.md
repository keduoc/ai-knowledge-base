# Coding Standards

## Naming

- 变量、函数、方法: `snake_case`
- 类、异常: `PascalCase`
- 常量: `UPPER_SNAKE_CASE`
- 模块名: 简短全小写，必要时加下划线
- 私有成员: 前缀单下划线 `_internal_method`

## Style

- 行宽上限 100 字符
- 缩进 4 空格（禁止 Tab）
- 文件末尾一个换行符
- 导入顺序: 标准库 → 第三方库 → 本地模块，每组之间空一行
- 避免 `from module import *`

## Docstrings

- 公共函数/类/方法必须有 docstring
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

## Logging

- 使用 `logging` 模块，禁止裸 `print()`
- 日志级别: `DEBUG`（调试）、`INFO`（关键节点）、`WARNING`（可恢复异常）、`ERROR`（不可恢复异常）
- 每个模块定义独立的 logger: `logger = logging.getLogger(__name__)`

## Type Hints

- 所有公共函数必须有类型注解
- 使用 `dict[str, Any]` 而非 `Dict`（Python 3.9+ 语法）
- 复杂类型用 `TypeAlias` 定义别名

## Error Handling

- 不吞异常，至少记录日志
- 不裸 `except:`，必须指定异常类型
- 外部 API 调用必须包裹 try/except 并记录日志

## Configuration

- API Key / Token / Webhook URL 必须从环境变量或 `.env` 文件读取
- 禁止硬编码任何密钥
- 配置常量集中在 `config.py` 中

## Git

- Commit message 遵循 Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- 每个 commit 只做一件事
- 不提交 `.env`、`__pycache__`、`*.pyc`、`knowledge/raw/`、`knowledge/articles/`
