# Phinite plugin for OpenCode

Build, ship, run and debug **Phinite agent graphs** from OpenCode. The plugin connects OpenCode to the hosted
**Phinite MCP server** (`https://mcp.dev.phinite.ai/mcp`, remote with OAuth) and adds the Phinite playbook as skills, commands and the
`phinite-builder` subagent. It is generated from the Claude plugin, so both behave the same.

## Install

OpenCode plugins are JavaScript hooks and have no package format for commands, skills and MCP servers, so
`install.py` copies them into an OpenCode config folder and adds the `phinite` server to its `opencode.json`:

```text
git clone https://github.com/Auto-AI-Labs/phinite-opencode-plugin phinite-opencode
python phinite-opencode/install.py                    # all projects: ~/.config/opencode
python phinite-opencode/install.py --project <repo>   # one project: <repo>/.opencode
```

Restart OpenCode. Re-run `install.py` after `git pull` to update; `--uninstall` removes everything it added.

- Only the server, without the skills: `opencode mcp add phinite --url https://mcp.dev.phinite.ai/mcp --global`.
- To work on the plugin itself, open this folder in OpenCode: its `opencode.json` and `AGENTS.md` load the server
  and the rules. (OpenCode 1.x puts servers directly under `"mcp"`; `install.py` detects that.)
- To use another server (production or a local one), change `url` for `phinite` in `opencode.json`.

You need Python 3.9+ for the project script. No Phinite token is stored in the repo.

## Sign in

Run `opencode mcp auth phinite` (or `/mcps` in OpenCode), or `/phinite-login`. A browser opens on the Phinite login
(Google, GitHub or email); pick the org and the workspace. To switch workspace: `opencode mcp logout phinite`,
then sign in again and pick another one.

## Use

| Command | What it does |
|---|---|
| `/phinite-login [workspace]` | Sign in, check the sign-in, or switch workspace |
| `/phinite-new <folder> [schema] [idea]` | Scaffold a use-case project and design its graphs with you |
| `/phinite-deploy <folder>` | Dry run, then deploy: tools upserted (published when changed), graphs created or updated |
| `/phinite-test <graph> [message \| user_variables]` | Chat or run the graph autonomously, read the log, diagnose |
| `/phinite-ship <graph> [env]` | Publish → build → environment → trigger or Chat API → API key → call it from outside |
| `/phinite-logs <workflow_id>` | Explain a run: tool calls, inputs, outputs, variables, errors |
| `/phinite-eval <graph> [focus]` | Evaluate with LLM judges: cases, metrics, failures and fixes |

Or just ask the agent to build a use case: the `phinite-builder` subagent (`@phinite-builder`) takes it end to end.

## What's inside

- **Skills** (the same as the Claude plugin's, from the Phinite playbook): `phinite-design`, `phinite-ship`,
  `phinite-debug`, `phinite-api` and `phinite-project`, plus `phinite-quality` for evaluations (LLM judges,
  custom metrics, production scoring).
- **A local project script**, `skills/phinite-project/scripts/phinite_project.py` (Python 3.9+, standard library
  only). It scaffolds use-case folders from `templates/`, runs `graph_spec.py` on your machine, bundles the project
  and sends files through the server's upload links. The hosted server can't read your disk.
- `tests/`: the offline tests for that script: `python -m unittest tests/test_offline.py`.

The MCP tools and the rules they apply are listed in the
[phinite-mcp README](https://github.com/Auto-AI-Labs/phinite-mcp#tools).

## Security notes

- **No secrets on disk or in the chat.** The client stores and refreshes the OAuth token; the assistant never sees
  it. Env values go from your `.env` straight to an upload link and never pass through the chat.
- **Upload links** are valid for 15 minutes and for one purpose. The project script accepts only https links on
  `*.phinite.ai` (or the `PHINITE_MCP_URL` host, or localhost) with the `/u/<ticket>` path, so a link from a file,
  web page or message is refused.
- **Hidden files** (`.env`, `.git`…) in folders are never sent, and `KNOWLEDGE` files must be inside the project.
- **Env variables are workspace-wide**: prefix a use case's own secrets (`MYUC_SLACK_TOKEN`), and the assistant asks
  before overwriting a name that already exists.
- **`graph_spec.py` is code**: `deploy` runs it on your machine. Deploy only projects you wrote or trust.
