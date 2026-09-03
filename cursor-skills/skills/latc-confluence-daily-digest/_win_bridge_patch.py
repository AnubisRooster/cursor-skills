"""Windows compatibility shim for cursor-sdk 0.1.6.

The SDK's bridge discovery (cursor_sdk._bridge._read_discovery) reads the
bridge subprocess's stderr using selectors.DefaultSelector, which on Windows
maps to select.select(). Windows select() only accepts sockets, not pipe file
descriptors, so launching any local agent raises:

    OSError: [WinError 10038] An operation was attempted on something
             that is not a socket

This module replaces _read_discovery with a thread-based blocking readline
implementation that does not use selectors. Import it BEFORE creating any
agent:

    import _win_bridge_patch  # noqa: F401  (must precede cursor_sdk use)

It is a no-op on non-Windows platforms.
"""
from __future__ import annotations

import os
import sys
import threading
from typing import Any, Mapping

if sys.platform == "win32":
    from cursor_sdk import _bridge as _b
    from cursor_sdk.errors import CursorSDKError

    def _read_discovery_win(process, timeout: float) -> Mapping[str, Any]:
        if process.stderr is None:
            raise CursorSDKError("Bridge process stderr is unavailable")

        result: dict[str, Any] = {}
        collected: list[str] = []

        def reader() -> None:
            try:
                for line in process.stderr:  # blocking readline; fine in a thread
                    collected.append(line)
                    discovery = _b.parse_discovery_line(line)
                    if discovery is not None:
                        result["discovery"] = discovery
                        return
            except Exception as exc:  # noqa: BLE001
                result["error"] = exc

        t = threading.Thread(target=reader, name="cursor-bridge-discovery", daemon=True)
        t.start()
        t.join(timeout)

        if "discovery" in result:
            return result["discovery"]
        if "error" in result:
            raise CursorSDKError(
                f"Bridge discovery read failed: {result['error']}"
            )
        exit_code = process.poll()
        if exit_code is not None:
            raise CursorSDKError(
                f"Bridge exited before discovery with status {exit_code}: "
                + "".join(collected)
            )
        raise CursorSDKError("Timed out waiting for bridge discovery")

    _b._read_discovery = _read_discovery_win  # type: ignore[attr-defined]
