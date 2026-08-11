"""Tests for the MSX Bridge Provider."""

from pkgutil import extend_path

# The provider suite runs beside a Music Assistant checkout and reuses shared
# test helpers from it while keeping provider-specific tests in this package.
__path__ = extend_path(__path__, __name__)
