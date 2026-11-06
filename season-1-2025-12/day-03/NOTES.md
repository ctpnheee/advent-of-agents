# Day 03 — Gemini + ADK (Python)

Source: https://adventofagents.com/2025/12/03
Demo it's based on: https://github.com/GoogleCloudPlatform/devrel-demos/tree/main/ai-ml/agent-labs/gemini-3-pro-agent-demo

## What I built
Moved from YAML (Day 2) to a **Python** ADK agent:

```
assistant (root_agent)
├── get_current_time        ← custom Python function tool
└── google_search_agent     ← sub-agent with built-in google_search, used via AgentTool
```

- `search_agent/agent.py` — agent definitions (what `adk web` loads)
- `main.py` — runs the agent from code with `Runner` + `InMemorySessionService` (no UI)

## How to run
```bash
uv sync                                   # install deps into .venv
# API key lives in search_agent/.env (git-ignored)
uv run adk web                            # browser UI at http://localhost:8000
uv run python main.py "latest AI news?"   # run from code, prints tool calls + answer
```
Optional: add `AGENT_MODEL=gemini-3.5-flash` to `.env` once billing is enabled.

## Key takeaways
- A Python agent folder = `__init__.py` (`from . import agent`) + `agent.py` exposing `root_agent`.
- **Function tools**: any Python function with type hints + docstring. The docstring is what the model
  reads to decide when and how to call it, so write it for the model.
- **Built-in `google_search` can't be mixed with other tools in the same agent** → wrap it in its own
  agent and expose it with `AgentTool(agent=...)`.
- `adk web` hides the plumbing; `main.py` shows it: `Runner` drives the loop, `SessionService` stores
  the conversation, and `run_async` yields **events** (tool calls, tool results, final answer).

## Bugs hit
- Model called `get_current_time("Asia/Hanoi")` — not a real IANA zone (Vietnam is `Asia/Ho_Chi_Minh`).
  Fixed by mapping city names to zones, documenting valid values in the docstring, and returning an
  error message that tells the model how to retry. Lesson: tools should be forgiving and their errors
  should be instructions for the model.

## Not covered (from the Day 3 page)
- Computer use and Live API (voice/video) — Live API comes back on Day 12.
- `uvx agent-starter-pack create` — production template; revisit on Day 4–5.
