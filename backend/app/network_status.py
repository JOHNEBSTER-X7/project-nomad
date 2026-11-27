"""Safe, configuration-based network status for the NOMAD edge host.

This module intentionally does not scan networks, enumerate client devices,
or expose IP addresses. It reports operator-configured posture and local
service health only.
"""
import os


def _enabled(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def network_status(*, ai: dict, knowledge: dict) -> dict:
    mode = os.getenv("NOMAD_NETWORK_MODE", "lan").strip().lower()
    if mode not in {"lan", "standalone"}:
        mode = "lan"
    return {
        "network_mode": mode,
        "connectivity": "local_only",
        "external_sync_enabled": _enabled(os.getenv("NOMAD_EXTERNAL_SYNC_ENABLED", "false")),
        "device_discovery": "disabled",
        "services": {
            "api": "online",
            "local_ai": "available" if ai.get("available") else ("disabled" if not ai.get("enabled") else "unavailable"),
            "knowledge_index": "ready" if knowledge.get("enabled") and knowledge.get("indexed") else "lexical_fallback",
        },
        "safety": {"network_scanning": False, "client_inventory_exposed": False, "external_sync_opt_in": True},
    }
