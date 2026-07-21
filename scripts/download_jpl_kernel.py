"""Download the pinned JPL DE440s kernel and verify its SHA-256 digest."""

from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
from urllib.request import Request, urlopen

DEFAULT_URL = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp"
DEFAULT_SHA256 = "c1c7feeab882263fc493a9d5a5b2ddd71b54826cdf65d8d17a76126b260a49f2"
CHUNK_SIZE = 1024 * 1024


def file_sha256(path: Path) -> str:
    """Return the lowercase SHA-256 digest of a local file."""

    digest = sha256()
    with path.open("rb") as source:
        while chunk := source.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_sha256(value: str) -> str:
    normalized = value.strip().lower()
    if len(normalized) != 64 or any(character not in "0123456789abcdef" for character in normalized):
        raise ValueError("expected SHA-256 must contain exactly 64 hexadecimal characters")
    return normalized


def download_kernel(destination: Path, url: str, expected_sha256: str) -> None:
    """Download a kernel to an atomic temporary file and verify it before install."""

    expected = _validate_sha256(expected_sha256)
    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.is_file() and file_sha256(destination) == expected:
        print(f"Verified existing JPL kernel: {destination}")
        return

    temporary = destination.with_suffix(f"{destination.suffix}.part")
    temporary.unlink(missing_ok=True)
    request = Request(url, headers={"User-Agent": "jyothisyam-api-build/0.1"})
    digest = sha256()
    size = 0

    try:
        with urlopen(request, timeout=180) as response, temporary.open("wb") as target:
            while chunk := response.read(CHUNK_SIZE):
                target.write(chunk)
                digest.update(chunk)
                size += len(chunk)

        actual = digest.hexdigest()
        if size == 0:
            raise ValueError("downloaded JPL kernel is empty")
        if actual != expected:
            raise ValueError(f"JPL kernel SHA-256 mismatch: expected {expected}, received {actual}")

        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)

    print(f"Downloaded and verified JPL kernel: {destination} ({size} bytes, {expected})")


def main() -> int:
    """Parse command-line arguments and install the verified kernel."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--destination",
        type=Path,
        default=Path("app/data/jpl/de440s.bsp"),
        help="destination path for the verified SPK kernel",
    )
    parser.add_argument("--url", default=DEFAULT_URL, help="official JPL kernel URL")
    parser.add_argument(
        "--sha256",
        default=DEFAULT_SHA256,
        help="required lowercase or uppercase SHA-256 digest",
    )
    arguments = parser.parse_args()
    download_kernel(arguments.destination, arguments.url, arguments.sha256)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
