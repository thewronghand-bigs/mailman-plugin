# Google Chat webhook notes

- Incoming webhooks are one-way delivery endpoints for a specific Google Chat space.
- This skill sends JSON in the form:

```json
{
  "text": "message body"
}
```

- Raw mention tokens in text use the format `<users/{user}>`.
- If you only know a teammate name and not the Chat user token, use a plain-text fallback such as `@프론트`.
- To start or reply in a thread, use `thread.threadKey` in the request body.
- When replying by webhook, add `messageReplyOption=REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD` to the webhook URL.
- Code blocks displayed in Chat should use plain triple backticks. If you send ```json, Chat shows `json` as visible text.
- For local testing, use `--allow-non-google-url` with a local HTTP server.
- For real delivery, prefer a webhook URL provided explicitly by the user or from an approved local secret source.
