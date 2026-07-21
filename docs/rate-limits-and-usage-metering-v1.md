# Rate limits and usage metering v1

This package adds authenticated, per-consumer request admission and usage recording around the existing calculation routes. It does not change any astronomical or Jyothisyam calculation.

## Trust boundary

The Horos mobile client must never call the Python API with the service key. The Supabase Edge Function:

1. verifies the user's Supabase JWT,
2. sends the server-only `JYOTHISYAM_API_KEY`,
3. sends the authenticated user UUID in `X-Astro-Consumer-ID`, and
4. creates a globally unique `X-Request-ID` for every calculation attempt.

The Python API validates the bearer service key before trusting the consumer UUID.

## Astro project binding

Durable metering is hard-bound to Astro project `hdaugtypjpniesdgyral`. Only these dedicated variables are read:

```text
JYOTHISYAM_SUPABASE_URL=https://hdaugtypjpniesdgyral.supabase.co
JYOTHISYAM_SUPABASE_SERVICE_ROLE_KEY=<server-only-secret>
```

Generic `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` variables are deliberately ignored so an unrelated project such as MDMS cannot be selected accidentally. A different Supabase hostname leaves `/health/usage` unready and calculation routes fail closed.

## Backends

- `memory`: deterministic opt-in local and test backend. It is process-local and is not accepted as durable when usage enforcement is required in staging or production.
- `supabase`: shared durable backend using two security-definer Postgres RPCs.
- `disabled`: the default for existing development/test workflows and permitted only when usage enforcement is not required.

Staging and production default to `supabase` and require usage readiness. A deployment without the exact Astro project URL and service-role key remains unready.

## Policy

Version 1 uses one credit for every admitted calculation request. Endpoint-specific billing weights are intentionally deferred until commercial plans are approved.

- default rate: 60 requests per minute per consumer
- default monthly credit limit: 0, meaning usage is recorded without enforcing a monthly ceiling
- response statuses 200–399 consume the reserved credit
- response statuses 400–599 release the reserved credit
- each request ID can be admitted only once
- reused request IDs return HTTP 409 and must be replaced with a new ID
- rate-limit and quota rejections return HTTP 429 and `Retry-After`

Rejecting request-ID reuse prevents duplicate execution, cross-consumer collisions, and free successful retries after a failed calculation. Response replay caching is not part of v1.

## Response headers

Successful admitted calculation responses include:

- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-Astro-Credit-Cost`
- `X-Request-ID`

## Database migrations

Apply these migrations in order:

1. `supabase/migrations/20260721161000_api_usage_metering_v1.sql`
2. `supabase/migrations/20260721170000_api_usage_metering_safety_v1.sql`

They create or update only these Astro-project objects:

- `public.api_rate_limit_windows`
- `public.api_usage_monthly`
- `public.api_usage_events`
- `public.api_usage_admit_v1(...)`
- `public.api_usage_finalize_v1(...)`

All three tables have RLS enabled. `anon` and `authenticated` receive no direct access. Only `service_role` may execute the RPCs. The safety migration serializes global request-ID admission and enforces quota checks for the first monthly row.

The migrations must never be applied to MDMS.

## Required staging and production secrets

```text
JYOTHISYAM_USAGE_BACKEND=supabase
JYOTHISYAM_REQUIRE_USAGE_GUARD=true
JYOTHISYAM_SUPABASE_URL=https://hdaugtypjpniesdgyral.supabase.co
JYOTHISYAM_SUPABASE_SERVICE_ROLE_KEY=<server-only-secret>
```

The service-role key belongs only in the Python API deployment secret store. It must never be committed, logged, returned by a health endpoint, or bundled into Horos.

## Readiness

`GET /health/usage` reports only non-secret policy state. `GET /health/ready` requires usage readiness alongside JPL integrity, service authentication, and runtime guardrails.

## Deployment sequence

1. pass Ruff, full tests, and Docker smoke checks,
2. review both SQL migrations,
3. apply them only to Astro project `hdaugtypjpniesdgyral`,
4. run SQL admission, duplicate-ID, quota, and finalization verification,
5. configure deployment secrets,
6. deploy staging,
7. update the Horos Edge Function to send the authenticated user UUID and a unique request ID,
8. confirm shared limits across more than one API instance.
