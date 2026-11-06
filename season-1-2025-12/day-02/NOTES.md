# Day 02 — Hello World with YAML

Source: https://adventofagents.com/2025/12/02

## What I built
A config-based ADK agent (`search_agent/root_agent.yaml`) running on `gemini-2.5-flash-lite`
with the built-in `google_search` tool — no Python code.

## How to run
```bash
# 1. Put your Gemini API key in search_agent/.env (GOOGLE_API_KEY=...) — this file is git-ignored
# 2. From this folder (day-02/):
uvx --from google-adk adk web          # browser UI at http://localhost:8000
# or in the terminal:
uvx --from google-adk adk run search_agent
```

## Key takeaways
- `adk create --type=config <name>` scaffolds `root_agent.yaml` + `.env`.
- A YAML agent needs `name`, `model`, `instruction`; `tools` adds built-ins like `google_search`.
- `adk web` serves every agent folder in the current directory.

## Try next
- Add `sub_agents` (multi-agent in YAML)
- Add an MCP toolset — https://google.github.io/adk-docs/tools/third-party/

## Questions / notes
- **429 RESOURCE_EXHAUSTED with `google_search`**: on the free tier, Search grounding had no quota
  for `gemini-3.5-flash`, `gemini-3-flash-preview`, `gemini-3.1-flash-lite` (plain text calls worked).
  `gemini-2.5-flash-lite` works with Search on the free tier. Enabling billing should unlock the newer models.
