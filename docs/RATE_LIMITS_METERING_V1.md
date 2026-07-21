# Rate limits and usage metering v1

This package adds authenticated, per-consumer request admission and usage recording around the existing calculation routes. It does not change any astronomical or Jyothisyam calculation.

## Trust boundary

The Horos mobile client must never call the Python API with the service key. The Supabase Edge Function:

1. verifies the user's Supabase JWT,
2. sends the server-only `JYOTHISYAM_API_KEY`,
3. sends the authenticated user UUID in `X-Astro-Consumer-ID`, and
4. forwards or creates a unique `X-Request-ID`.

The Python API validates the bearer service key before trusting the consumer UUID.

## Backends

- `memory`: deterministic local and test backend. It is process-local and is not accepted as durable when usage enforcement is required in staging or production.
- `supabase`: shared durable backend using two security-definer Postgres RPCs.
- `disabled`: permitted only when usage enforcement is not required.

The production Docker image defaults to `supabase` and requires usage readiness. A deployment without the Astro project URL and service-role key remains unready.

## Policy

Version 1 uses one credit for every admitted calculation request. Endpoint-specific billing weights are intentionally deferred until commercial plans are approved.

- default rate: 60 requests per minute per consumer
- default monthly credit limit: 0, meaning usage is recorded without enforcing a monthly ceiling
- response statuses 200–399 consume the reserved credit
- response statuses 400–599 release the reserved credit
- request IDs are idempotent and cannot be charged twice
- rate-limit rejections return HTTP 429 and `Retry-After`

## Response headers

Successful admitted calculation responses include:

- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-Astro-Credit-Cost`
- `X-Request-ID`

## Database migration

The migration is:

`supabase/migrations/20260721161000_api_usage_metering_v1.sql`

It creates only these Astro-project objects:

- `public.api_rate_limit_windows`
- `public.api_usage_monthly`
- `public.api_usage_events`
- `public.api_usage_admit_v1(...)`
- `public.api_usage_finalize_v1(...)`

All three tables have RLS enabled. `anon` and `authenticated` receive no direct access. Only `service_role` may execute the RPCs.

The migration must not be applied to MDMS.

## Required staging and production secrets

```text
JYOTHISYAM_USAGE_BACKEND=supabase
JYOTHISYAM_REQUIRE_USAGE_GUARD=true
JYOTHISYAM_SUPABASE_URL=https://<astro-project-ref>.supabase.co
JYOTHISYAM_SUPABASE_SERVICE_ROLE_KEY=<server-only-secret>
```

The service-role key belongs only in the Python API deployment secret store. It must never be committed, logged, returned by a health endpoint, or bundled into Horos.

## Readiness

`GET /health/usage` reports only non-secret policy state. `GET /health/ready` requires usage readiness alongside JPL integrity, service authentication, and runtime guardrails.

## Deployment sequence

1. pass Ruff, full tests, and Docker smoke checks,
2. review the SQL migration,
3. apply it only to the Astro Supabase project,
4. run SQL admission/finalization verification,
5. configure deployment secrets,
6. deploy staging,
7. update the Horos Edge Function to send the authenticated user UUID,
8. confirm shared limits across more than one API instance.
