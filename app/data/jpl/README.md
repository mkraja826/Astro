# JPL planetary ephemeris data

The Skyfield calculation profile expects a local JPL DE440s SPK kernel at:

```text
app/data/jpl/de440s.bsp
```

The pinned production kernel identity is:

```text
File: de440s.bsp
Size: 32726016 bytes
SHA-256: c1c7feeab882263fc493a9d5a5b2ddd71b54826cdf65d8d17a76126b260a49f2
```

The API never downloads this file at runtime. Docker and CI use the repository build helper to download the official JPL file and reject it unless the digest matches:

```powershell
python scripts/download_jpl_kernel.py `
  --destination app/data/jpl/de440s.bsp
```

Official source:

```text
https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp
```

To use an absolute path, set both the path and the expected digest:

```powershell
$env:JYOTHISYAM_JPL_EPHEMERIS_PATH = "C:\ephemeris\de440s.bsp"
$env:JYOTHISYAM_JPL_EPHEMERIS_SHA256 = "c1c7feeab882263fc493a9d5a5b2ddd71b54826cdf65d8d17a76126b260a49f2"
```

Check process health and verified ephemeris readiness at:

```text
GET /health
GET /health/ephemeris
```

The `.bsp` file is intentionally ignored by Git. Production images must install it through the verified build helper or mount an identically hashed copy.
