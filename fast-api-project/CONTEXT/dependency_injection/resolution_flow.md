---
description: Step-by-step dependency resolution — from function signature analysis through recursive solving to value injection
---

# Dependency Resolution Flow

## Phase 1: Analysis (startup time)

`get_dependant()` in `dependencies/utils.py` introspects the endpoint signature:

1. `get_typed_signature()` extracts parameters with resolved `Annotated` types
2. Each parameter is classified by `analyze_param()`:
   - If it has a `Depends()` marker → sub-dependency (recurse)
   - If annotated with `Path/Query/Header/Cookie/Body/Form/File` → classified param
   - If name matches a path template variable → path param
   - Otherwise → query param (default location)
3. Special names are detected: `request`, `websocket`, `response`, `background_tasks`
4. Result is a `Dependant` dataclass holding all classified params and sub-dependencies

`get_flat_dependant()` then flattens the tree: recursively collects all params from
sub-dependencies into a single `Dependant`. This flat version is used for OpenAPI
schema generation (needs all params in one place).

## Phase 2: Solving (per-request)

`solve_dependencies()` runs on every request:

1. Iterates over `dependant.dependencies` (sub-deps first, depth-first)
2. For each sub-dependency:
   - Checks `dependency_overrides` dict (for testing)
   - Checks the cache (`dependency_cache` keyed by `(callable, scopes, scope)`)
   - If not cached: recursively calls `solve_dependencies()` for sub-dep
   - Executes the dependency callable (async or sync via `run_in_threadpool()`)
   - If it's a generator/async generator: wraps in AsyncExitStack for cleanup
   - Stores result in cache and values dict
3. After all deps resolved, extracts path/query/header/cookie/body params from the request
4. Returns a `SolvedDependency` with all resolved values and any validation errors

## Key data structures

- `Dependant` (`dependencies/models.py`) — the dependency tree node
- `SolvedDependency` — result of solving, contains `values`, `errors`, `background_tasks`
- `dependency_cache` — dict passed through recursive calls, enables cross-dep caching
