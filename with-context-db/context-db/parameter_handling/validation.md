---
description: How extracted params are validated through Pydantic — ModelField creation, TypeAdapter usage, and the 422 error format
---

# Parameter Validation

## Validation pipeline

1. Raw values extracted from request by `request_params_to_args()`
   (`fastapi/dependencies/utils.py:784`) for path/query/header/cookie and
   `request_body_to_args()` (line 951) for body
2. Each value validated via `_validate_value_with_model_field()` (line 738)
   which calls Pydantic's `field.validate()`
3. Validation errors collected (not raised immediately — all params validated
   first)
4. If any errors: `RequestValidationError` raised with full error list → 422
   response

## ModelField and TypeAdapter

Each parameter gets a `ModelField` created by `create_model_field()`
(`fastapi/utils.py:58`). This wraps Pydantic v2's `TypeAdapter` for type
coercion and validation.

The `TypeAdapter` handles complex types: `List[int]`, `Optional[str]`, nested
models, union types, constrained types (`gt=0`, `max_length=50`).

## Error format

422 responses follow this structure:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["query", "name"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

The `loc` field shows the parameter location and name, making it clear which
param failed and where it was expected (path, query, body, header, cookie).
