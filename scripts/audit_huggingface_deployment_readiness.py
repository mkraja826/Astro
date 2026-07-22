from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PROJECT_REF = "hdaugtypjpniesdgyral"
BLOCKED_PROJECT_REF = "mzjtdcpb" + "voximdukpukd"
EXPECTED_JPL_SHA256 = "c1c7feeab882263fc493a9d5a5b2ddd71b54826cdf65d8d17a76126b260a49f2"

REQUIRED_FILES = (
    ROOT / "Dockerfile",
    ROOT / "deploy" / "docker-entrypoint.sh",
    ROOT / "deploy" / "huggingface" / "SPACE_README.md",
    ROOT / "docs" / "HUGGING_FACE_DEPLOYMENT_RUNBOOK.md",
    ROOT / "scripts" / "download_jpl_kernel.py",
)


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def require_contains(content: str, expected: str, message: str) -> None:
    if expected not in content:
        fail(message)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        relative_path = path.relative_to(ROOT)
        fail(f"Expected UTF-8 text file could not be decoded: {relative_path} ({exc})")


def tracked_status() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail("Unable to read Git working-tree status.")
    return [line for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    print("Astro Hugging Face deployment readiness audit")
    print(f"Repository: {ROOT}")

    for path in REQUIRED_FILES:
        if not path.is_file():
            fail(f"Required file is missing: {path.relative_to(ROOT)}")

    status = tracked_status()
    if status:
        fail(
            "The Astro working tree is not clean. "
            "Commit or stash local changes before auditing."
        )

    dockerfile = read_text(ROOT / "Dockerfile")
    entrypoint = read_text(ROOT / "deploy" / "docker-entrypoint.sh")
    manifest = read_text(ROOT / "deploy" / "huggingface" / "SPACE_README.md")
    runbook = read_text(ROOT / "docs" / "HUGGING_FACE_DEPLOYMENT_RUNBOOK.md")

    require_contains(
        dockerfile,
        "FROM python:3.12-slim",
        "Production Docker base image changed unexpectedly.",
    )
    require_contains(
        dockerfile,
        "PORT=8080",
        "Production Dockerfile no longer defaults to port 8080.",
    )
    require_contains(
        dockerfile,
        "EXPOSE 8080",
        "Production Dockerfile does not expose port 8080.",
    )
    require_contains(
        dockerfile,
        EXPECTED_JPL_SHA256,
        "Pinned JPL DE440s checksum is missing from the Dockerfile.",
    )
    require_contains(
        dockerfile,
        "USER api",
        "Production container must run as a non-root user.",
    )
    require_contains(
        dockerfile,
        'ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]',
        "Production Dockerfile does not use the guarded secret-loading entrypoint.",
    )

    require_contains(
        entrypoint,
        r"direct_value=\${${variable_name}:-}",
        "Entrypoint direct-secret support is missing.",
    )
    require_contains(
        entrypoint,
        "load_secret_file JYOTHISYAM_API_KEY",
        "Astro API key loader is missing.",
    )
    require_contains(
        entrypoint,
        "load_secret_file JYOTHISYAM_SUPABASE_SERVICE_ROLE_KEY",
        "Supabase usage credential loader is missing.",
    )

    require_contains(
        manifest,
        "sdk: docker",
        "Hugging Face manifest must select the Docker SDK.",
    )
    require_contains(
        manifest,
        "app_port: 8080",
        "Hugging Face manifest must expose port 8080.",
    )
    require_contains(
        manifest,
        "JYOTHISYAM_API_KEY",
        "Space secret-name documentation is incomplete.",
    )
    require_contains(
        manifest,
        "JYOTHISYAM_SUPABASE_SERVICE_ROLE_KEY",
        "Space Supabase secret-name documentation is incomplete.",
    )

    required_runbook_values = (
        EXPECTED_PROJECT_REF,
        EXPECTED_JPL_SHA256,
        "APP_ENV=production",
        "PORT=8080",
        "JYOTHISYAM_ENABLE_DOCS=false",
        "JYOTHISYAM_REQUIRE_API_KEY=true",
        "JYOTHISYAM_USAGE_BACKEND=supabase",
        "JYOTHISYAM_REQUIRE_USAGE_GUARD=true",
        "JYOTHISYAM_ALLOWED_HOSTS=<owner>-<space>.hf.space",
        "Steps 1–10 are hosted actions and require explicit approval before execution.",
    )
    for value in required_runbook_values:
        require_contains(
            runbook,
            value,
            f"Deployment runbook is missing required value: {value}",
        )

    deployment_sources = "\n".join((dockerfile, entrypoint, manifest, runbook))
    if BLOCKED_PROJECT_REF in deployment_sources:
        fail("Blocked MDMS project reference exists in Hugging Face deployment material.")

    forbidden_value_markers = (
        "sb_secret_",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.",
        "-----BEGIN PRIVATE KEY-----",
    )
    for marker in forbidden_value_markers:
        if marker in deployment_sources:
            fail(
                "A credential-like value marker exists in Hugging Face "
                "deployment material."
            )

    print("ProjectRef           :", EXPECTED_PROJECT_REF)
    print("SpaceSdk             : docker")
    print("SpacePort            : 8080")
    print("JplSha256            :", EXPECTED_JPL_SHA256)
    print("DirectRuntimeSecrets : supported")
    print("BlockedMdmsRefs      : 0")
    print("CredentialMarkers    : 0")
    print("Static Hugging Face deployment readiness: PASS")
    print("No network or cloud state was accessed or changed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
