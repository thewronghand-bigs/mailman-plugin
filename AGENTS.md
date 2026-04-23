# mailman-plugin

Codex Desktop용 Mailman 플러그인. Google Chat 봇 메시지를 snapshot driver로 수집해 로컬 SQLite에 저장하고 Codex 대화에 삽입한다.

## 구조

```
.agents/plugins/marketplace.json  # 로컬 marketplace 등록
assets/                           # 플러그인 아이콘
bootstrap.sh                      # 로컬 설치 헬퍼
runtime/                          # snapshot 전용 Mailman 런타임
  collector.ts                    # snapshot JSON → SQLite import
  fetch.ts                        # SQLite → markdown 출력
  fetch.sh / run.sh               # 셸 래퍼
  runtime.ts                      # 공용 설정/경로 해석
  snapshot.ts                     # snapshot JSON 파서
  config.example.json             # 설정 템플릿
scripts/
  extract_google_chat_messages.js # 브라우저에서 DOM → JSON 추출
  import_snapshot.sh              # snapshot import 래퍼
skills/
  mailman/SKILL.md                # 주 스킬
  mailman-sandbox/SKILL.md        # 호환 별칭
```

## 런타임

- bun 전용 (`bun:sqlite`)
- Playwright 없음 — snapshot driver만 지원
- `MAILMAN_HOME` 환경변수로 데이터 경로 지정 (기본: `~/.mailman`)

## 주요 환경변수

| 변수 | 설명 |
|------|------|
| `MAILMAN_HOME` | 런타임 데이터 루트 (기본: `~/.mailman`) |
| `MAILMAN_SNAPSHOT_FILE` | import할 JSON 파일 경로 |

## 원본 레포

Claude Code용 전체 런타임(Playwright 포함)은 [claude-mailman](https://github.com/thewronghand-bigs/mailman)에 있다.
