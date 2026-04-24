# 설치 가이드

## 요구사항

- macOS (다른 OS는 `MAILMAN_CHROME_PATH` 설정 필요)
- [bun](https://bun.sh) >= 1.0
- Google Chat 접근 가능한 계정

## 설치

```bash
curl -fsSL https://raw.githubusercontent.com/thewronghand-bigs/mailman-plugin/main/install.sh | bash
```

또는 직접 clone:

```bash
git clone https://github.com/thewronghand-bigs/mailman-plugin.git
cd mailman-plugin
bash bootstrap.sh
```

이게 전부입니다. bootstrap.sh가 알아서:

1. 플러그인을 `~/plugins/mailman`에 복사
2. bun 의존성 설치
3. Playwright Chromium 설치
4. `runtime/config.json` 생성
5. `~/.agents/plugins/marketplace.json`에 등록

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
| `mentionFilter` | 설정하면 해당 문자열이 포함된 메시지만 수집. 생략 시 전체 |

## 최초 로그인

```bash
bash ~/plugins/mailman/runtime/run.sh auth
```

Chrome이 뜹니다. 회사 계정으로 로그인 → DM이 보이면 터미널에서 Enter.

## 사용

Codex Desktop을 재시작하면 `@mailman`으로 사용 가능합니다.

## 문제 생기면

| 증상 | 처방 |
|------|------|
| "로그인 세션이 없거나 만료되었습니다" | `bash ~/plugins/mailman/runtime/run.sh auth` |
| 아무것도 안 나옴 | config.json의 `bots` 확인 |
| Codex에서 @mailman이 안 보임 | Codex Desktop 재시작 |
