---
title: Jyothisyam Astro API
emoji: 🪐
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 8080
pinned: false
---

# Jyothisyam Astro API

Protected Vedic astrology calculation service powered by Skyfield and the pinned JPL DE440s kernel.

This Space is an API service, not an interactive demo. The public HTTPS endpoint remains protected by the Astro service API key, consumer ID, request ID, durable usage guard, and rate limiting.

## Security

Never commit or print secret values. Configure these only through Hugging Face Space **Secrets**:

- `JYOTHISYAM_API_KEY`
- `JYOTHISYAM_SUPABASE_SERVICE_ROLE_KEY`

Configure non-sensitive runtime settings through Space **Variables** as documented in `docs/HUGGING_FACE_DEPLOYMENT_RUNBOOK.md` in the source repository.

The source repository is public. Space secrets are not part of the repository and must never be copied into this file, the Dockerfile, build arguments, logs, screenshots, or mobile code.

## Status

Hosted availability must not be claimed until the HTTPS readiness check and authenticated durable smoke test both pass against the deployed Space.
