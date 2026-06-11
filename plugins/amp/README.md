# Headroom for Amp

Context compression plugin for [Amp](https://ampcode.com). Compresses large tool outputs before they reach the model, with reversible CCR retrieval.

## Install

```bash
headroom wrap amp
```

This command:

1. Copies `headroom.ts` and `lib.ts` into `.amp/plugins/`
2. Writes `headroom.proxyUrl` into `.amp/settings.json`
3. Starts a local `headroom proxy` on port `8787`

Then in Amp:

1. Open the command palette (`Ctrl+O`)
2. Run `plugins: reload`
3. Continue your thread

## What it does

- Hooks `tool.result` and compresses large outputs through the local Headroom proxy
- Registers `headroom_retrieve` for CCR lookups
- Shows cumulative token savings in the Amp status bar

## Configuration

Workspace settings in `.amp/settings.json`:

| Key | Default | Description |
|-----|---------|-------------|
| `headroom.proxyUrl` | `http://127.0.0.1:8787` | Headroom proxy base URL |
| `headroom.proxyPort` | `8787` | Used when `headroom.proxyUrl` is omitted |
| `headroom.minCompressChars` | `500` | Minimum tool output size to compress |
| `headroom.enabled` | `true` | Set `false` to disable compression |

Install globally instead of per project:

```bash
headroom wrap amp --global
```

## Development

```bash
cd plugins/amp
npm install
npm test
```

Use a local plugin checkout:

```bash
headroom wrap amp --plugin-path ./plugins/amp
```

## License

Apache-2.0
