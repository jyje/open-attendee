# open-attendee 발표 자료 (Slidev)

기획 문서 `docs/open-attendee-planning.md`를 바탕으로 만든 발표 초안입니다. 발표자와 시간 등 미확정 항목은 `slides.md`의 TODO 주석에 있습니다.

## 실행

Node.js 26(`.nvmrc` 참고)과 pnpm 12가 필요합니다. `corepack enable`을 켜면 `package.json`의 `packageManager` 값대로 pnpm이 맞춰집니다.

```sh
pnpm install --frozen-lockfile   # 최초 1회
pnpm run dev        # 개발 서버 (기본 http://localhost:3030)
pnpm run build      # 정적 빌드 -> dist/
```

## 파일

- `slides.md`: 발표 본문
- `slidev.config.ts`: Slidev 설정
- `styles/index.css`: 색상 (design-system/tokens.css 값을 복사)
- `package.json`: 의존성 (`@slidev/cli`, `@slidev/theme-default`)

## 참고

- 영문 덱은 아직 없습니다. 기획 문서가 한국어만 요구하므로 제외했습니다.
- 글꼴은 외부에서 받지 않고 시스템 글꼴을 씁니다.
