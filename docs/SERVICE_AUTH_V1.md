# Service authentication v1

Jyothisyam protects every `/v1` calculation and classical route with one opaque
bearer key when production authentication is enabled. Process and readiness
probes remain public so the hosting platform can monitor the service.

## Environment

```text
JYOTHISYAM_REQUIRE_API_KEY=true
JYOTHISYAM_API_KEY=<random secret containing at least 32 characters>
```

The production Docker image sets `JYOTHISYAM_REQUIRE_API_KEY=true`. The key must
be supplied by the runtime secret manager. It must never be committed, included
in a mobile build, returned by a health endpoint, or placed in a client-visible
Supabase variable.

Generate an independent key with Python:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Use the same value in exactly two server-side locations:

1. `JYOTHISYAM_API_KEY` on the Python Astro service.
2. `ASTRO_API_KEY` on the Horos Supabase Edge Function.

The Horos mobile app must know only the Supabase Edge Function URL. It must not
receive the Astro service key.

## Request contract

```http
Authorization: Bearer <service-key>
```

Example:

```bash
curl --fail \
  --header "Authorization: Bearer $JYOTHISYAM_API_KEY" \
  --header "Content-Type: application/json" \
  --data @positions-request.json \
  https://astro-api.example.com/v1/positions
```

Authentication responses are stable JSON objects:

```json
{
  "code": "API_KEY_REQUIRED",
  "message": "A bearer API key is required for calculation routes."
}
```

Status codes:

- `401 API_KEY_REQUIRED`: no usable bearer credential was supplied.
- `403 API_KEY_INVALID`: a credential was supplied but did not match.
- `503 API_AUTH_NOT_CONFIGURED`: production requires authentication, but the
  configured key is missing or shorter than 32 characters.

## Public probes

- `GET /health` checks process liveness only.
- `GET /health/ephemeris` verifies the pinned DE440s kernel.
- `GET /health/security` reports non-secret authentication readiness.
- `GET /health/ready` requires both verified ephemeris data and ready service
  authentication.

The Docker health check uses `/health/ready`.

## Docker example

```bash
docker build --tag jyothisyam-api .
docker run --rm --publish 8080:8080 \
  --env JYOTHISYAM_API_KEY="$JYOTHISYAM_API_KEY" \
  jyothisyam-api
```

## Rotation

1. Generate a new independent key.
2. Update `JYOTHISYAM_API_KEY` on the Astro service and redeploy it.
3. Immediately update `ASTRO_API_KEY` on the Horos Edge Function and redeploy it.
4. Confirm `/health/ready` and one authenticated calculation request.
5. Remove the previous value from all secret managers and local shells.

This v1 contract intentionally supports one server-to-server key. Per-client
keys, quotas, billing identity, and cryptographic request signing belong to a
future gateway layer and must not be simulated by the mobile app.
