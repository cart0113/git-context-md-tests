---
description: How the dependency cache key includes OAuth scopes — same dependency can resolve differently per security context
---

# Dependency Cache Keys

The dependency cache is a dict keyed by a tuple (in `solve_dependencies()` at
`fastapi/dependencies/utils.py:598`):

```python
cache_key = (dependency_callable, tuple(oauth_scopes), scope)
```

This means the **same dependency function** can be resolved multiple times in
one request if it's used with different OAuth scopes. For example, if
`get_current_user` is used in two places with
`Security(get_current_user, scopes=["read"])` vs
`Security(get_current_user, scopes=["write"])`, each gets its own cache entry.

When `use_cache=False` is set on a `Depends()`, the dependency is always
re-executed regardless of cache state. This is useful for dependencies with
side effects.

The cache dict is created once per request and passed through all recursive
`solve_dependencies()` calls, ensuring cross-branch deduplication within the
dependency tree.
