---
name: mailman-get
description: Google Chat에서 최신 메시지(API 스펙 등)를 수집해 현재 대화에 삽입
user-invokable: true
argument-hint: "[스페이스별칭] [봇별칭] [개수=5]"
---

# Mailman

Google Chat DM에서 봇 메시지를 수집해 현재 대화에 삽입한다.

## 실행

파일을 탐색하거나 config를 읽지 말고, 아래 명령어를 바로 실행하라:

```bash
bash ~/plugins/mailman/runtime/fetch.sh [스페이스별칭] [봇별칭] [개수]
```

인자는 사용자 요청에서 추론한다:
- 스페이스별칭: "인준", "tn" 등. 생략 시 기본 스페이스.
- 봇별칭: config.json의 bots에 등록된 별칭. 생략 시 전체 메시지.
- 개수: 숫자. 생략 시 5.

예시:
- "인준 방에서 백신사 메시지 1개" → `bash ~/plugins/mailman/runtime/fetch.sh 인준 백신사 1`
- "tn 방에서 최근 3개" → `bash ~/plugins/mailman/runtime/fetch.sh tn 3`
- "최근 스펙 가져와" → `bash ~/plugins/mailman/runtime/fetch.sh`

## 출력 활용

출력된 메시지에 API 스펙이 있으면 타입 정의와 요청 작성에 활용하라.

## 에러 대응

- "수집된 데이터가 없습니다" → 수집이 아직 안 된 상태. `bash ~/plugins/mailman/runtime/run.sh` 실행 후 재시도.
- "로그인 세션이 없거나 만료되었습니다" → `bash ~/plugins/mailman/runtime/run.sh auth` 실행을 안내.
- config.json 관련 에러 → `~/plugins/mailman/runtime/config.json`을 설정하라고 안내.

## 금지

- 브라우저를 직접 열거나 DOM을 추출하지 마라.
- config.json, fetch.sh, run.sh 등 내부 파일을 읽거나 탐색하지 마라.
- 샌드박스에서 실행하지 마라. 반드시 로컬 셸에서 실행하라. Playwright는 로컬 Chrome 프로필이 필요하다.
- 명령어 하나로 끝나는 작업이다. 경로 확인, 도구 검색 등 불필요한 탐색을 하지 마라.
