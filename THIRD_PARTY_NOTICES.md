# Third-party components

## Skyfield

Skyfield is the astronomical calculation library used by the production
`south_indian_drik_lahiri_jpl_de440s_v1` profile.

Project: `https://github.com/skyfielders/python-skyfield`

License: MIT. Preserve the upstream copyright and license notice when
redistributing Skyfield.

## NumPy

NumPy is used for vector and matrix operations in the JPL provider.

Project: `https://numpy.org/`

License: BSD 3-Clause. Preserve the upstream copyright and license notice when
redistributing NumPy.

## JPL DE440s SPK kernel

The service reads the unmodified `de440s.bsp` planetary ephemeris from NASA/JPL
NAIF. The kernel is not committed to this repository and is never automatically
downloaded by an application request.

Official directory:
`https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/`

Review NASA/JPL and NAIF distribution notices before redistributing the kernel in
a packaged product. A deployment may instead mount the official file separately.
