# syntax=docker/dockerfile:1
# 빌드 맥락은 저장소 루트다: docker build -f docker/Dockerfile .
# Vue 화면을 빌드하고(node), Python 서버에 얹어서(FastAPI) 이미지 하나로 낸다.
ARG NODE_VERSION=26.13.1
ARG PNPM_VERSION=12.23.0
ARG PYTHON_VERSION=3.13

# --- 1) 화면 빌드 ---------------------------------------------------------
# 다이제스트는 node:26.13.1-alpine 매니페스트 리스트다. 버전을 올릴 때 함께 바꾼다.
FROM node:${NODE_VERSION}-alpine@sha256:6bd9ab43c0ec0190ca7b2d193906cb8b7edf6e7f4afa43ddeccd6452710bffb5 AS frontend
# Node 26 이미지에는 corepack이 없어서 pnpm을 직접 설치한다.
ARG PNPM_VERSION
RUN npm install --global pnpm@${PNPM_VERSION}
WORKDIR /build
# vite.config.ts가 ../../design-system 의 토큰을 가져오므로 같은 상대 위치에 둔다.
COPY design-system ./design-system
WORKDIR /build/webapp/frontend
COPY webapp/frontend/package.json webapp/frontend/pnpm-lock.yaml webapp/frontend/pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile
COPY webapp/frontend/ ./
RUN pnpm run build

# --- 2) 서버 의존성 -------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS backend
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
# webapp은 ../../provider-manager/src 를 경로 의존성으로 쓰므로 같은 상대 위치를 지킨다.
WORKDIR /app
COPY provider-manager/src ./provider-manager/src
WORKDIR /app/webapp/src
COPY webapp/src/pyproject.toml webapp/src/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY webapp/src/open_attendee ./open_attendee
RUN uv sync --frozen --no-dev

# --- 3) 실행 이미지 -------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS runtime
# 비루트로 실행한다. /data에 SQLite와 업로드 파일이 쌓인다(볼륨으로 붙인다).
RUN groupadd --gid 10001 app \
 && useradd --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app \
 && mkdir /data && chown app:app /data
COPY --from=backend /app /app
COPY --from=frontend /build/webapp/frontend/dist /app/webapp/frontend/dist
WORKDIR /app/webapp/src
ENV PATH="/app/webapp/src/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    FRONTEND_DIST=/app/webapp/frontend/dist \
    DATA_DIR=/data
# 이미지가 어느 커밋에서 왔는지 남긴다. 값이 매번 바뀌므로 무거운 층 뒤에 둔다.
ARG SOURCE_URL=https://github.com/jyje/open-attendee
ARG IMAGE_TAG=dev
ARG COMMIT_SHA=unknown
ARG BUILD_TIME=unknown
LABEL org.opencontainers.image.title="open-attendee" \
      org.opencontainers.image.source="${SOURCE_URL}" \
      org.opencontainers.image.version="${IMAGE_TAG}" \
      org.opencontainers.image.revision="${COMMIT_SHA}" \
      org.opencontainers.image.created="${BUILD_TIME}"
USER 10001:10001
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2).status == 200 else 1)"]
CMD ["uvicorn", "open_attendee.main:app", "--host", "0.0.0.0", "--port", "8080"]
