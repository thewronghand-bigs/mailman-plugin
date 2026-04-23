# Mailman Codex Plugin

Standalone Codex Desktop plugin package for pulling Google Chat bot messages into the current Codex conversation.

This directory is meant to be self-contained so it can either:

- live inside this repository while we iterate, or
- become its own public plugin repository later without much reshuffling

Once installed, the short skill name `mailman` is available. The longer alias `mailman-sandbox` is kept for compatibility with earlier experiments.

## What is in here

- `.codex-plugin/plugin.json`: plugin manifest shown in Codex Desktop
- `skills/mailman/SKILL.md`: primary user-invokable skill
- `skills/mailman-sandbox/SKILL.md`: compatibility alias
- `scripts/extract_google_chat_messages.js`: browser extraction snippet
- `scripts/import_snapshot.sh`: snapshot import wrapper
- `runtime/`: bundled Mailman snapshot runtime
- `marketplace.example.json`: local marketplace example for testing
- `bootstrap.sh`: helper for home-local plugin registration

## Local testing in Codex Desktop

For a local install before marketplace publishing:

1. Put this plugin at `~/plugins/mailman`
2. Run `bash bootstrap.sh`
3. Edit `runtime/config.json`
4. Restart Codex Desktop if the plugin list does not refresh

That writes or updates:

- `~/.agents/plugins/marketplace.json`
- `~/plugins/mailman/runtime/config.json`

## Runtime setup

```bash
cd runtime
cp config.example.json config.json
bun install
```

In a sandboxed workspace:

```bash
export MAILMAN_HOME="$PWD/.mailman"
mkdir -p "$MAILMAN_HOME"
```

Use browser tools to open Google Chat, extract JSON to `$PWD/.mailman/chat.json`, then:

```bash
MAILMAN_HOME="$PWD/.mailman" \
MAILMAN_SNAPSHOT_FILE="$PWD/.mailman/chat.json" \
bash scripts/import_snapshot.sh myspace
```

Read latest threads:

```bash
MAILMAN_HOME="$PWD/.mailman" bash runtime/fetch.sh myspace specbot 3
```

## Publishing notes

Packaging this directory correctly is only the first half of the job. To make Mailman appear in the Codex Desktop plugin menu for other people, this package still needs to be distributed through whatever plugin marketplace or catalog your users' Codex Desktop instances read from.

Use [PUBLISHING.md](./PUBLISHING.md) as the handoff checklist for splitting this into its own repo and preparing that distribution step.
