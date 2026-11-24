<div align="center">

# Open Attendee

밋업 들으러 가는 당신을 위한 요약 도구

[![CI](https://github.com/jyje/open-attendee/actions/workflows/ci.yml/badge.svg)](https://github.com/jyje/open-attendee/actions/workflows/ci.yml)
[![Build image](https://github.com/jyje/open-attendee/actions/workflows/build.yml/badge.svg)](https://github.com/jyje/open-attendee/actions/workflows/build.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

밋업, 이벤트, 학회, 미팅에서 직접 기록하고 참고자료를 받아, AI로 요약해 원하는 형태로 정리하는 필기 도구입니다. 정리된 초안에 내 인사이트를 더한 뒤 최종 검토합니다. 이 프로젝트는 AWS Kiro Crew로 구성한 AI 에이전트 팀과 함께 만들었습니다.

**Demo:** [https://attendee.app.jyje.online](https://attendee.app.jyje.online) (prd). 소유자 1명용 로그인이 필요합니다. 컨테이너 이미지는 `ghcr.io/jyje/open-attendee`(prd), `-stg`, `-dev`로 공개되어 있고, 아래 6절의 명령으로 직접 실행해 볼 수도 있습니다.

**발표자료:** [`PRESENTATION.pdf`](PRESENTATION.pdf) (12쪽)

> **지금 구현 단계:** 기록(필기, 사진, 자료 첨부, 녹음 동의 게이트)부터 AI 요약, 출처가 붙은 초안, 검토와 승인, 마크다운 내보내기까지 동작합니다. 녹음과 전사, 템플릿 선택·저장, 얼굴 흐림 등은 구현 전입니다. 기능별 상태는 2절 표에 있습니다.

---

## 1. 문제 정의

### 대상 사용자
밋업, 이벤트, 학회, 미팅에 참석하는 학생과 직장인.

### 문제 상황
참석자가 발표를 들으며 메모합니다. 나중에 내용을 요약하는 데 시간이 많이 들고, 메모는 여러 서비스에 흩어져 있습니다.

### 기존 방식과 한계
메모장, 노션, 음성 녹음 앱, 클로바 노트 같은 서비스는 기능이 좋습니다. 하지만 사용량 제한이 있고, 플랫폼이 여러 곳으로 나뉘어 있습니다. 내게 필요한 세부 기능이 없는 경우도 많습니다.

### 근거
직접 경험입니다. 밋업 한 번에 녹음이 3~4시간 나오고, PDF와 PPT가 많습니다. 기록에 쓰는 서비스는 10개 이상이고, 대부분 새 구독료가 듭니다.

### 목표
행사 중 필기(20장 이상), 녹음, 사진, 발표자료, 참고자료를 한곳에 모습니다. AI가 요약해 원하는 형태로 정리하고, 사용자가 자기 인사이트를 더한 뒤 최종 검토합니다. 사용자가 선호하는 일관된 템플릿으로 구성할 수 있습니다.

---

## 2. 핵심 기능

웹에서 필기하고, 녹음은 STT 모델로 글로 바꾸고, 사진과 자료를 첨부합니다. AI 에이전트가 이 기록을 요약하고 정리해 초안을 만듭니다. 이때 초안의 모든 문장에는 출처(어느 메모, 어느 쪽, 어느 사진)를 붙이고, 출처로 확인되지 않은 문장은 "미검증"으로 표시해서 사람이 검토하기 전에는 내보내지 않습니다.

| 기능 | 해결하는 불편 | 상태 | 코드 위치 |
|---|---|---|---|
| 웹 필기 편집기 (블록 단위, 입력을 멈추면 자동 저장) | 메모가 여러 서비스에 흩어짐 | **동작** | [`SessionDetailView.vue`](webapp/frontend/src/views/SessionDetailView.vue), [`sessions.py`](webapp/src/open_attendee/sessions.py) |
| 사진 첨부 (세션당 200장까지, EXIF 위치 정보 제거, 촬영 시각이 가까운 메모에 자동 연결) | 필기와 사진이 따로 있음 | **동작** | [`AssetsPanel.vue`](webapp/frontend/src/components/AssetsPanel.vue), [`processors/photo.py`](webapp/src/open_attendee/processors/photo.py) |
| 발표자료(PDF) 첨부와 텍스트 추출 (30MB까지) | 자료를 직접 읽고 요약해야 함 | **동작** (PPTX는 구현 전) | [`processors/docs.py`](webapp/src/open_attendee/processors/docs.py), [`assets.py`](webapp/src/open_attendee/assets.py) |
| 참고자료 받기 (PDF, TXT, MD) | 흩어진 참고자료를 따로 찾아야 함 | **동작** (URL 가져오기는 구현 전) | [`assets.py`](webapp/src/open_attendee/assets.py) |
| 녹음과 STT 전사 (동의 확인 후에만 처리) | 3~4시간 녹음을 직접 정리해야 함 | **동의 게이트만 동작**, 녹음과 전사는 꺼져 있음 | [`consent.py`](webapp/src/open_attendee/consent.py) |
| AI 요약, 초안 (모든 문장에 출처, 출처가 뒷받침하는지 AI가 한 번 더 확인) | 요약에 시간이 많이 듦 | **동작** (요청 안에서 동기 실행) | [`llm.py`](webapp/src/open_attendee/llm.py), [`drafts.py`](webapp/src/open_attendee/drafts.py), [`SummaryPanel.vue`](webapp/frontend/src/components/SummaryPanel.vue) |
| 원하는 템플릿 선택, 저장, 재사용 | 원하는 형태로 정리하는 기능이 부족함 | 블로그 템플릿 1개만 고정, 선택·저장은 구현 전 | |
| 인사이트 추가와 최종 검토 (미검증 문장 처리, 사람만 승인, 승인한 초안만 내보내기) | AI 요약만으로는 내 생각이 빠짐 | **동작** (마크다운) | [`DraftPanel.vue`](webapp/frontend/src/components/DraftPanel.vue), [`drafts.py`](webapp/src/open_attendee/drafts.py) |

설치 환경은 맥북, 모바일(반응형 웹), AWS, 온프레미스입니다. 자세한 방법은 6절에 씁니다.

### 구조

```text
브라우저 (Vue 3 + Vite)
   │  /api  (JSON, 쿠키 세션, CSRF 토큰)
   ▼
FastAPI 서버 ─ SQLite (SQLModel) ─ 파일 저장소 (로컬 볼륨, S3는 구현 전)
   │
   └─ provider-manager (OpenAI / Bedrock, Strands 모델 팩토리)
```

- 이미지 하나로 나옵니다. Vue 화면을 빌드해서 FastAPI가 같이 서빙합니다.
- 서버는 `/api` 아래 JSON만 냅니다. 화면은 [`design-system/`](design-system)의 토큰과 글꼴을 그대로 씁니다.
- 컨테이너는 비루트(uid 10001)로 8080 포트에서 실행합니다. amd64와 arm64 이미지를 모두 만듭니다.

### 개인정보와 보안 기본값

- **녹음은 동의 기록이 있어야만 처리합니다.** 화면이 아니라 서버가 업로드와 작업 등록에서 두 번 막습니다. 본인 혼자 말한 음성 메모만 예외입니다. 지금 배포에서는 녹음 기능 자체가 꺼져 있습니다(`FEATURE_RECORDING=false`).
- **사진의 위치 정보(EXIF)는 저장하지 않습니다.** 촬영 시각만 남깁니다.
- 소유자 1명의 비밀번호(argon2 해시)로 로그인하고, 로그인 시도는 접속자 IP별로 분당 5회까지 받으며, 쓰기 요청은 CSRF 토큰을 검사합니다.
- 비밀 값은 환경 변수와 Kubernetes Secret으로만 받고, 저장소와 이미지에는 넣지 않으며 로그에서는 가립니다.

---

## 3. 사용 시나리오

1. 발표를 들으며 웹에 필기하고, 사진과 발표자료를 첨부합니다. (녹음은 동의를 확인한 뒤 켤 수 있도록 준비 중입니다.)
2. AI 에이전트가 기록을 요약하고, 블로그 템플릿에 맞춰 출처가 붙은 초안을 만듭니다.
3. 사용자가 초안에 자기 인사이트를 더하고, 미검증 문장을 처리한 뒤 승인하고, 마크다운으로 내려받습니다.

## 4. 기대 효과

- **서비스 10개 이상 → 1개**: 필기, 사진, PDF, 요약, 내보내기를 한곳에서 합니다.
- **새 구독료 없음**: 내 AWS, 내 서버, 내 AI 키를 씁니다. 사용료는 따로 듭니다.
- **믿을 수 있는 요약**: 모든 문장에 출처가 붙고, 확인되지 않은 문장은 표시됩니다.
- **개인정보 보호**: 사진 위치 정보는 지우고, 동의 없는 녹음은 처리하지 않습니다.
- **어디서든 실행**: 이미지 하나로 맥북, AWS, 온프레미스에서 돕니다.

목표(아직 측정하지 않았습니다): 정리 시간 2~3시간 → 30분 이내. 녹음과 전사가 꺼져 있어서, 지금은 필기, 사진, PDF만 기준입니다.

## 5. 차별점

- 여러 플랫폼에 흩어진 기능을 한곳에서 씁니다.
- 새 구독료 대신 내 AWS, 온프레미스, AI 구독을 씁니다.
- 내게 필요한 세부 기능을 직접 정합니다.
- 초안의 모든 문장에 출처를 붙이고, 확인되지 않은 문장은 사람이 처리하기 전에는 내보내지 않습니다.

---

## 6. 설치와 실행

필요한 것: [uv](https://docs.astral.sh/uv/)(Python 3.13), Node.js 22, Docker(컨테이너로 실행할 때).

```bash
git clone https://github.com/jyje/open-attendee.git
cd open-attendee
```

### 로컬 개발 (맥북)

```bash
# 1. 환경 변수 만들기 (webapp/.env는 커밋되지 않습니다)
cp webapp/.env.example webapp/.env
#    OWNER_PASSWORD_HASH: 비밀번호의 argon2 해시. 만드는 명령은 webapp/.env.example 안에 있습니다.
#    SESSION_SECRET: 아무 긴 문자열 (python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# 2. 서버 (자동 재시작)
cd webapp/src
uv sync
uv run uvicorn open_attendee.main:app --reload --env-file ../.env --port 8080

# 3. 화면 (다른 터미널, 저장하면 바로 반영)
cd webapp/frontend
pnpm install --frozen-lockfile
pnpm run dev        # http://localhost:5173 으로 접속합니다
```

로그인 쿠키에 `Secure`가 붙어 있어서 `http://localhost`나 `https://`에서만 로그인이 유지됩니다.

### 컨테이너 (compose)

```bash
cp webapp/.env.example webapp/.env     # 값을 채웁니다
docker compose up --build              # http://localhost:8080
```

### Kubernetes (microk8s, AWS, 온프레미스)

`main`(과 `dev`, `stg`, `prd`)에 머지되면 GitHub Actions가 amd64와 arm64 이미지를 만들어 `r<번호>-<커밋>` 태그로 올립니다. `main`과 `dev`는 `ghcr.io/jyje/open-attendee-dev`, `stg`는 `-stg`, `prd`는 `ghcr.io/jyje/open-attendee`입니다. 차트의 기본 이미지는 `prd`용이라서 개발 이미지는 `--set image.repository=...`로 바꿉니다.

```bash
helm upgrade --install open-attendee ./helm -n open-attendee --create-namespace \
  --set image.repository=ghcr.io/jyje/open-attendee-dev \
  --set image.tag=<CI가 만든 태그>
```

비밀(Secret) 만들기, 환경 변수 표, 인그레스, 되돌리기는 [`docs/deploy.md`](docs/deploy.md)에 있습니다. AI 요약을 쓰려면 `OPENAI_API_KEY` 또는 `AWS_BEARER_TOKEN_BEDROCK`을 Secret에 더합니다.

## 7. 테스트

```bash
# 서버: 린트와 테스트 (속성 기반 테스트 포함)
cd webapp/src
uv run ruff check . && uv run ruff format --check . && uv run pytest

# 화면: 타입 검사와 빌드
cd webapp/frontend && pnpm run build

# provider-manager
cd provider-manager/src && uv run pytest

# helm 차트
helm lint helm --set image.tag=test
```

위 검사는 PR과 `main`에서 [`ci.yml`](.github/workflows/ci.yml)이 같은 명령으로 실행합니다. 이미지 빌드는 [`build.yml`](.github/workflows/build.yml)이 PR에서는 검증만 하고, `main`에서만 게시합니다.

테스트가 확인하지 못하는 것: 실제 LLM 호출(가짜 응답으로만 시험), 실제 클러스터 배포, 사용자가 쓰는 브라우저별 화면(헤드리스 Chrome으로만 확인).

---

## 8. 현재 상태와 로드맵

**구현 정도:** 기록(로그인, 행사, 필기, 사진, PDF·참고자료, 녹음 동의 게이트)과 AI 요약, 출처가 붙은 초안, 지지 판정, 검토·승인, 마크다운 내보내기가 동작하고 테스트와 CI가 있습니다. 실제 OpenAI 호출로 끝까지 확인했지만, AI의 지지 판정은 느슨해서 추정 문장도 통과했습니다. 그래서 사람의 검토와 승인이 필수입니다.

**배포 환경 (반영됨)**
- 다단계 `Dockerfile`(화면 빌드, 서버 의존성, 실행), 비루트, 8080, amd64와 arm64. 로컬용 `docker-compose.yml`.
- `helm/`: 설정은 ConfigMap, 비밀은 미리 만든 Secret 참조, 데이터는 PVC, `/healthz` 확인, 복제본 1개.
- CI: `ci.yml`(테스트, 린트, 화면 빌드, helm lint), `build.yml`(브랜치별 이미지, 불변 태그).
- microk8s에 맞춘 값: 기본 저장소가 NFS라서 SQLite를 `delete` 저널로 사용, 인그레스 `nginx`와 `nginx-letsencrypt-prod`, 업로드 본문 32m, 인그레스 뒤 접속자 IP별 로그인 제한(`FORWARDED_ALLOW_IPS`).

**로드맵 (아직 반영하지 않음)**
- 클러스터에 실제 배포하고 Demo 주소 채우기. 아직 배포하지 않았습니다.
- `dev`, `stg`, `prd` 브랜치 만들기와 환경별 helm values. 지금은 values 파일 하나입니다.
- 템플릿 선택·저장·복제, 수정한 문장의 재검증, 더 엄격한 지지 판정, 작업 큐(지금은 요청 안에서 동기 실행).
- 녹음, STT 전사, 전사 후 원본 삭제, 동의 철회. 사진 얼굴 흐림, PPTX, HTML 내보내기.
- S3 저장소(지금은 로컬 볼륨만), 상태 점검 명령, 정리 시간 측정.
- 화면 자동 테스트(지금은 헤드리스 Chrome으로 수동 확인), 녹음 법률 검토, 데이터 보관 기간 정책.
- 여러 사용자와 공유, AWS GPU 전사. 이번 범위 밖입니다.

---

## 문서

- 배포 가이드: [`docs/deploy.md`](docs/deploy.md)
- Kiro를 어떻게 썼는지: [`BUILD_REPORT.md`](BUILD_REPORT.md), [`docs/KIRO_USAGE.md`](docs/KIRO_USAGE.md)
- 평가, 거버넌스, 보안 유의사항: [`docs/EVALUATION_GOVERNANCE_SECURITY.md`](docs/EVALUATION_GOVERNANCE_SECURITY.md)
- 발표자료: [`PRESENTATION.pdf`](PRESENTATION.pdf). 원본은 [`slidev/slides.md`](slidev/slides.md)이고, 글꼴은 Pretendard(한글)와 Rubik(영문 제목, 디자인 시스템)을 npm 패키지로 묶어 PDF에 넣었습니다.

  ```bash
  cd slidev
  pnpm install --frozen-lockfile
  pnpm add --save-dev playwright-chromium    # PDF 내보내기에 필요합니다. package.json과 락 파일 변경은 커밋하지 마세요
  pnpm exec slidev export --output ../PRESENTATION.pdf --wait 3000
  ```

## 출처와 라이선스

- 이 저장소의 코드는 [MIT](LICENSE)입니다. 화면, 서버, 배포 설정은 이 해커톤에서 새로 작성했습니다.
- **디자인**: [kirothon-timer.vercel.app](https://kirothon-timer.vercel.app/)에서 추출한 토큰([`design-system/`](design-system))과, AWS의 오픈소스 [Cloudscape](https://cloudscape.design/) 디자인 토큰 참고 자료(Apache-2.0, [`docs/references/cloudscape/`](docs/references/cloudscape)에 라이선스와 출처 포함).
- **글꼴**: `@fontsource`로 내려받는 Rubik(OFL-1.1), Rubik Mono One, Permanent Marker(Apache-2.0).
- **주요 라이브러리**: Vue, Vite, FastAPI, SQLModel, Pillow, pypdf, Strands Agents 등. 각 라이선스는 해당 패키지를 따릅니다.
- **CI 이미지 빌드 방식**은 작성자 본인의 저장소 [`jyje/mungchilog`](https://github.com/jyje/mungchilog)의 `build.yml` 구성을 참고했습니다.

## 디자인 시스템

- 토큰: [`design-system/tokens.css`](design-system/tokens.css)
- 규칙과 컴포넌트: [`design-system/DESIGN.md`](design-system/DESIGN.md)
- 에이전트 스킬: [`.agents/skills/kirothon-design-system/SKILL.md`](.agents/skills/kirothon-design-system/SKILL.md)

원본 디자인은 [kirothon-timer.vercel.app](https://kirothon-timer.vercel.app/)에서 추출했어요.

---

## 팀

- **팀 번호:** team-032 (해커톤 제출 당시 레포 이름은 `kirothon-team-032`였고, 이후 `open-attendee`로 옮겼습니다)
- **팀명:** Studio.R4iny (1인팀)

| 이름 | 역할 |
|---|---|
| 팀장이 (Bot) | 팀장 |
| 정책이 (Bot) | 평가 기준, 거버넌스, 보안 유의사항 문서와 Kiro 활용 증거, 정책 점검 |
| 문서기 (Bot) | 기획 문서와 공지 정리 <!-- 담당 확인 필요 --> |
| 배포기 (Bot) | 배포 <!-- 담당 확인 필요 --> |
| 디자이니 (Bot) | 디자인 시스템 <!-- 담당 확인 필요 --> |
| jyje | 1인팀 구성원 |

팀 구조와 근거는 [`docs/team.md`](docs/team.md)에 있습니다.
