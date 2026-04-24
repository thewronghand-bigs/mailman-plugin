# Mailman Plugin

Codex Desktop용 Google Chat 메시지 수집 플러그인.

백엔드가 봇으로 뿌린 API 스펙을 `@mailman` 한 마디로 빨아옵니다.

## 설치

```bash
curl -fsSL https://raw.githubusercontent.com/thewronghand-bigs/mailman-plugin/main/install.sh | bash
```

bun이 없으면 [여기서](https://bun.sh) 먼저 설치하세요.

설치하면 알아서:
- `~/plugins/mailman`에 플러그인 배치
- bun 의존성 + Playwright Chromium 설치
- `~/.agents/plugins/marketplace.json`에 등록
- `runtime/config.json` 생성

## 설정

```bash
vi ~/plugins/mailman/runtime/config.json
```

```json
{
  "spaces": {
    "myspace": {
      "url": "https://chat.google.com/u/0/app/chat/스페이스_ID",
      "webhookUrl": "",
      "bots": {
        "봇별칭": "봇 표시 이름"
      },
      "defaultBot": "봇별칭",
      "mentionFilter": "@홍길동"
    }
  },
  "defaultSpace": "myspace"
}
```

| 필드 | 설명 |
|------|------|
| `url` | 브라우저에서 해당 DM 열고 주소창 복사 |
| `webhookUrl` | 전송용 webhook URL. 없으면 비워두기 |
| `bots` | `{ "별칭": "봇 표시 이름" }`. **한 글자라도 다르면 못 잡음** |
| `mentionFilter` | 이 문자열이 포함된 메시지만 수집. 생략 시 전체 수집 |

## 최초 로그인

```bash
bash ~/plugins/mailman/runtime/run.sh auth
```

Chrome이 뜹니다. 회사 계정으로 로그인하세요. DM이 보이면 터미널에서 Enter.

## 사용

Codex Desktop을 재시작하면 `@mailman`으로 사용 가능합니다.

## 데이터 위치

| 항목 | 경로 |
|------|------|
| 플러그인 | `~/plugins/mailman` |
| DB | `~/.mailman/inbox/mailman.db` |
| Chrome 프로필 | `~/.mailman/state/mailman-chrome` |
| 로그 | `~/.mailman/logs/mailman.log` |

## 문제 생기면

| 증상 | 처방 |
|------|------|
| "로그인 세션이 없거나 만료되었습니다" | `bash ~/plugins/mailman/runtime/run.sh auth` |
| 아무것도 안 나옴 | config.json의 `bots` 확인. 띄어쓰기 하나 틀려도 안 됨 |
| Codex에서 @mailman이 안 보임 | Codex Desktop 재시작 |
| DB 초기화하고 싶음 | `sqlite3 ~/.mailman/inbox/mailman.db "DELETE FROM messages; DELETE FROM meta;"` |

## 삭제

```bash
curl -fsSL https://raw.githubusercontent.com/thewronghand-bigs/mailman-plugin/main/uninstall.sh | bash
```

수집 데이터(`~/.mailman`)는 자동 삭제되지 않습니다. 완전히 지우려면 `rm -rf ~/.mailman`.

## 원본

Claude Code용 전체 런타임은 [claude-mailman](https://github.com/thewronghand-bigs/mailman)에 있습니다.
