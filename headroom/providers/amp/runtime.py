"""Runtime helpers for Amp integrations."""

from __future__ import annotations

from pathlib import Path


def project_plugin_dir(project: Path | None = None) -> Path:
    """Return the project-scoped Amp plugin directory."""
    root = project or Path.cwd()
    return root / ".amp" / "plugins"


def project_settings_path(project: Path | None = None) -> Path:
    """Return the workspace Amp settings file."""
    root = project or Path.cwd()
    return root / ".amp" / "settings.json"


def global_plugin_dir() -> Path:
    """Return the user-wide Amp plugin directory on Linux/macOS."""
    return Path.home() / ".config" / "amp" / "plugins"


def default_proxy_url(port: int) -> str:
    """Build the default local Headroom proxy URL."""
    return f"http://127.0.0.1:{port}"


def render_setup_lines(port: int, *, plugin_path: Path, reload_required: bool) -> list[str]:
    """Render Amp setup instructions after `headroom wrap amp`."""
    lines = [
        "  Headroom proxy is running for Amp.",
        "",
        f"  Plugin installed: {plugin_path}",
        f"  Proxy URL:        {default_proxy_url(port)}",
        "",
        "  In Amp:",
        "    1. Open the command palette (Ctrl+O)",
        "    2. Run `plugins: reload`",
        "    3. Start or continue a thread — large tool outputs compress automatically",
        "",
        "  CCR retrieval tool: `headroom_retrieve`",
        "  Status bar shows cumulative token savings for this Amp session.",
    ]
    if reload_required:
        lines.extend(
            [
                "",
                "  Reload plugins after changing Headroom settings or updating the plugin file.",
            ]
        )
    return lines
