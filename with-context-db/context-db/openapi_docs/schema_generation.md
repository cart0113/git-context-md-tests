---
description: How get_openapi() at fastapi/openapi/utils.py:514 walks routes to build the OpenAPI spec — parameter extraction, schema refs, and separate input/output schemas
---

# OpenAPI Schema Generation

## Generation flow

`FastAPI.openapi()` (called lazily on first `/openapi.json` request) calls
`get_openapi()` (`fastapi/openapi/utils.py:514`):

1. Iterates all `app.routes`, filtering for `APIRoute` instances
2. For each route, calls `get_openapi_operation_metadata()` (line 236) for
   tags, summary, description
3. Extracts parameters via `_get_openapi_operation_parameters()` (line 107)
   from the route's flat `Dependant` (path, query, header, cookie params)
4. Extracts request body schema via `get_openapi_operation_request_body()`
   (line 180)
5. Extracts security definitions via `get_openapi_security_definitions()`
   (line 81)
6. Builds response schema from `response_model`
7. Assembles into OpenAPI 3.1.0 spec with `$ref` schema references

## Separate input/output schemas

`separate_input_output_schemas=True` (default) generates distinct schemas when
a Pydantic model's input validation schema differs from its output
serialization schema. For example, a field with `default=None` might be
optional on input but always present on output.

## Schema caching

The generated spec is cached on `self.openapi_schema`. It's only regenerated if
the attribute is cleared (`app.openapi_schema = None`). Routes added after the
first `/openapi.json` request won't appear until the cache is cleared.
