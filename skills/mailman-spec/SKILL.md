---
name: mailman-spec
description: API 스펙 변경 내용을 정형화된 포맷으로 Google Chat에 전달
user-invokable: true
argument-hint: "[스페이스별칭]"
---

# Mailman Spec

API 스펙 변경 사항을 정형화된 포맷으로 Google Chat에 전송한다.

## 실행

파일을 탐색하지 말고, 아래 형식으로 바로 실행하라:

```bash
cat <<'MAILMAN_EOF' | bash ~/plugins/mailman/runtime/send.sh [스페이스별칭]
[메시지 내용]
MAILMAN_EOF
```

## 메시지 작성 규칙

### 구조

- 첫 줄: 멘션 또는 대상 + 주제 (짧게)
- API별로 분리해서 작성
- 각 API는 아래 구조를 따른다:

```
@{대상} {주제} API 변경 전달.

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

### 타입 표기

- 값 타입: `STRING`, `NUMBER`, `BOOLEAN`, `ARRAY`, `OBJECT`
- nullable이면 값 옆에 `// nullable` 주석
- enum이면 `"A | B | C"` 형태

### 포함할 것

- 변경된 API의 요청/응답 구조
- 새로 추가되거나 변경된 필드
- 프론트가 구현에 필요한 정보

### 포함하지 말 것

- 백엔드 구현 상세
- 테스트 상태
- 검증 로직
- 변경 없는 기존 API 재언급

## 공통 규칙

1. **사용자 승인 필수** — 초안을 출력한 뒤 "이 내용으로 Google Chat에 전송할까요?"라고 묻는다. 승인 전에는 절대 전송하지 않는다.
2. **전송 실행** — 승인되면 위 명령어로 전송.

## 금지

- 사용자 승인 없이 절대 전송하지 마라.
- 내부 파일을 탐색하지 마라.
- 단순 텍스트 발송은 이 스킬이 아니라 `mailman-post`를 사용하라.
