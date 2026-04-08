---
description: How dependency_overrides enables test mocking — the override lookup mechanism in solve_dependencies()
---

# Dependency Overrides for Testing

`app.dependency_overrides` is a plain dict mapping original callables to
replacement callables. During `solve_dependencies()`
(`fastapi/dependencies/utils.py:598`), before executing any dependency, the
solver checks this dict:

```python
if dependency_overrides_provider:
    original = dep.dependency
    dep.dependency = dependency_overrides_provider.dependency_overrides.get(original, original)
```

This enables test patterns like:

```python
def override_get_db():
    return test_db

app.dependency_overrides[get_db] = override_get_db
```

The override is looked up by identity (the original callable object), not by
name. This means you must reference the exact same function object that was
used in `Depends()`.

Overrides apply transitively — if dependency A depends on B, and B is
overridden, A will receive the overridden B.
