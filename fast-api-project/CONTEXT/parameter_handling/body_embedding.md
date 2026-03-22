---
description: When and why multiple body params get wrapped in a synthetic model — the embed logic that surprises people
---

# Body Field Embedding

When an endpoint has body parameters, FastAPI decides whether to wrap them:

## Rules

- **Single body param, Pydantic model, no `embed=True`** → request body IS the model
  (e.g., `{"name": "foo", "price": 10}`)
- **Multiple body params** → wrapped in an object with param names as keys
  (e.g., `{"item": {"name": "foo"}, "user": {"name": "bar"}}`)
- **Single body param with `Body(embed=True)`** → wrapped like multiple params
  (e.g., `{"item": {"name": "foo"}}`)

This is implemented in `_should_embed_body_fields()` in `dependencies/utils.py`.

## Why this matters

This is one of the most common sources of confusion. A developer adds a second body
parameter and the entire request body schema changes shape — what was flat becomes
nested. The OpenAPI docs update automatically, but clients break.

## Form field extraction

Special case: if there's a single body param that's a Pydantic model and the param
is annotated with `Form()`, FastAPI extracts the model's fields as individual form
fields rather than expecting a JSON body. This allows Pydantic models to work with
HTML forms.
