from __future__ import annotations


def test_admin_system_status_requires_admin_role(client, auth_headers, monkeypatch) -> None:
    monkeypatch.setenv("ADMIN_USER_IDS", "other-admin-id")
    from app.core.config import get_settings

    get_settings.cache_clear()

    response = client.get("/api/v1/admin/system-status", headers=auth_headers)
    assert response.status_code == 403


def test_admin_system_status_allows_configured_admin(client, auth_headers, monkeypatch) -> None:
    monkeypatch.setenv("ADMIN_USER_IDS", "user-1,other-admin")
    from app.core.config import get_settings

    get_settings.cache_clear()

    response = client.get("/api/v1/admin/system-status", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"ok", "degraded", "error"}
    assert "components" in payload
