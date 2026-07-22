# Astro Hugging Face Deployment Runbook

This runbook prepares a free private-beta HTTPS deployment of the protected Astro API on a public Hugging Face Docker Space. It does not authorize deployment by itself.

## Decision

Hugging Face Docker Spaces is the selected no-card private-beta host because it can run the existing Docker/FastAPI service, provides a managed HTTPS endpoint, supports runtime secrets, and offers enough free CPU and memory for the pinned JPL DE440s kernel.

This is a private-beta host, not a production availability commitment. Free hardware can sleep after inactivity and may have a cold start on the first request.

Rejected for this gate:

- Cloudflare Workers Free: the JPL kernel and calculation runtime do not fit the free Worker bundle, memory, and CPU limits.
- Cloudflare Containers: requires the Workers Paid plan.
- Koyeb Free: requires payment-method validation and provides substantially less CPU and memory.
- Render Free: usable as a fallback, but sleeps much sooner and has tighter free-service limits.

## Architecture

```text
Horos Supabase Edge Function
    -> https://<owner>-<space>.hf.space
        -> protected Astro FastAPI container
            -> Skyfield + pinned JPL DE440s
            -> durable usage metering in Supabase project hdaugtypjpniesdgyral
```

The Space is publicly reachable, but protected endpoints remain inaccessible without the Astro API key, a valid consumer UUID, and a unique request ID. The Astro source repository is already public. Secret values remain outside both GitHub and the Space repository.

## Repository preparation gate

Run from a clean Astro checkout:

```powershell
cd C:\Astro

.\.venv\Scripts\python.exe `
  .\scripts\audit_huggingface_deployment_readiness.py
```

Expected ending:

```text
Static Hugging Face deployment readiness: PASS
No network or cloud state was accessed or changed.
```

The audit is static. It does not create a Space, authenticate to Hugging Face, read hosted secrets, contact Supabase, deploy code, or enable billing.

## Space repository layout

Create a new **public Docker Space** only after explicit deployment approval.

The Space repository must contain the tracked Astro application files required by the existing root `Dockerfile`. Replace the Space root `README.md` with:

```text
deploy/huggingface/SPACE_README.md
```

The manifest pins:

```text
sdk: docker
app_port: 8080
```

Do not upload `.env`, `.env.local`, local secret directories, JPL binary files from the workstation, service-account files, signing files, test outputs, or virtual environments. The Docker build downloads DE440s from the pinned source and verifies its SHA-256 checksum.

## Hugging Face Space Secrets

Set these by name only through **Space Settings → Secrets**. Never paste their values into chat, Git, README files, Docker build arguments, screenshots, or logs.

```text
JYOTHISYAM_API_KEY
JYOTHISYAM_SUPABASE_SERVICE_ROLE_KEY
```

Rules:

- Generate a dedicated Astro API key for this hosted deployment; do not reuse a user password.
- Use only the current secret key for Supabase project `hdaugtypjpniesdgyral`.
- Never reuse the revoked legacy service-role JWT.
- The Space runtime injects these as environment variables. The existing Docker entrypoint accepts direct environment values, so `_FILE` variants are not used on Hugging Face.

## Hugging Face Space Variables

Set these non-sensitive values through **Space Settings → Variables**:

```text
APP_ENV=production
PORT=8080
LOG_LEVEL=INFO
JYOTHISYAM_ENABLE_DOCS=false
JYOTHISYAM_ALLOWED_HOSTS=<owner>-<space>.hf.space
JYOTHISYAM_REQUIRE_API_KEY=true
JYOTHISYAM_USAGE_BACKEND=supabase
JYOTHISYAM_REQUIRE_USAGE_GUARD=true
JYOTHISYAM_REQUESTS_PER_MINUTE=60
JYOTHISYAM_MONTHLY_CREDIT_LIMIT=0
JYOTHISYAM_USAGE_RPC_TIMEOUT_SECONDS=10
JYOTHISYAM_SUPABASE_URL=https://hdaugtypjpniesdgyral.supabase.co
JYOTHISYAM_JPL_EPHEMERIS_PATH=/app/app/data/jpl/de440s.bsp
JYOTHISYAM_JPL_EPHEMERIS_SHA256=c1c7feeab882263fc493a9d5a5b2ddd71b54826cdf65d8d17a76126b260a49f2
```

Replace `<owner>-<space>.hf.space` with the exact hostname assigned to the Space. Do not use `*` in production allowed hosts.

## Deployment sequence — paused until explicit approval

1. Create a Hugging Face account without adding paid hardware.
2. Create one public Docker Space on free CPU Basic hardware.
3. Upload only the approved Space repository files.
4. Set the variables above.
5. Set the two secrets above without displaying their values afterward.
6. Wait for the Docker build and startup to complete.
7. Record only the public `https://...hf.space` hostname.
8. Run hosted readiness.
9. Run one authenticated durable staging smoke with a disposable consumer UUID.
10. Configure the Horos Edge Function `ASTRO_API_URL` only after both hosted checks pass.

Steps 1–10 are hosted actions and require explicit approval before execution.

## Hosted acceptance gate

The Space is not approved for Horos until all of these are true:

```text
GET /health/ready -> HTTP 200
ready -> true
usage backend -> supabase
durable -> true
configured -> true
reachable -> true
project ref -> hdaugtypjpniesdgyral
schema version -> api_usage_metering_safety_v1
unauthenticated protected request -> HTTP 401
authenticated request without consumer UUID -> HTTP 400
authenticated durable chart request -> HTTP 200
unique request ID returned and metered
duplicate request ID with changed payload -> HTTP 409
```

Use the existing staging smoke script over HTTPS. Do not use `--allow-http` for the hosted gate.

## Cold-start handling

Free CPU Spaces sleep after prolonged inactivity. Before a scheduled private-beta test:

1. Request `/health/ready` once.
2. Wait until it returns ready.
3. Start the user-flow test only after readiness passes.

Do not run artificial keep-alive traffic solely to bypass the free-tier sleep policy.

## Rollback

If readiness, metering, authentication, or calculations fail:

1. Do not configure Horos to use the Space.
2. Pause the Space or remove public access.
3. Remove or rotate any credential that may have appeared in logs.
4. Restore the last known-good repository commit.
5. Re-run local CI, the private-beta local preflight, and this static deployment audit.
6. Redeploy only after the failure is understood.

No hosted availability claim is allowed until the complete hosted acceptance gate passes.
