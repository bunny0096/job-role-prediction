"""Launch RoleScope server with LAN-friendly defaults."""

from __future__ import annotations

import socket
from datetime import datetime, timezone
import os

import uvicorn


def get_lan_ip() -> str:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except Exception:  # noqa: BLE001
        return "127.0.0.1"


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    lan_ip = get_lan_ip()
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    enable_reload = os.getenv("ROLE_SCOPE_RELOAD", "false").lower() == "true"

    print("\nRoleScope server starting...")
    print(f"UTC server time: {now_utc}")
    print(f"Bind host: {host}")
    print(f"Local URL: http://127.0.0.1:{port}")
    print(f"LAN URL (same network): http://{lan_ip}:{port}")
    print("Run with port-forwarding or cloud deployment for worldwide access.\n")

    uvicorn.run(
        "backend.app.main:app",
        host=host,
        port=port,
        reload=enable_reload,
    )
