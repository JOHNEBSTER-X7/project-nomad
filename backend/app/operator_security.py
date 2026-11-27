"""Minimal fail-closed bearer-token protection for operator-only API routes.
This bootstrap mechanism supports one trusted operator token supplied through
the server environment. It is not a multi-user identity provider.
"""
import hmac
import os
from fastapi import HTTPException, Request, status

def require_operator(request: Request) -> dict:
    configured = os.getenv("NOMAD_OPERATOR_TOKEN", "")
    if len(configured) < 32:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Operator access is not configured. Set a strong server-side NOMAD_OPERATOR_TOKEN.")
    header = request.headers.get("Authorization", "")
    scheme, _, supplied = header.partition(" ")
    if scheme.lower() != "bearer" or not supplied:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Operator authentication required.", headers={"WWW-Authenticate": "Bearer"})
    if not hmac.compare_digest(supplied, configured):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid operator credentials.", headers={"WWW-Authenticate": "Bearer"})
    return {"role": "operator", "authenticated": True}
