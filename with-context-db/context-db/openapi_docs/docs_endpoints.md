---
description: How /docs, /redoc, and /openapi.json endpoints are wired up — auto-registration in FastAPI.__init__ and the OAuth2 redirect handler
---

# Docs Endpoints

## Auto-registration

`FastAPI.__init__()` (`fastapi/applications.py:41`) sets up docs routes based
on constructor params:

- `docs_url="/docs"` → Swagger UI (set to `None` to disable)
- `redoc_url="/redoc"` → ReDoc (set to `None` to disable)
- `openapi_url="/openapi.json"` → OpenAPI JSON spec (set to `None` to disable
  all docs)

These are added via `self.setup()` which calls `self.add_route()` for each.

## Swagger UI serving

`get_swagger_ui_html()` (`fastapi/openapi/docs.py:40`) generates a
self-contained HTML page that loads Swagger UI from CDN (configurable) and
points it at the OpenAPI JSON URL.

Supports custom configuration via `swagger_ui_parameters` dict and OAuth2 init
via `swagger_ui_init_oauth`. Uses `_html_safe_json()` (line 9) to prevent XSS
when injecting config.

## OAuth2 redirect

`/docs/oauth2-redirect` serves the OAuth2 callback HTML needed for the
"Authorize" button in Swagger UI. Handled by
`get_swagger_ui_oauth2_redirect_html()` (`fastapi/openapi/docs.py:301`). This
endpoint is registered automatically when `docs_url` is set.
