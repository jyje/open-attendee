"""빌드된 Vue 화면 서빙 (요구사항 2.7, 25.4)."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from open_attendee.config import Settings
from open_attendee.main import create_app

from .conftest import BASE_URL, login


@pytest.fixture
def dist(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<!doctype html><title>OA</title>", encoding="utf-8")
    (dist / "assets" / "app-abc123.js").write_text("console.log(1)", encoding="utf-8")
    (dist / "favicon.svg").write_text("<svg/>", encoding="utf-8")
    (tmp_path / "secret.txt").write_text("secret", encoding="utf-8")
    monkeypatch.setenv("FRONTEND_DIST", str(dist))
    return dist


@pytest.fixture
def spa_client(settings: Settings, dist: Path) -> Iterator[TestClient]:
    with TestClient(create_app(settings, provider_factory=lambda: None), base_url=BASE_URL) as c:
        yield c


def test_login_route_serves_index_without_login(spa_client: TestClient) -> None:
    res = spa_client.get("/login")
    assert res.status_code == 200
    assert "<title>OA</title>" in res.text


def test_built_assets_are_public(spa_client: TestClient) -> None:
    assert spa_client.get("/assets/app-abc123.js").status_code == 200


def test_deep_link_needs_login_then_serves_index(spa_client: TestClient) -> None:
    res = spa_client.get("/sessions/abc", headers={"Accept": "text/html"}, follow_redirects=False)
    assert (res.status_code, res.headers["location"]) == (303, "/login")
    login(spa_client)
    res = spa_client.get("/sessions/abc", headers={"Accept": "text/html"})
    assert res.status_code == 200
    assert "<title>OA</title>" in res.text


def test_unknown_api_path_is_json_404_after_login(spa_client: TestClient) -> None:
    login(spa_client)
    res = spa_client.get("/api/nope")
    assert res.status_code == 404
    assert res.headers["content-type"].startswith("application/json")


def test_root_files_are_served_but_not_outside_dist(spa_client: TestClient) -> None:
    login(spa_client)
    assert spa_client.get("/favicon.svg").text == "<svg/>"
    outside = spa_client.get("/..%2Fsecret.txt")
    assert "secret" not in outside.text


def test_missing_build_says_so(settings: Settings, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("FRONTEND_DIST", str(tmp_path / "nothing"))
    with TestClient(create_app(settings, provider_factory=lambda: None), base_url=BASE_URL) as c:
        res = c.get("/login")
    assert res.status_code == 503
    assert "pnpm run build" in res.text
