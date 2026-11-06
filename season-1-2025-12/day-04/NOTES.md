# Day 04 — Source-Based Deployment to Agent Engine

Source: https://adventofagents.com/2025/12/04

## What I did
1. New GCP project `advent-agents-0jzupg` + billing + budget alert, ADC login
   (`gcloud auth application-default login`), enabled Vertex AI / Storage / Cloud Build / Logging / Trace.
2. Scaffolded with Agent Starter Pack (prototype = no Terraform / CI/CD):
   ```bash
   uvx agent-starter-pack create my-agent -a adk_base -d agent_engine --prototype --region us-central1
   ```
3. Replaced `app/agent.py` with my Day 03 agent (search sub-agent via `AgentTool` + `get_current_time`),
   now on Vertex AI with `gemini-3-flash-preview`.
4. `make playground` locally → `make deploy` → queried it with `scripts/query_remote.py`.

## Layout
| File | Role |
|---|---|
| `app/agent.py` | the agent (`root_agent`) + `app = App(...)` |
| `app/agent_engine_app.py` | `AdkApp` wrapper: logging, telemetry, feedback — the deploy entrypoint |
| `app/app_utils/deploy.py` | uploads **source** (`./app` + requirements) to Agent Engine |
| `app/.env` | `GOOGLE_CLOUD_PROJECT=...` (git-ignored) |
| `scripts/query_remote.py` | chat with the deployed agent (session + streaming events) |
| `scripts/delete_remote.py` | delete the deployed agent |

## Commands
```bash
cd my-agent
make playground                                   # local, http://localhost:8501 → pick "app"
make deploy                                       # create/update on Agent Engine (~3–5 min)
uv run python scripts/query_remote.py "question"  # call the cloud agent
uv run python scripts/delete_remote.py            # clean up when done
```

## Key takeaways
- **Source-based deployment**: ship code + requirements and let Agent Engine build it, instead of
  pickling a live agent object (no more serialization / module-path errors).
- Local vs cloud auth: locally ADC (my account); in Agent Engine a service account
  (`service-<project-number>@gcp-sa-aiplatform-re.iam.gserviceaccount.com`).
- Agent Engine owns sessions: `async_create_session` → `async_stream_query(session_id=...)`.
- With billing on Vertex AI, Google Search grounding works on Gemini 3.x (it 429'd on the free AI Studio tier).

## Gotchas hit
- **Wrong project**: the template resolves the project via `google.auth.default()`, which fell back to
  my gcloud default project. `make playground` read `app/.env`, `make deploy` didn't → 403 on the
  other project. Fix: Makefile now `-include app/.env` and passes `--project=$(GOOGLE_CLOUD_PROJECT)`.
- **Cost defaults**: template deploys `min-instances=1, cpu=4, memory=8Gi` (always on). For learning I use
  `--min-instances=0 --max-instances=1 --cpu=1 --memory=2Gi` (override via `DEPLOY_SIZING`).
  Trade-off: first request after idle has a cold start.
- **aiohttp `assert self._connector is not None`**: `client().agent_engines.get(...)` let the
  `vertexai.Client` be garbage-collected, closing its HTTP session. Keep a reference to the client.
