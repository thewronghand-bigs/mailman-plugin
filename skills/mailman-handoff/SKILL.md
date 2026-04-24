---
name: mailman-handoff
description: API 스펙 변경 내용을 카드형 메시지로 Google Chat에 전달. 백엔드가 프론트에 스펙을 공유할 때 사용.
user-invokable: true
---

# Mailman Handoff

Prepare a short teammate-facing handoff and optionally send it to Google Chat by webhook.

## Workflow

1. Collect the real status first.
   - Read changed files, API paths, request fields, response fields, and real frontend impact.
   - Do not include backend-only implementation notes unless they directly change frontend handling.
2. Build the message with `scripts/handoff_google_chat.py`.
3. Default to `--mode draft`.
4. Use `--mode send` only when a destination webhook URL is available and the target is clear.
5. For frontend handoff by webhook, prefer:
   - send the parent summary first
   - the parent summary should be one short plain-text message with the teammate mention at the very beginning
   - one reply per added/modified API using the same `threadKey`
   - each API reply should be one detail card
   - the card title should tell which API was added or modified
6. Prefer `cardsV2` presentation through the helper script.

## Message Rules

- Keep the message short and operational.
- First line: mention or teammate label plus the topic.
- For frontend handoff, the parent summary can stay short and should be plain text only.
- For API reply cards, use:
  - card title = 어떤 API가 추가/수정되었는지
  - card body = `요청`, `응답` 섹션
  - `요청`, `응답`은 카드 섹션 자체로 분리
  - JSON은 각각 분리해서 표시
- For schema-like JSON:
  - 값 타입은 `STRING`, `NUMBER`, `BOOLEAN`, `ARRAY`, `OBJECT` 등으로 표기
  - nullable 이면 값 옆에 `// nullable` 주석 추가
  - enum 값이면 값 자리에 `"A | B | C"` 형태로 표기
- Do not include test status or backend validation detail in frontend handoff unless the user explicitly asks for it.
- If the work is complex, add one extra reply for `API 호출 흐름` only when needed.
- Do not send duplicate layers for the same change.
  - no extra "API 목록" card
  - no extra "변경 내용 요약" card when detailed API cards are already sent
  - no per-API title-only card without `요청`/`응답`
- Only send cards that help the receiver implement the spec.
  - skip backend-only notes
  - skip validation notes
  - skip cards for unchanged legacy APIs unless the user explicitly wants them restated

Good summary:

```text
@프론트 채권 이력 조회 API 변경 전달.
```

Parent summary command:

```bash
python3 ~/plugins/mailman/skills/mailman-handoff/scripts/handoff_google_chat.py \
  --mention-key frontend \
  --webhook-key frontend \
  --thread-key deduction-api-spec-20260411 \
  --mode send \
  --text-only \
  --raw-text "<users/107987990660367540952> 채권 이력 조회 API 변경 전달."
```

Good API card:

```text
*채권 이력 조회 API 수정*

GET /api/v1/ar-dunning-process-targets/history/{targetId}?from=2026-04-01&to=2026-04-30&page=0&size=50

요청
```
{
  "targetId": "NUMBER",
  "from": "STRING",
  "to": "STRING",
  "page": "NUMBER",
  "size": "NUMBER"
}
```

응답
```
{
  "response": {
    "items": [
      {
        "id": "NUMBER",
        "arDunningTargetId": "NUMBER",
        "settlementId": "STRING", // nullable
        "settlementTargetId": "NUMBER" // nullable
      }
    ]
  }
}
```
```

Avoid:

- long code-level explanations
- hiding unverified behavior
- saying "done" without the impact on the receiver
- assuming webhook messages will be threaded without `thread.threadKey` and `messageReplyOption`
- sending test status to frontend by default
- mixing summary sections and API JSON in the same card
- sending the mention after API cards
- sending one-line API cards and then sending the same API again as a detailed card
- sending summary cards that do not add spec information

## Mentions

- This skill supports webhook delivery.
- Webhook mode can send raw Chat mention tokens such as `<users/{user}>` if you already know them.
- If you don't know the real Chat user token, use a plain-text fallback such as `@프론트`.
- Store reusable teammate mappings in `~/plugins/mailman/skills/mailman-handoff/references/mention-map.json` using `team -> users`.
- Store reusable webhook mappings in `~/plugins/mailman/skills/mailman-handoff/references/webhook-map.json` using `team -> channels`.

## Safety

- Never send to a webhook URL discovered incidentally from source code unless the target is clearly intended.
- Prefer `draft` if the destination, recipient, or message accuracy is uncertain.
- Use `--allow-non-google-url` only for local test servers.

## Commands

Draft a parent summary:

```bash
python3 ~/plugins/mailman/skills/mailman-handoff/scripts/handoff_google_chat.py \
  --title "정산 흐름 상세 API 변경" \
  --mention-key frontend \
  --webhook-key frontend \
  --bullet "transferTransactions 응답 구조 변경" \
  --mode draft
```

Send a parent summary:

```bash
python3 ~/plugins/mailman/skills/mailman-handoff/scripts/handoff_google_chat.py \
  --title "정산 흐름 상세 API 변경" \
  --mention-key frontend \
  --webhook-key frontend \
  --bullet "transferTransactions 응답 구조 변경" \
  --mode send
```

Send a preformatted API message:

```bash
python3 ~/plugins/mailman/skills/mailman-handoff/scripts/handoff_google_chat.py \
  --webhook-key frontend \
  --mode send \
  --raw-text-file ./api-message.txt
```

Send a parent summary in a thread:

```bash
python3 ~/plugins/mailman/skills/mailman-handoff/scripts/handoff_google_chat.py \
  --mention-key frontend \
  --webhook-key frontend \
  --thread-key deduction-api-spec-20260411 \
  --mode send \
  --text-only \
  --raw-text "<users/107987990660367540952> 법인 월별 공제금 API 변경 전달."
```

Send an API reply in the same thread:

```bash
python3 ~/plugins/mailman/skills/mailman-handoff/scripts/handoff_google_chat.py \
  --webhook-key frontend \
  --thread-key deduction-api-spec-20260411 \
  --mode send \
  --raw-text-file ./api-message.txt
```

## Resources

- Read `~/plugins/mailman/skills/mailman-handoff/references/google-chat-webhook.md` when you need the webhook and mention constraints.
- Read `~/plugins/mailman/skills/mailman-handoff/references/mention-map.json.example` when you need the mapping format for teammates.
- Read `~/plugins/mailman/skills/mailman-handoff/references/webhook-map.json.example` when you need the mapping format for channels.
- Use `scripts/handoff_google_chat.py` for both draft and send flows.
