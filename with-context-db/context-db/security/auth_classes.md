---
description: Concrete security classes — OAuth2PasswordBearer, HTTPBearer, HTTPBasic, APIKey variants and how they extract credentials from requests
---

# Security Auth Classes

All security classes inherit from `SecurityBase`
(`fastapi/security/base.py:4`) and are used as dependencies. Each extracts
credentials from a specific location in the request.

## OAuth2 — `fastapi/security/oauth2.py`

- `OAuth2PasswordBearer` (line 433) — extracts Bearer token from
  `Authorization` header. The `tokenUrl` is only used for OpenAPI docs (the
  "Authorize" button). Returns the raw token string.
- `OAuth2AuthorizationCodeBearer` (line 547) — authorization code flow variant.
- `OAuth2PasswordRequestForm` (line 14) — a dependency that parses
  `application/x-www-form-urlencoded` body with `username`, `password`,
  `scope`, `grant_type` fields.
- `OAuth2PasswordRequestFormStrict` (line 162) — same but enforces
  `grant_type="password"` per spec.
- `SecurityScopes` (line 653) — injectable object listing required scopes.

## HTTP Auth — `fastapi/security/http.py`

- `HTTPBearer` (line 222) — extracts Bearer token, returns
  `HTTPAuthorizationCredentials(scheme, credentials)`
- `HTTPBasic` (line 105) — extracts Basic auth, returns
  `HTTPBasicCredentials(username, password)`

## API Key — `fastapi/security/api_key.py`

- `APIKeyHeader` (line 147) — reads from request header
- `APIKeyCookie` (line 235) — reads from cookie
- `APIKeyQuery` (line 55) — reads from query parameter

All return the raw key string. All accept `auto_error=True` (default) which
raises 401 if the credential is missing. Set to `False` for optional auth.
