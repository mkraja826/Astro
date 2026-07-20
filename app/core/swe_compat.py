"""Compatibility helpers for maintained Swiss Ephemeris Python bindings."""

import swisseph as swe

_RISE_TRANS_CONSTANTS = {
    "BIT_DISC_CENTER": 256,
    "BIT_GEOCTR_NO_ECL_LAT": 128,
    "BIT_NO_REFRACTION": 512,
}


def ensure_rise_trans_constants() -> None:
    """Expose documented rise/set flags omitted by some binary bindings."""

    for name, value in _RISE_TRANS_CONSTANTS.items():
        if not hasattr(swe, name):
            setattr(swe, name, value)
