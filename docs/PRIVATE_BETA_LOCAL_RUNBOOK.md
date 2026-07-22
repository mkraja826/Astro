# Astro private-beta local runbook

This runbook verifies the protected local Jyothisyam API before any private-beta release work.
It does not deploy the service, enable cloud billing, configure Supabase Edge Function secrets,
or touch any Supabase project other than the Astro project reference
`hdaugtypjpniesdgyral` already bound to the protected local container.

## Proven local architecture

```text
Horos adapter or local client
        |
        v
Protected Astro FastAPI container
        |
        +-- API-key authentication
        +-- consumer UUID requirement
        +-- unique request IDs
        +-- rate limiting
        +-- durable usage metering
        |
        v
Astro Supabase project: hdaugtypjpniesdgyral
```

The astronomical runtime is Skyfield with the locally stored JPL DE440s kernel.
The pinned kernel SHA-256 is:

```text
c1c7feeab882263fc493a9d5a5b2ddd71b54826cdf65d8d17a76126b260a49f2
```

## Requirements

- Windows PowerShell
- repository at `C:\Astro`
- Python virtual environment at `C:\Astro\.venv`
- Docker Desktop running
- existing container named `astro-staging-durable`
- protected local API key file at
  `%LOCALAPPDATA%\Astro\staging-secrets\api_key`
- JPL kernel at `app\data\jpl\de440s.bsp`

The script never prints the API key, Supabase server key, secret-file contents, or container
environment variables.

## Complete verification

From `C:\Astro`:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\scripts\verify-private-beta-local.ps1
```

The complete verification performs these gates:

1. Git working tree is clean.
2. `.env` is ignored and sensitive local files are not tracked.
3. the local Python environment exists.
4. JPL DE440s matches the pinned SHA-256 digest.
5. Ruff passes.
6. the full pytest suite passes.
7. Docker Desktop is reachable.
8. `astro-staging-durable` exists and is running.
9. `/health/ready` confirms:
   - `ready = true`
   - usage backend `supabase`
   - durable and reachable usage
   - project reference `hdaugtypjpniesdgyral`
   - schema `api_usage_metering_safety_v1`
10. the authenticated staging smoke confirms:
    - health and readiness
    - docs disabled
    - unauthenticated requests rejected
    - consumer ID required
    - authenticated metered request accepted
    - unit credit and rate-limit headers present
    - duplicate request ID rejected with `REQUEST_ID_REUSED`

Expected final lines:

```text
Staging smoke checks passed.
Astro private-beta local preflight passed.
This proves the protected local Astro service only; hosted HTTPS deployment remains a separate gate.
```

The authenticated smoke consumes one admitted durable metered request. The duplicate request is
rejected using the same request ID.

## Faster repeat checks

Skip Ruff and pytest while retaining kernel, Docker, readiness, and authenticated smoke checks:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\scripts\verify-private-beta-local.ps1 `
  -SkipTests
```

Skip the durable metered request while retaining local code, kernel, Docker, and readiness checks:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\scripts\verify-private-beta-local.ps1 `
  -SkipMeteredSmoke
```

Use the complete command before merging private-beta readiness changes.

## What this does not prove

A successful local preflight does not prove:

- a public HTTPS Astro endpoint exists;
- hosted infrastructure can reach the Astro Supabase project;
- Horos Edge Function secrets are configured;
- the deployed Horos API can call the hosted Astro service;
- mobile private-beta builds are ready;
- store billing or RevenueCat configuration is complete.

Those remain separate operator-controlled gates. Do not enable billing or deploy hosted resources
without explicit approval.

## Safety boundaries

- Never use the MDMS Supabase project for Astro or Horos work.
- Never place the Supabase server secret in Horos mobile code.
- Never reuse the revoked legacy service-role JWT.
- Never print secret files or inspect container environment variables.
- Never regenerate golden baselines simply to hide a regression.
