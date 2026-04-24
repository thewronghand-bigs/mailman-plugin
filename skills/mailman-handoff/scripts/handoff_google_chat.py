#!/usr/bin/env python3
"""
Build or send a Google Chat handoff message.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Draft or send a Google Chat handoff message.")
    parser.add_argument("--title", help="Primary message title.")
    parser.add_argument("--mention-key", help="Team key in mention map, e.g. frontend.")
    parser.add_argument(
        "--mention-map",
        default=str(Path(__file__).resolve().parent.parent / "references" / "mention-map.json"),
        help="Path to mention map JSON file.",
    )
    parser.add_argument("--mention-token", help="Raw Chat mention token, e.g. <users/...>.")
    parser.add_argument("--mention-text", help="Plain text mention fallback, e.g. @프론트.")
    parser.add_argument("--raw-text", help="Send this text as-is without auto formatting.")
    parser.add_argument("--raw-text-file", help="Read message text from a file and send it as-is.")
    parser.add_argument(
        "--text-only",
        action="store_true",
        help="Send only top-level text without cards. Useful for the parent mention summary.",
    )
    parser.add_argument("--bullet", action="append", default=[], help="Message bullet. Repeatable.")
    parser.add_argument("--test-status", help="Short test status line.")
    parser.add_argument("--impact", help="Short impact line.")
    parser.add_argument("--note", action="append", default=[], help="Extra note. Repeatable.")
    parser.add_argument("--mode", choices=["draft", "send"], default="draft")
    parser.add_argument("--output", help="Optional file path to store the rendered message.")
    parser.add_argument("--webhook-url", help="Google Chat incoming webhook URL.")
    parser.add_argument("--webhook-key", help="Team key in webhook map, e.g. frontend.")
    parser.add_argument(
        "--webhook-map",
        default=str(Path(__file__).resolve().parent.parent / "references" / "webhook-map.json"),
        help="Path to webhook map JSON file.",
    )
    parser.add_argument(
        "--webhook-url-env",
        default="GOOGLE_CHAT_WEBHOOK_URL",
        help="Environment variable name for webhook URL fallback.",
    )
    parser.add_argument("--thread-key", help="Optional thread key appended to the webhook URL.")
    parser.add_argument(
        "--allow-non-google-url",
        action="store_true",
        help="Allow non-chat.googleapis.com targets for local testing.",
    )
    return parser.parse_args()


def load_json(path: str) -> dict:
    json_path = Path(path)
    if not json_path.exists():
        return {}

    with json_path.open() as fp:
        data = json.load(fp)

    return data if isinstance(data, dict) else {}


def first_nested_entry(data: dict, top_level_key: str | None, nested_key: str) -> dict:
    if not top_level_key:
        return {}

    entry = data.get(top_level_key, {})
    if not isinstance(entry, dict):
        return {}

    nested_entries = entry.get(nested_key)
    if isinstance(nested_entries, dict) and nested_entries:
        first_value = next(iter(nested_entries.values()))
        if isinstance(first_value, dict):
            return first_value

    return entry


def load_mention_entry(path: str, mention_key: str | None) -> dict:
    return first_nested_entry(
        data=load_json(path),
        top_level_key=mention_key,
        nested_key="users",
    )


def load_webhook_entry(path: str, webhook_key: str | None) -> dict:
    return first_nested_entry(
        data=load_json(path),
        top_level_key=webhook_key,
        nested_key="channels",
    )


def resolve_mention(args: argparse.Namespace) -> str:
    entry = load_mention_entry(args.mention_map, args.mention_key)
    token = args.mention_token or entry.get("token") or ""
    text = args.mention_text or entry.get("fallbackText") or entry.get("displayName") or ""

    mention = token.strip() or text.strip()
    return mention


def strip_mention_tokens(text: str) -> str:
    return re.sub(r"<users/[^>]+>\s*", "", text).strip()


def to_chat_html(text: str) -> str:
    return html.escape(text).replace("\n", "<br>")


def build_message(args: argparse.Namespace) -> str:
    raw_text = resolve_raw_text(args)
    if raw_text is not None:
        return raw_text

    if not args.title:
        raise ValueError("Either --title or --raw-text/--raw-text-file is required.")

    lines: list[str] = []
    mention = resolve_mention(args)
    first_line = f"{mention} {args.title}".strip()
    lines.append(first_line)

    for bullet in args.bullet:
        if bullet.strip():
            lines.append(f"- {bullet.strip()}")

    if args.test_status:
        lines.append(f"- 테스트: {args.test_status.strip()}")

    if args.impact:
        lines.append(f"- 영향: {args.impact.strip()}")

    for note in args.note:
        if note.strip():
            lines.append(f"- 참고: {note.strip()}")

    return "\n".join(lines).strip()


def resolve_raw_text(args: argparse.Namespace) -> str | None:
    if args.raw_text and args.raw_text_file:
        raise ValueError("Use only one of --raw-text or --raw-text-file.")

    if args.raw_text:
        return args.raw_text.strip()

    if args.raw_text_file:
        return Path(args.raw_text_file).read_text().strip()

    return None


def maybe_write_output(message: str, output_path: str | None) -> None:
    if not output_path:
        return
    path = Path(output_path)
    path.write_text(message + "\n")


def resolve_webhook_url(args: argparse.Namespace) -> str:
    webhook_entry = load_webhook_entry(args.webhook_map, args.webhook_key)
    webhook_url = args.webhook_url or webhook_entry.get("webhookUrl") or os.getenv(args.webhook_url_env, "")
    if not webhook_url:
        raise ValueError(
            "Webhook URL is required for send mode. "
            f"Pass --webhook-url, use --webhook-key, or set ${args.webhook_url_env}.",
        )
    return webhook_url


def build_target_url(webhook_url: str, thread_key: str | None) -> str:
    if not thread_key:
        return webhook_url

    parsed = urllib.parse.urlparse(webhook_url)
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    reply_option = ("messageReplyOption", "REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD")

    if reply_option not in query:
        query.append(reply_option)

    return parsed._replace(query=urllib.parse.urlencode(query)).geturl()


def validate_target_url(url: str, allow_non_google_url: bool) -> None:
    if allow_non_google_url:
        return

    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "chat.googleapis.com":
        raise ValueError(
            "Refusing to send to a non-Google Chat webhook URL without --allow-non-google-url.",
        )


def parse_api_spec(raw_text: str) -> tuple[str, str | None, str | None, str | None]:
    lines = [line.rstrip() for line in raw_text.splitlines()]
    title = ""
    method_line = None
    request_body = None
    response_body = None

    if lines and lines[0].startswith("*") and lines[0].endswith("*"):
        title = lines[0].strip("*").strip()
    else:
        title = strip_mention_tokens(lines[0]) if lines else ""

    method_match = re.search(r"(?m)^(GET|POST|PUT|PATCH|DELETE)\s+.+$", raw_text)
    if method_match:
        method_line = method_match.group(0).strip()

    request_match = re.search(r"요청\s*```(.*?)```", raw_text, re.DOTALL)
    if request_match:
        request_body = request_match.group(1).strip("\n").strip()

    response_match = re.search(r"응답\s*```(.*?)```", raw_text, re.DOTALL)
    if response_match:
        response_body = response_match.group(1).strip("\n").strip()

    if request_body is None and response_body is None:
        code_match = re.search(r"```(.*?)```", raw_text, re.DOTALL)
        if code_match:
            block = code_match.group(1).strip("\n")
            block_lines = block.splitlines()
            if block_lines and method_line is None:
                method_line = block_lines[0].strip()
            response_body = "\n".join(block_lines[1:]).strip() if len(block_lines) > 1 else ""

    return title, method_line, request_body, response_body


def parse_summary_sections(raw_text: str) -> tuple[str, list[tuple[str | None, list[str]]]]:
    stripped_text = raw_text.strip()
    if not stripped_text:
        return "Handoff", []

    blocks = [block.strip() for block in re.split(r"\n\s*\n", stripped_text) if block.strip()]
    title = strip_mention_tokens(blocks[0].splitlines()[0]).strip() if blocks else "Handoff"
    sections: list[tuple[str | None, list[str]]] = []

    for block in blocks[1:]:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue

        section_title = lines[0].rstrip(":")
        section_items = lines[1:]

        if not section_items:
            sections.append((None, [section_title]))
            continue

        sections.append((section_title, section_items))

    return title or "Handoff", sections


def format_code_html(text: str) -> str:
    normalized_text = text
    try:
        normalized_text = json.dumps(
            json.loads(text),
            ensure_ascii=False,
            indent=2,
        )
    except json.JSONDecodeError:
        normalized_text = text

    lines = normalized_text.splitlines()
    escaped_lines = [html.escape(it).replace(" ", "&nbsp;") for it in lines]
    return '<font face="monospace">' + "<br>".join(escaped_lines) + "</font>"


def build_payload(message: str, args: argparse.Namespace) -> dict:
    raw_text = resolve_raw_text(args)
    if args.text_only:
        payload: dict[str, object] = {
            "text": message,
        }
        if args.thread_key:
            payload["thread"] = {"threadKey": args.thread_key}
        return payload

    if raw_text is None:
        title = args.title or "Handoff"
        widgets: list[dict] = []

        bullets = [it.strip() for it in args.bullet if it.strip()]
        if bullets:
            widgets.append(
                {
                    "textParagraph": {
                        "text": "<b>변경 내용</b><br>" + "<br>".join(f"• {to_chat_html(it)}" for it in bullets),
                    },
                },
            )
        if args.impact:
            widgets.append(
                {
                    "decoratedText": {
                        "topLabel": "영향",
                        "text": to_chat_html(args.impact.strip()),
                    },
                },
            )
        if args.note:
            notes = [it.strip() for it in args.note if it.strip()]
            if notes:
                widgets.append(
                    {
                        "textParagraph": {
                            "text": "<b>참고</b><br>" + "<br>".join(f"• {to_chat_html(it)}" for it in notes),
                        },
                    },
                )

        payload: dict[str, object] = {
            "text": message,
            "cardsV2": [
                {
                    "cardId": f"google-chat-dev-handoff-{hashlib.sha1(message.encode('utf-8')).hexdigest()[:12]}",
                    "card": {
                        "header": {
                            "title": strip_mention_tokens(message) or title,
                        },
                        "sections": [
                            {
                                "widgets": widgets or [{"textParagraph": {"text": to_chat_html(message)}}],
                            },
                        ],
                    },
                },
            ],
        }
    else:
        title, method_line, request_body, response_body = parse_api_spec(raw_text)
        sanitized_raw_text = strip_mention_tokens(raw_text)
        sections: list[dict] = []
        if method_line:
            sections.append(
                {
                    "widgets": [
                        {
                            "decoratedText": {
                                "topLabel": "API",
                                "text": f"<b>{to_chat_html(method_line)}</b>",
                            },
                        },
                    ],
                },
            )
        if request_body:
            sections.append(
                {
                    "header": "요청",
                    "widgets": [
                        {
                            "textParagraph": {
                                "text": format_code_html(request_body),
                            },
                        },
                    ],
                },
            )
        if response_body:
            sections.append(
                {
                    "header": "응답",
                    "widgets": [
                        {
                            "textParagraph": {
                                "text": format_code_html(response_body),
                            },
                        },
                    ],
                },
            )
        if not sections:
            summary_title, sections = parse_summary_sections(sanitized_raw_text)
            title = summary_title or title
            card_sections: list[dict] = []

            if sections:
                for section_title, section_items in sections:
                    if section_title is None:
                        card_sections.append(
                            {
                                "widgets": [
                                    {
                                        "textParagraph": {
                                            "text": "<br>".join(to_chat_html(it) for it in section_items),
                                        },
                                    },
                                ],
                            },
                        )
                        continue

                    bullet_items = [it[2:].strip() if it.startswith("- ") else it for it in section_items]
                    card_sections.append(
                        {
                            "header": section_title,
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": "<br>".join(f"• {to_chat_html(it)}" for it in bullet_items),
                                    },
                                },
                            ],
                        },
                    )
            else:
                card_sections.append(
                    {
                        "widgets": [
                            {
                                "textParagraph": {
                                    "text": to_chat_html(sanitized_raw_text),
                                },
                            },
                        ],
                    },
                )

            sections = card_sections

        payload = {
            "cardsV2": [
                {
                    "cardId": f"google-chat-dev-handoff-raw-{hashlib.sha1(raw_text.encode('utf-8')).hexdigest()[:12]}",
                    "card": {
                        "header": {
                            "title": title or "API Handoff",
                        },
                        "sections": sections,
                    },
                },
            ],
        }

    if args.thread_key:
        payload["thread"] = {"threadKey": args.thread_key}

    if "text" not in payload and raw_text is not None and re.search(r"<users/[^>]+>", raw_text):
        payload["text"] = raw_text.splitlines()[0].strip()

    return payload


def send_message(message: str, args: argparse.Namespace) -> None:
    webhook_url = resolve_webhook_url(args)
    target_url = build_target_url(webhook_url, args.thread_key)
    validate_target_url(target_url, args.allow_non_google_url)
    payload = json.dumps(build_payload(message=message, args=args)).encode("utf-8")
    request = urllib.request.Request(
        target_url,
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request) as response:
            body = response.read().decode("utf-8", errors="replace")
            print(f"[OK] Sent message. status={response.status}")
            if body:
                print(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"[ERROR] HTTP {exc.code}")
        if body:
            print(body)
        raise


def main() -> int:
    args = parse_args()
    message = build_message(args)
    maybe_write_output(message, args.output)

    if args.mode == "draft":
        print(message)
        return 0

    send_message(message, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
