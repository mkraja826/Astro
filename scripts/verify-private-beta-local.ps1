[CmdletBinding()]
param(
    [switch]$SkipTests,
    [switch]$SkipMeteredSmoke
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Assert-ExitCode {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    if ($LASTEXITCODE -ne 0) {
        throw $Message
    }
}

function Test-DockerReady {
    $previousPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        docker info *> $null
        return $LASTEXITCODE -eq 0
    }
    finally {
        $ErrorActionPreference = $previousPreference
    }
}

$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot

try {
    Write-Host "Astro private-beta local preflight"
    Write-Host "Repository: $repoRoot"

    git rev-parse --is-inside-work-tree *> $null
    Assert-ExitCode "This script must be run from the Astro Git repository."

    $status = @(git status --porcelain)
    Assert-ExitCode "Unable to read Git working-tree status."
    if ($status.Count -gt 0) {
        throw "The Astro working tree is not clean. Commit or stash local changes before verification."
    }

    $branch = (git branch --show-current).Trim()
    Assert-ExitCode "Unable to determine the current Git branch."
    $head = (git rev-parse --short HEAD).Trim()
    Assert-ExitCode "Unable to determine the current Git commit."

    git check-ignore -q .env
    if ($LASTEXITCODE -ne 0) {
        throw "Astro .env is not protected by Git ignore rules."
    }

    $trackedSensitive = @(
        git ls-files -- ".env" ".env.local" "*.jks" "*.keystore" "*.p8" "*.p12" "google-service-account.json"
    )
    Assert-ExitCode "Unable to verify tracked sensitive files."
    if ($trackedSensitive.Count -gt 0) {
        throw "Sensitive local files are tracked by Git: $($trackedSensitive -join ', ')"
    }

    $python = Join-Path $repoRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path $python -PathType Leaf)) {
        throw "The Astro Python environment is missing at .venv\Scripts\python.exe. Recreate the local environment first."
    }

    $kernelPath = Join-Path $repoRoot "app\data\jpl\de440s.bsp"
    $expectedKernelSha256 = "c1c7feeab882263fc493a9d5a5b2ddd71b54826cdf65d8d17a76126b260a49f2"
    if (-not (Test-Path $kernelPath -PathType Leaf)) {
        throw "The verified JPL DE440s kernel is missing."
    }

    $kernelSha256 = (Get-FileHash -Algorithm SHA256 $kernelPath).Hash.ToLowerInvariant()
    if ($kernelSha256 -ne $expectedKernelSha256) {
        throw "The JPL DE440s kernel checksum does not match the pinned production checksum."
    }

    if (-not $SkipTests) {
        Write-Host "Running Ruff..."
        & $python -m ruff check .
        Assert-ExitCode "Ruff checks failed."

        Write-Host "Running the Astro test suite..."
        & $python -m pytest -q
        Assert-ExitCode "Astro tests failed."
    }
    else {
        Write-Host "Ruff and pytest skipped by request."
    }

    if (-not (Test-DockerReady)) {
        throw "Docker Desktop is not ready. Open Docker Desktop and rerun this script."
    }

    $containerName = "astro-staging-durable"
    $container = (
        docker ps -a --filter "name=^${containerName}$" --format "{{.Names}}"
    ).Trim()
    Assert-ExitCode "Unable to inspect the protected Astro staging container."
    if ($container -ne $containerName) {
        throw "The $containerName container is missing. Recreate it from the protected staging setup."
    }

    $running = (
        docker inspect --format "{{.State.Running}}" $containerName
    ).Trim()
    Assert-ExitCode "Unable to inspect the Astro container state."
    if ($running -ne "true") {
        docker start $containerName *> $null
        Assert-ExitCode "Unable to start the Astro staging container."
    }

    Write-Host "Waiting for protected Astro readiness..."
    $health = $null
    for ($attempt = 1; $attempt -le 30; $attempt++) {
        Start-Sleep -Seconds 2
        try {
            $health = Invoke-RestMethod `
                -Uri "http://127.0.0.1:8080/health/ready" `
                -TimeoutSec 5

            if (
                $health.ready -eq $true -and
                $health.usage.ready -eq $true -and
                $health.usage.backend -eq "supabase" -and
                $health.usage.durable -eq $true -and
                $health.usage.reachable -eq $true -and
                $health.usage.project_ref -eq "hdaugtypjpniesdgyral" -and
                $health.usage.schema_version -eq "api_usage_metering_safety_v1"
            ) {
                break
            }
        }
        catch {
            $health = $null
        }
    }

    if (
        -not $health -or
        $health.ready -ne $true -or
        $health.usage.ready -ne $true -or
        $health.usage.backend -ne "supabase" -or
        $health.usage.durable -ne $true -or
        $health.usage.reachable -ne $true -or
        $health.usage.project_ref -ne "hdaugtypjpniesdgyral" -or
        $health.usage.schema_version -ne "api_usage_metering_safety_v1"
    ) {
        throw "Protected Astro staging did not pass the durable readiness gate."
    }

    [pscustomobject]@{
        AstroBranch  = $branch
        AstroHead    = $head
        KernelSha256 = $kernelSha256
        Ready        = $health.ready
        Backend      = $health.usage.backend
        Durable      = $health.usage.durable
        Reachable    = $health.usage.reachable
        ProjectRef   = $health.usage.project_ref
        Schema       = $health.usage.schema_version
    } | Format-List

    if ($SkipMeteredSmoke) {
        Write-Host "Authenticated metered smoke skipped by request."
    }
    else {
        $apiKeyPath = Join-Path $env:LOCALAPPDATA "Astro\staging-secrets\api_key"
        if (-not (Test-Path $apiKeyPath -PathType Leaf)) {
            throw "The protected local Astro API key file is missing."
        }

        $apiKey = (Get-Content $apiKeyPath -Raw).Trim()
        if ($apiKey.Length -lt 32) {
            throw "The protected local Astro API key file is invalid."
        }

        $env:ASTRO_STAGING_API_KEY = $apiKey
        $env:ASTRO_STAGING_CONSUMER_ID = [guid]::NewGuid().ToString()

        try {
            Write-Host "Running authenticated durable staging smoke..."
            & $python scripts\staging_smoke.py `
                --base-url http://127.0.0.1:8080 `
                --allow-http
            Assert-ExitCode "Authenticated durable staging smoke failed."
        }
        finally {
            Remove-Item Env:ASTRO_STAGING_API_KEY -ErrorAction SilentlyContinue
            Remove-Item Env:ASTRO_STAGING_CONSUMER_ID -ErrorAction SilentlyContinue
            $apiKey = $null
        }
    }

    Write-Host "Astro private-beta local preflight passed."
    Write-Host "This proves the protected local Astro service only; hosted HTTPS deployment remains a separate gate."
}
finally {
    Pop-Location
}
