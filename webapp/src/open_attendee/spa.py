"""빌드된 Vue 화면(`frontend/dist`)을 서빙한다. API가 아닌 GET 요청은 모두 `index.html`로 보낸다."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles

# 이 파일: webapp/src/open_attendee/spa.py → webapp/frontend/dist
DEFAULT_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"

_NO_BUILD = (
    "화면이 빌드되지 않았어요. webapp/frontend에서 `pnpm run build`를 실행하거나, "
    "개발 중이면 Vite 개발 서버(5173)로 접속하세요."
)


def mount_spa(app: FastAPI, dist: Path | None = None) -> None:
    """라우터 등록이 모두 끝난 뒤 마지막에 부른다. catch-all이 다른 경로를 가리지 않게 한다."""
    dist = (dist or DEFAULT_DIST).resolve()
    index = dist / "index.html"
    assets = dist / "assets"
    if assets.is_dir():
        # 파일 이름에 해시가 붙어 있어 오래 캐시해도 된다.
        app.mount("/assets", StaticFiles(directory=assets), name="spa-assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str) -> Response:
        if path == "api" or path.startswith("api/"):
            return JSONResponse({"detail": "찾을 수 없어요."}, status_code=404)
        if not index.is_file():
            return PlainTextResponse(_NO_BUILD, status_code=503)
        candidate = (dist / path).resolve()
        if path and candidate.is_file() and candidate.is_relative_to(dist):
            return FileResponse(candidate)  # favicon 같은 루트 파일
        return FileResponse(index, headers={"Cache-Control": "no-cache"})
