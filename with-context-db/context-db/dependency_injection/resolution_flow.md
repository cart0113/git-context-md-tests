---
description: Step-by-step dependency resolution — from function signature analysis through recursive solving to value injection, with file paths
---

# Dependency Resolution Flow

## Phase 1: Analysis (startup time)

`get_dependant()` (`fastapi/dependencies/utils.py:286`) introspects the
endpoint signature:

1. `get_typed_signature()` (`fastapi/dependencies/utils.py:228`) extracts
   parameters with resolved `Annotated` types
2. Each parameter is classified by `analyze_param()`
   (`fastapi/dependencies/utils.py:393`):
   - If it has a `Depends()` marker → sub-dependency (recurse)
   - If annotated with `Path/Query/Header/Cookie/Body/Form/File` → classified
     param
   - If name matches a path template variable → path param
   - Otherwise → query param (default location)
3. Special names are detected: `request`, `websocket`, `response`,
   `background_tasks` (via `add_non_field_param_to_dependency()` at line 362)
4. Result is a `Dependant` dataclass (`fastapi/dependencies/models.py:32`)
   holding all classified params and sub-dependencies

`get_flat_dependant()` (`fastapi/dependencies/utils.py:138`) then flattens the
tree: recursively collects all params from sub-dependencies into a single
`Dependant`. This flat version is used for OpenAPI schema generation.

## Phase 2: Solving (per-request)

`solve_dependencies()` (`fastapi/dependencies/utils.py:598`) runs on every
request (called from `get_request_handler()`'s inner `app()` at
`fastapi/routing.py:459`):

1. Iterates over `dependant.dependencies` (sub-deps first, depth-first)
2. For each sub-dependency:
   - Checks `dependency_overrides` dict (for testing)
   - Checks the cache (`dependency_cache` keyed by `(callable, scopes, scope)`)
   - If not cached: recursively calls `solve_dependencies()` for sub-dep
   - Executes the dependency callable (async or sync via `run_in_threadpool()`)
   - If it's a generator/async generator: wraps via `_solve_generator()`
     (line 578) using AsyncExitStack for cleanup
   - Stores result in cache and values dict
3. Extracts path/query/header/cookie/body params via `request_params_to_args()`
   (line 784) and `request_body_to_args()` (line 951)
4. Returns a `SolvedDependency` (line 590) with `values`, `errors`,
   `background_tasks`

## Key data structures

- `Dependant` (`fastapi/dependencies/models.py:32`) — the dependency tree node
- `SolvedDependency` (`fastapi/dependencies/utils.py:590`) — result of solving
- `dependency_cache` — dict passed through recursive calls, enables cross-dep
  caching
