---
name: ontocode-python
description: Python conventions for this repo.
disable-model-invocation: true
---

## Python Development Best Practices

### Ignore Python 2 compatibility

This project uses Python 3+. You should not use the `__future__` module.

If you need to worry about feature compatibility between different 3.xx point releases, check the
closest `pyproject.toml`'s `requires-python` field to see what minimum runtime version is supported.
