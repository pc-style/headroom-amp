"""Amp wrapper provider helpers."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from .runtime import (
    default_proxy_url,
    global_plugin_dir,
    project_plugin_dir,
    project_settings_path,
)

PLUGIN_FILENAME = "headroom.ts"
PLUGIN_LIB_FILENAME = "lib.ts"
PLUGIN_FILES: tuple[str, ...] = (PLUGIN_FILENAME, PLUGIN_LIB_FILENAME)
HEADROOM_PROXY_URL_KEY = "headroom.proxyUrl"
HEADROOM_PROXY_PORT_KEY = "headroom.proxyPort"
HEADROOM_ENABLED_KEY = "headroom.enabled"


def plugin_source_dir(plugin_path: Path | None = None) -> Path:
    """Return the directory containing Amp plugin source files."""
    if plugin_path is not None:
        source_dir = plugin_path.resolve()
        if not source_dir.is_dir():
            raise NotADirectoryError(f"Amp plugin source directory not found: {source_dir}")
        return source_dir

    packaged_dir = Path(__file__).resolve().parent
    if all((packaged_dir / name).exists() for name in PLUGIN_FILES):
        return packaged_dir

    repo_dir = Path(__file__).resolve().parents[3] / "plugins" / "amp"
    if all((repo_dir / name).exists() for name in PLUGIN_FILES):
        return repo_dir

    raise FileNotFoundError("Headroom Amp plugin source was not found in the package or repository.")


def resolve_plugin_source(plugin_path: Path | None) -> Path:
    """Resolve the main Amp plugin entry file for installation."""
    return plugin_source_dir(plugin_path) / PLUGIN_FILENAME


def _read_json_mapping(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def build_workspace_settings(
    *,
    existing: dict[str, Any] | None,
    port: int,
    enabled: bool = True,
) -> dict[str, Any]:
    """Merge Headroom workspace settings into `.amp/settings.json`."""
    settings = dict(existing or {})
    settings[HEADROOM_PROXY_URL_KEY] = default_proxy_url(port)
    settings[HEADROOM_PROXY_PORT_KEY] = port
    settings[HEADROOM_ENABLED_KEY] = enabled
    return settings


def install_plugin(
    *,
    source_dir: Path,
    port: int,
    project: Path | None = None,
    global_install: bool = False,
    enabled: bool = True,
) -> tuple[Path, bool]:
    """Install the Headroom Amp plugin and workspace settings.

    Returns the installed plugin path and whether the plugin file changed.
    """
    destination_dir = global_plugin_dir() if global_install else project_plugin_dir(project)
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / PLUGIN_FILENAME

    plugin_changed = False
    for filename in PLUGIN_FILES:
        src = source_dir / filename
        if not src.exists():
            raise FileNotFoundError(f"Missing Amp plugin file: {src}")
        dest = destination_dir / filename
        existing_bytes = dest.read_bytes() if dest.exists() else None
        shutil.copy2(src, dest)
        if filename == PLUGIN_FILENAME:
            plugin_changed = existing_bytes != dest.read_bytes()

    if not global_install:
        settings_path = project_settings_path(project)
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        merged = build_workspace_settings(
            existing=_read_json_mapping(settings_path),
            port=port,
            enabled=enabled,
        )
        settings_path.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")

    return destination, plugin_changed


def remove_plugin(*, project: Path | None = None, global_install: bool = False) -> None:
    """Remove the managed Headroom Amp plugin file."""
    destination_dir = global_plugin_dir() if global_install else project_plugin_dir(project)
    plugin_path = destination_dir / PLUGIN_FILENAME
    if plugin_path.exists():
        plugin_path.unlink()
