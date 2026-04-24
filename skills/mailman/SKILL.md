---
name: mailman
description: Google Chat에서 수집한 최신 메시지(API 스펙 등) 가져오기
user-invokable: true
argument-hint: "[스페이스별칭] [봇별칭] [개수=5]"
---

# Mailman

Google Chat DM에서 봇 메시지를 수집해 현재 대화에 삽입한다.

## 사용 예시

- "mailman으로 최근 스펙 가져와"
- "tn 방에서 최근 메시지 3개 가져와"
- "인준 방에서 백신사 메시지 1개만"

## 실행 방법

아래 명령어를 실행한다:

```bash
bash ~/plugins/mailman/runtime/fetch.sh [스페이스별칭] [봇별칭] [개수]
```

인자는 사용자 요청에서 추론한다:
- 스페이스별칭: "인준", "tn" 등. 생략 시 기본 스페이스.
- 봇별칭: config.json의 bots에 등록된 별칭. 생략 시 전체 메시지.
- 개수: 숫자. 생략 시 5.

## 주의

- 브라우저를 직접 열거나 DOM을 추출하지 마라. fetch.sh가 Playwright collector를 내부적으로 실행한다.
- config.json이 없으면 "runtime/config.json을 먼저 설정하세요"라고 안내한다.
- "로그인 세션이 없거나 만료되었습니다" 에러가 나오면 `bash ~/plugins/mailman/runtime/run.sh auth` 실행을 안내한다.
