# Operator Access Control — V0.5

## Purpose
V0.5 adds a minimal authentication gate for the read-only operator status endpoint. The bootstrap uses one server-side bearer token configured by the site operator.

## Configuration
Set `NOMAD_OPERATOR_TOKEN` in the private environment of the NOMAD API. Use a cryptographically random value of at least 32 characters (for example, generate 32 random bytes encoded as hexadecimal). Never commit the secret or expose it in client-side build variables.

If the token is absent or shorter than 32 characters, the protected endpoint returns HTTP 503 and fails closed. Requests without a valid Bearer token receive HTTP 401. Comparison uses a constant-time comparison function.

## Protected endpoint
`GET /api/operator/status` requires `Authorization: Bearer <token>`. It returns the operator role and coarse service/network status only. It does not return the configured secret or provide privileged network changes.

The browser demonstration keeps the entered token in component memory only. It does not write it to localStorage, sessionStorage, cookies or URLs. A page reload clears the token. Use HTTPS whenever traffic crosses a network that is not physically trusted; a private LAN is not automatically secure.

## Current limitations
This is a bootstrap gate for one trusted operator, not a complete identity and access-management system. It does not provide individual accounts, MFA, password recovery, rotation/revocation workflows, granular permissions, audit logging, rate limiting, lockout controls or central identity integration. The token is a shared secret; anyone who obtains it can act as the operator for this endpoint.

The endpoint is read-only. Do not add network-changing actions under this mechanism without a separate threat model, audit trail, confirmation workflow and least-privilege design.

## Required before school/community deployment
1. Define named operator accounts and lifecycle (provisioning, rotation, revocation).
2. Adopt a reviewed identity provider or vetted authentication library.
3. Add MFA for privileged access where feasible.
4. Add role/permission boundaries for administrators, educators, maintainers and learners.
5. Add tamper-evident audit events without recording secrets or learner content.
6. Add rate limiting, monitoring and secure session/token handling.
7. Perform independent security review and site-specific privacy/safeguarding review.
8. Verify TLS and network segmentation on actual deployment hardware.

No production-grade identity service or school-ready access control is claimed.