# JPL planetary ephemeris data

The Skyfield calculation profile expects a local JPL DE440s SPK kernel at:

```text
app/data/jpl/de440s.bsp
```

The API never downloads this file automatically. Download the official kernel from:

```text
https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force app/data/jpl
Invoke-WebRequest `
  -Uri "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp" `
  -OutFile "app/data/jpl/de440s.bsp"
```

Or set an absolute path:

```powershell
$env:JYOTHISYAM_JPL_EPHEMERIS_PATH = "C:\ephemeris\de440s.bsp"
```

Check readiness at:

```text
GET /health/ephemeris/jpl
```

The `.bsp` file is intentionally ignored by Git. Deployment must copy or mount it separately.
