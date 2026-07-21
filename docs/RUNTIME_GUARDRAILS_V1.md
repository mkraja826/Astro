# Runtime guardrails v1

This document defines the first production runtime policy around the deterministic Jyothisyam calculation engine. It does not change any astronomical or Jyotisha calculation.

## Environment

- `APP_ENV`: `development`, `test`, `staging`, or `production`.
- `LOG_LEVEL`: `CRITICAL`, `ERROR`, `WARNING`, `INFO`, or `DEBUG`.
- `JYOTHISYAM_ALLOWED_HOSTS`: comma-separated exact hostnames accepted by `TrustedHostMiddleware`. Wildcards are rejected.
- `JYOTHISYAM_CORS_ORIGINS`: optional comma-separated exact `http://` or `https://` browser origins. Empty means browser CORS is disabled.
- `JYOTHISYAM_MAX_REQUEST_BODY_BYTES`: positive request body limit. Default: `1048576` bytes.
- `JYOTHISYAM_REQUEST_TIMEOUT_SECONDS`: positive end-to-end request timeout. Default: `30` seconds.
- `JYOTHISYAM_ENABLE_DOCS`: controls Swagger, ReDoc, and OpenAPI routes outside production. It must be false in production.

The production Docker image sets `APP_ENV=production`, requires service authentication, disables interactive documentation, accepts only local health-probe hosts by default, and leaves CORS disabled. Deployment must override `JYOTHISYAM_ALLOWED_HOSTS` with the exact staging or production API hostname.

## Request identity

Every HTTP response contains:

```text
X-Request-ID: <opaque identifier>
X-Content-Type-Options: nosniff
```

A caller-supplied `X-Request-ID` is retained only when it contains 1–64 ASCII letters, digits, `.`, `_`, `:`, or `-`. Otherwise the server generates a new identifier. Error responses include the same identifier in their JSON body.

## Access logs

The `jyothisyam.access` logger emits one JSON object per request with only:

- request ID
- method
- route path
- response status
- duration
- number of request-body bytes consumed

It does not log query strings, request bodies, birth details, authorization headers, API keys, or response bodies.

## Rejections

- malformed `Content-Length`: HTTP `400`, code `INVALID_CONTENT_LENGTH`
- body larger than the configured limit: HTTP `413`, code `REQUEST_BODY_TOO_LARGE`
- processing timeout: HTTP `504`, code `REQUEST_TIMEOUT`
- unexpected application failure: HTTP `500`, code `INTERNAL_SERVER_ERROR`

Unexpected failures return a generic message and correlation ID. Internal exception details remain server-side.

## Public health routes

- `/health`: process liveness
- `/health/ephemeris`: pinned JPL integrity
- `/health/security`: service-authentication readiness
- `/health/runtime`: non-secret runtime policy
- `/health/ready`: combined production readiness

All `/v1` calculation and validation routes remain protected by the Horos service bearer key in production.

## CORS policy

CORS is not required for the intended Supabase Edge Function to Python API connection because that is server-to-server traffic. Configure browser origins only when a reviewed web client directly calls this API. Wildcard origins are intentionally unsupported.
