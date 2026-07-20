"""Provider-neutral ephemeris errors."""


class EphemerisConfigurationError(RuntimeError):
    """Raised when an astronomical provider is configured incorrectly."""


class EphemerisUnavailableError(RuntimeError):
    """Raised when required astronomical data is unavailable."""
