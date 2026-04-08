---
description: How OAuth2 scopes propagate up the dependency tree and appear in OpenAPI — the Security() vs Depends() distinction
---

# Security Scope Propagation

## Security() vs Depends()

`Security(dependency, scopes=["read", "write"])` is `Depends()` with an
additional `scopes` parameter. It marks the dependency as a security scheme and
attaches OAuth2 scopes.

## Scope propagation

Scopes flow **up** the dependency tree. When `get_flat_dependant()`
(`fastapi/dependencies/utils.py:138`) flattens the tree, it merges
`own_oauth_scopes` from each level. A parent endpoint that uses
`Security(get_current_user, scopes=["admin"])` and `get_current_user` itself
uses `Security(oauth2_scheme)` — the final security requirement includes both
scopes.

## SecurityScopes injection

A dependency can receive a `SecurityScopes` object
(`fastapi/security/oauth2.py:653`) that lists all scopes required by its
dependants:

```python
async def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
    # security_scopes.scopes contains scopes from all callers
```

This enables a single auth dependency to enforce different scopes depending on
which endpoint calls it.

## OpenAPI integration

`get_openapi_security_definitions()` (`fastapi/openapi/utils.py:81`) walks the
flat dependency tree, finds all `SecurityBase` instances, and builds the
`securitySchemes` component and per-operation `security` requirements in the
OpenAPI spec.
