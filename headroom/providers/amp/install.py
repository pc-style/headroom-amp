"""Amp install-time helpers."""

from __future__ import annotations

from .runtime import default_proxy_url


def build_install_env(*, port: int, backend: str) -> dict[str, str]:
    """Build the persistent install environment for Amp."""
    del backend
    return {
        "HEADROOM_PROXY_URL": default_proxy_url(port),
        "HEADROOM_PORT": str(port),
    }
