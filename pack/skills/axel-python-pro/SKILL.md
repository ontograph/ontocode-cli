---
name: axel-python-pro
description: Use when building Python 3.11+ applications requiring type safety, async programming, or robust error handling. Generates type-annotated Python code, configures mypy in strict mode, writes pytest test suites with fixtures and mocking, and validates code with Ruff. Invoke for type hints, async/await patterns, dataclasses, dependency injection, logging configuration, and structured error handling.
license: MIT
metadata:
  author: https://github.com/Jeffallan
  version: "1.1.0"
  vendored_from: https://github.com/Jeffallan/claude-skills
  vendored_ref: 882ef55e377dbf9a4dbe496bb41ac6ccd0e555cf
  vendored_on: "2026-08-22"
  domain: language
  triggers: Python development, type hints, async Python, pytest, mypy, dataclasses, Python best practices, Pythonic code
  role: specialist
  scope: implementation
  output-format: code
---

# Python Pro

Modern Python 3.11+ specialist focused on type-safe, async-first, production-ready code.

## Axel Workspace Overrides

These rules override conflicting upstream guidance:

- Target Python 3.11+.
- Validate with `mypy --strict`, `ruff check`, and `ruff format --check`; do not add Black as a second formatter.
- Meet the repository's coverage gate when one exists; otherwise optimize for meaningful branch and error-path coverage rather than a percentage by itself.
- Add dependencies only through the repository's approved dependency and lockfile workflow.
- Bound concurrent I/O, set timeouts, check response status, and use structured cancellation for network operations.

## When to Use This Skill

- Writing type-safe Python with complete type coverage
- Implementing async/await patterns for I/O operations
- Setting up pytest test suites with fixtures and mocking
- Creating Pythonic code with comprehensions, generators, context managers
- Building packages with Poetry and proper project structure
- Performance optimization and profiling

## Core Workflow

1. **Analyze codebase** — Review structure, dependencies, type coverage, test suite
2. **Design interfaces** — Define protocols, dataclasses, type aliases
3. **Implement** — Write Pythonic code with full type hints and error handling
4. **Test** — Create a comprehensive pytest suite that meets the repository coverage gate
5. **Validate** — Run `mypy --strict`, `ruff check`, and `ruff format --check`
   - If mypy fails: fix type errors reported and re-run before proceeding
   - If tests fail: debug assertions, update fixtures, and iterate until green
   - If Ruff reports issues: apply auto-fixes, then re-validate

## Reference Guide

Load detailed guidance based on context:

| Topic | Reference | Load When |
|-------|-----------|-----------|
| Type System | `references/type-system.md` | Type hints, mypy, generics, Protocol |
| Async Patterns | `references/async-patterns.md` | async/await, asyncio, task groups |
| Standard Library | `references/standard-library.md` | pathlib, dataclasses, functools, itertools |
| Testing | `references/testing.md` | pytest, fixtures, mocking, parametrize |
| Packaging | `references/packaging.md` | poetry, pip, pyproject.toml, distribution |

## Constraints

### MUST DO
- Type hints for all function signatures and class attributes
- Standard Python style enforced by Ruff formatting
- Comprehensive docstrings (Google style)
- Coverage meeting the repository gate, with emphasis on meaningful branches and error paths
- Use `X | None` instead of `Optional[X]` (Python 3.10+)
- Async/await for I/O-bound operations
- Dataclasses over manual __init__ methods
- Context managers for resource handling

### MUST NOT DO
- Skip type annotations on public APIs
- Use mutable default arguments
- Mix sync and async code improperly
- Ignore mypy errors in strict mode
- Use bare except clauses
- Hardcode secrets or configuration
- Prefer `pathlib` over string-based path manipulation; `os.path` remains valid where an OS-level API requires it

## Code Examples

### Type-annotated function with error handling
```python
from pathlib import Path

def read_config(path: Path) -> dict[str, str]:
    """Read configuration from a file.

    Args:
        path: Path to the configuration file.

    Returns:
        Parsed key-value configuration entries.

    Raises:
        FileNotFoundError: If the config file does not exist.
        ValueError: If a line cannot be parsed.
    """
    config: dict[str, str] = {}
    with path.open() as f:
        for line in f:
            key, _, value = line.partition("=")
            if not key.strip():
                raise ValueError(f"Invalid config line: {line!r}")
            config[key.strip()] = value.strip()
    return config
```

### Dataclass with validation
```python
from dataclasses import dataclass, field

@dataclass
class AppConfig:
    host: str
    port: int
    debug: bool = False
    allowed_origins: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not (1 <= self.port <= 65535):
            raise ValueError(f"Invalid port: {self.port}")
```

### Async pattern
```python
import asyncio
from collections.abc import Sequence

import httpx

async def fetch_all(
    urls: Sequence[str], *, concurrency: int = 10, timeout_seconds: float = 10.0
) -> list[bytes]:
    """Fetch URLs concurrently with bounded concurrency and shared timeout."""
    if concurrency < 1:
        raise ValueError("concurrency must be positive")

    semaphore = asyncio.Semaphore(concurrency)

    async def fetch(client: httpx.AsyncClient, url: str) -> bytes:
        async with semaphore:
            response = await client.get(url)
            response.raise_for_status()
            return response.content

    async with httpx.AsyncClient(timeout=httpx.Timeout(timeout_seconds)) as client:
        async with asyncio.TaskGroup() as task_group:
            tasks = [
                task_group.create_task(fetch(client, url), name=f"fetch:{url}")
                for url in urls
            ]

    return [task.result() for task in tasks]
```

### pytest fixture and parametrize
```python
import pytest
from pathlib import Path

@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    cfg = tmp_path / "config.txt"
    cfg.write_text("host=localhost\nport=8080\n")
    return cfg

@pytest.mark.parametrize("port,valid", [(8080, True), (0, False), (99999, False)])
def test_app_config_port_validation(port: int, valid: bool) -> None:
    if valid:
        AppConfig(host="localhost", port=port)
    else:
        with pytest.raises(ValueError):
            AppConfig(host="localhost", port=port)
```

### mypy strict configuration (pyproject.toml)
```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

Clean `mypy --strict` output looks like:
```
Success: no issues found in 12 source files
```
Any reported error (e.g., `error: Function is missing a return type annotation`) must be resolved before the implementation is considered complete.

## Output Templates

When implementing Python features, provide:
1. Module file with complete type hints
2. Test file with pytest fixtures
3. Type checking confirmation (mypy --strict passes)
4. Brief explanation of Pythonic patterns used

## Knowledge Reference

Python 3.11+, typing module, mypy, pytest, Ruff, dataclasses, async/await, asyncio, pathlib, functools, itertools, Poetry, Pydantic, contextlib, collections.abc, Protocol

[Documentation](https://jeffallan.github.io/claude-skills/skills/language/python-pro/)
