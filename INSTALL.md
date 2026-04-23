# Install

This package is the Codex Desktop plugin distribution candidate for Mailman.

## Recommended team setup

Use a separate shared marketplace repository for teammate installs.

The intended production setup is:

- plugin repo: `mailman-plugin`
- marketplace repo: `company-local-marketplace`

Then teammates install with a single command from the marketplace repo:

```bash
bash install-mailman-plugin.sh https://github.com/your-org/mailman-plugin.git
```

That installer should:

- clone or update the plugin into `~/plugins/mailman`
- register `mailman` in `~/.agents/plugins/marketplace.json`
- copy existing Mailman config when available
- create `runtime/config.json` if missing
- run `bun install` inside `runtime/`

If the plugin does not appear immediately, restart Codex Desktop.

## Local testing before the repo split

Copy or clone this package so the plugin root is:

```text
~/plugins/mailman
```

Then run:

```bash
cd ~/plugins/mailman
bash bootstrap.sh
```

## Runtime config

```bash
cd runtime
cp config.example.json config.json
bun install
```
