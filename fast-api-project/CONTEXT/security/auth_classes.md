---
description: Concrete security classes — OAuth2PasswordBearer, HTTPBearer, HTTPBasic, APIKey variants and how they extract credentials from requests
---

# Security Auth Classes

All security classes inherit from `SecurityBase` and are used as dependencies.
Each extracts credentials from a specific location in the request.

## OAuth2

- `OAuth2PasswordBearer(tokenUrl="/token")` — extracts Bearer token from
  `Authorization` header. The `tokenUrl` is only used for OpenAPI docs (the
  "Authorize" button). Returns the raw token string.
- `OAuth2PasswordRequestForm` — a dependency that parses `application/x-www-form-urlencoded`
  body with `username`, `password`, `scope`, `grant_type` fields. Used on the
  token endpoint itself.
- `OAuth2PasswordRequestFormStrict` — same but enforces `grant_type="password"` per spec.

## HTTP Auth

- `HTTPBearer()` — extracts Bearer token, returns `HTTPAuthorizationCredentials(scheme, credentials)`
- `HTTPBasic()` — extracts Basic auth, returns `HTTPBasicCredentials(username, password)`

## API Key

- `APIKeyHeader(name="X-API-Key")` — reads from request header
- `APIKeyCookie(name="session")` — reads from cookie
- `APIKeyQuery(name="api_key")` — reads from query parameter

All return the raw key string. All accept `auto_error=True` (default) which raises
401 if the credential is missing. Set to `False` to allow optional auth.

## Files

- `security/oauth2.py` — OAuth2 classes
- `security/http.py` — HTTPBearer, HTTPBasic
- `security/api_key.py` — APIKey variants
- `security/base.py` — `SecurityBase` base class
