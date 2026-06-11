from __future__ import annotations

import json
from pathlib import Path

from headroom.providers.amp.runtime import default_proxy_url, render_setup_lines
from headroom.providers.amp.wrap import (
    build_workspace_settings,
    install_plugin,
    plugin_source_dir,
)


def test_plugin_source_dir_prefers_packaged_copy() -> None:
    source_dir = plugin_source_dir()
    assert (source_dir / "headroom.ts").exists()
    assert (source_dir / "lib.ts").exists()


def test_build_workspace_settings_merges_proxy_values() -> None:
    settings = build_workspace_settings(
        existing={"amp.mcpServers": {}},
        port=9001,
        enabled=True,
    )
    assert settings["headroom.proxyUrl"] == "http://127.0.0.1:9001"
    assert settings["headroom.proxyPort"] == 9001
    assert settings["headroom.enabled"] is True
    assert settings["amp.mcpServers"] == {}


def test_install_plugin_writes_project_files(tmp_path: Path) -> None:
    source_dir = plugin_source_dir()
    installed_path, changed = install_plugin(
        source_dir=source_dir,
        port=8787,
        project=tmp_path,
    )

    assert changed is True
    assert installed_path == tmp_path / ".amp" / "plugins" / "headroom.ts"
    assert (tmp_path / ".amp" / "plugins" / "lib.ts").exists()

    settings = json.loads((tmp_path / ".amp" / "settings.json").read_text(encoding="utf-8"))
    assert settings["headroom.proxyUrl"] == default_proxy_url(8787)


def test_render_setup_lines_mentions_reload_when_needed() -> None:
    lines = render_setup_lines(
        8787,
        plugin_path=Path(".amp/plugins/headroom.ts"),
        reload_required=True,
    )
    joined = "\n".join(lines)
    assert "plugins: reload" in joined
    assert "headroom_retrieve" in joined
