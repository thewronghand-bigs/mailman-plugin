---
name: mailman-post
description: Google Chat 스페이스에 webhook으로 메시지를 전송 (완료 알림, 질문, API 스펙 공유)
user-invokable: true
argument-hint: "[스페이스별칭]"
---

# Mailman Post

Google Chat 스페이스에 webhook으로 메시지를 전송한다.

## 실행

파일을 탐색하지 말고, 아래 형식으로 바로 실행하라:

```bash
cat <<'MAILMAN_EOF' | bash ~/plugins/mailman/runtime/send.sh [스페이스별칭]
[메시지 내용]
MAILMAN_EOF
```

스페이스별칭은 사용자 요청에서 추론한다. 생략 시 기본 스페이스.

## 용도별 포맷

### 1. 작업 완료 알림

```
[작업 완료 알림]
도메인: {파악된 경우}
변경 요약:
- {핵심 변경 1}
- {핵심 변경 2}
변경 파일:
- path/to/file1
- path/to/file2
남은 이슈/질문: {있는 경우만, 없으면 "없음"}
```

5~10줄 이내. 불필요한 수식어 금지.

### 2. 백엔드에 질문

사용자가 "이거 물어봐", "백엔드한테 질문해" 같은 요청을 한 경우에만:

```
[API 스펙 질문]
대상 API: {method} {path}
질문:
- {질문 1}
- {질문 2}
```

### 3. API 스펙 공유

백엔드가 프론트에 API 변경 사항을 전달할 때:

- 첫 줄: 멘션 또는 대상 + 주제 (짧게)
- API별로 분리해서 작성
- 각 API는 아래 구조를 따른다:

```
*{API 제목} API {추가|수정}*

{METHOD} {path}

요청
{
  "fieldName": "TYPE",
  "nullableField": "TYPE", // nullable
  "enumField": "A | B | C"
}

응답
{
  "result": {
    "code": "NUMBER",
    "message": "STRING"
  },
  "payload": { ... }
}
```

스펙 공유 규칙:
- 값 타입은 `STRING`, `NUMBER`, `BOOLEAN` 등으로 표기
- nullable이면 `// nullable` 주석
- enum이면 `"A | B | C"` 형태
- 백엔드 구현 상세, 테스트 상태는 포함하지 마라
- 받는 사람이 구현에 필요한 정보만 포함하라

## 공통 규칙

1. **사용자 승인 필수** — 초안을 출력한 뒤 "이 내용으로 Google Chat에 전송할까요?"라고 묻는다. 승인 전에는 절대 전송하지 않는다. 수정 요청 시 반영 후 재승인.

2. **전송 실행** — 승인되면 위 명령어로 전송.

## 금지

- 사용자 승인 없이 절대 전송하지 마라.
- 자의적으로 질문을 생성하지 마라.
- 내부 파일을 탐색하지 마라.
