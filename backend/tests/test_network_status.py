from app.network_status import network_status


def test_network_status_defaults_to_local_and_safe(monkeypatch):
    monkeypatch.delenv("NOMAD_NETWORK_MODE", raising=False)
    monkeypatch.delenv("NOMAD_EXTERNAL_SYNC_ENABLED", raising=False)
    result = network_status(ai={"enabled": False, "available": False}, knowledge={"enabled": False, "indexed": False})
    assert result["network_mode"] == "lan"
    assert result["connectivity"] == "local_only"
    assert result["external_sync_enabled"] is False
    assert result["device_discovery"] == "disabled"
    assert result["services"]["api"] == "online"
    assert result["services"]["local_ai"] == "disabled"
    assert result["services"]["knowledge_index"] == "lexical_fallback"
    assert result["safety"]["network_scanning"] is False
    assert result["safety"]["client_inventory_exposed"] is False


def test_network_mode_is_constrained(monkeypatch):
    monkeypatch.setenv("NOMAD_NETWORK_MODE", "unknown-mode")
    assert network_status(ai={}, knowledge={})["network_mode"] == "lan"


def test_external_sync_requires_explicit_enablement(monkeypatch):
    monkeypatch.setenv("NOMAD_EXTERNAL_SYNC_ENABLED", "true")
    assert network_status(ai={}, knowledge={})["external_sync_enabled"] is True
