# Staging deployment v1

This runbook deploys the validated Jyothisyam API as a private staging service. It does not change calculation formulas, validation evidence, or the Horos production path.

## Scope

Staging must prove all of the following before Horos is connected:

- the immutable container starts with the verified DE440s kernel,
- `/health/ready` verifies JPL integrity, service authentication, runtime guards, and live Astro metering connectivity,
- durable metering is bound only to Astro project `hdaugtypjpniesdgyral`,
- interactive documentation remains disabled,
- unauthenticated and malformed requests fail safely,
- a real authenticated request is metered once,
- reusing a request ID returns HTTP 409,
- rollback to the previous image or revision is documented and tested.

## Required secrets

Create these only in the deployment platform's secret store:

- `JYOTHISYAM_API_KEY`: independently generated opaque service key, at least 32 characters.
- `JYOTHISYAM_SUPABASE_SERVICE_ROLE_KEY`: service-role key for Astro project `hdaugtypjpniesdgyral` only.

Never place either value in Git, shell history, screenshots, Horos, browser code, mobile builds, or health responses.

## Non-secret configuration

Start from `deploy/staging.env.example` and replace `JYOTHISYAM_ALLOWED_HOSTS` with the exact assigned staging hostname. Do not use wildcards. Keep `JYOTHISYAM_CORS_ORIGINS` empty until a browser origin is explicitly approved.

Mandatory staging values:

```text
APP_ENV=staging
JYOTHISYAM_ENABLE_DOCS=false
JYOTHISYAM_REQUIRE_API_KEY=true
JYOTHISYAM_USAGE_BACKEND=supabase
JYOTHISYAM_REQUIRE_USAGE_GUARD=true
JYOTHISYAM_SUPABASE_URL=https://hdaugtypjpniesdgyral.supabase.co
```

## Database prerequisite

Before deploying the new image, apply and verify:

```text
supabase/migrations/20260721173000_api_usage_health_v1.sql
```

The migration is additive and non-mutating. It creates only the service-role function `public.api_usage_health_v1()` and grants no client access.

## Preflight

Load the staging environment and secrets into the current shell without printing them, then run:

```powershell
.\.venv\Scripts\python.exe scripts\validate_staging_env.py
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest -q
```

Expected result: configuration valid, Ruff passed, and the full test suite passed.

Build the exact candidate image and record its digest:

```powershell
docker build --tag jyothisyam-api:staging-candidate .
docker image inspect jyothisyam-api:staging-candidate --format '{{json .RepoDigests}}'
```

Deploy by immutable image digest rather than a mutable `latest` tag. Keep the previous healthy image digest or platform revision available for rollback.

## Platform requirements

The selected container platform must provide:

- HTTPS termination,
- private or authenticated ingress during staging,
- secret references rather than plaintext environment values,
- port `8080`,
- at least one warm instance during verification,
- a request timeout greater than the API's 30-second internal timeout,
- startup/readiness probing against `/health/ready`,
- liveness probing against `/health`,
- retained logs without request bodies or birth data,
- revision or image-digest rollback.

Cloud Run is compatible with the container, but the cloud project, region, service account, ingress mode, and final hostname must be selected before provider-specific deployment files are committed.

## Post-deployment smoke test

Set these locally without committing them:

```text
ASTRO_STAGING_BASE_URL=https://<exact-staging-host>
ASTRO_STAGING_API_KEY=<same staging service key>
ASTRO_STAGING_CONSUMER_ID=<dedicated staging Supabase user UUID>
```

Run:

```powershell
.\.venv\Scripts\python.exe scripts\staging_smoke.py
```

The script verifies liveness, full readiness, live Astro RPC connectivity, disabled docs, authentication, consumer identity, metering headers, one successful unit charge, and HTTP 409 on duplicate request IDs. It never prints either secret.

## Acceptance gate

Staging is accepted only when:

- `/health` returns HTTP 200,
- `/health/ready` returns HTTP 200 and `ready: true`,
- `usage.reachable` is `true`,
- `usage.project_ref` is `hdaugtypjpniesdgyral`,
- `usage.schema_version` is `api_usage_metering_safety_v1`,
- `/docs` and `/openapi.json` return HTTP 404,
- unauthenticated calculation requests return HTTP 401,
- authenticated requests without a consumer UUID return HTTP 400,
- a valid request returns HTTP 200 with rate-limit and credit headers,
- the same request ID returns HTTP 409,
- no service-role secret appears in logs or responses.

## Rollback

Rollback is image/revision based; the three usage migrations are additive and should normally remain installed.

1. Stop new traffic to the failing staging revision.
2. Route staging traffic back to the last verified image digest or revision.
3. Confirm `/health` and `/health/ready` on the restored revision.
4. Disable the failing revision.
5. Rotate `JYOTHISYAM_API_KEY` only if exposure is suspected.
6. Rotate the Astro service-role key only if exposure is suspected, then update the secret reference and re-run readiness.
7. Preserve logs, request IDs, image digest, and deployment metadata for review.

Do not point rollback or recovery commands at MDMS.
