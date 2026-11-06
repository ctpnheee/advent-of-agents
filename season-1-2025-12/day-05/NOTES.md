# Day 05 — Production Observability

Source: https://adventofagents.com/2025/12/05 · Guide: https://googlecloudplatform.github.io/agent-starter-pack/guide/observability.html

Works on the Day 04 agent (`../day-04/my-agent`). No new agent code here, only cloud setup, SQL, and one fix.

## Two levels of observability
| Level | What | Where | Status |
|---|---|---|---|
| 1. Agent telemetry | One trace per run: LLM calls, tool calls, latency | Cloud Trace | ✅ after fix below |
| 2. Prompt-response logging | Inputs/outputs of every model call as JSONL | GCS bucket → BigQuery | ✅ set up by hand |

The full Starter Pack (non-`--prototype`) provisions level 2 with Terraform; I used the prototype,
so I built it manually to see each piece.

## What I set up
- Enabled `cloudresourcemanager.googleapis.com` and `bigquery.googleapis.com`.
- Bucket `gs://advent-agents-0jzupg-agent-logs` (us-central1, objects deleted after 30 days),
  `roles/storage.objectAdmin` for the Agent Engine service account.
- `LOGS_BUCKET_NAME` in `app/.env`; the Makefile passes it to the deployed agent via `--set-env-vars`,
  which turns on `app_utils/telemetry.py`'s GCS upload.
- BigQuery dataset `agent_logs`:
  - `raw_lines` — external table over `completions/*.jsonl` (CSV trick: one STRING column per line)
  - `messages` — view that parses lines into `completion_id, kind, role, part_type, text, tool_name, tool_args`

```bash
bq --project_id=advent-agents-0jzupg --location=us-central1 query --use_legacy_sql=false < sql/02_tool_usage.sql
```

## What the data showed
**Trace** of "latest AI news about Gemini" (25.7 s total):
```
invocation                                   25.72s
  invoke_agent root_agent                    25.50s
    call_llm → gemini-3-flash-preview         2.08s   (decide to call a tool)
    execute_tool google_search_agent         16.75s   ← the bottleneck
      invoke_agent google_search_agent → LLM + Google Search
    call_llm → gemini-3-flash-preview         6.19s   (write the answer)
```

**BigQuery** (`sql/03_question_to_action.sql`) showed the model turned
"Tìm 1 tin AI mới nhất về Gemini" into the search `"... tháng 12 2024"` → stale news.

## Bugs found through observability
1. **No traces at all.** Agent logs: `Failed to convert project number to project ID … Cloud Resource
   Manager API has not been used`. The agent only knows the project *number*; the trace exporter
   needs the *ID*. Fix: enable Cloud Resource Manager API, redeploy.
2. **Model doesn't know today's date** → searched for Dec 2024. Fix in `app/agent.py`: instructions are
   now functions (`InstructionProvider`) that inject today's date on every call. Local run now searches
   "tháng 11 2026". Needs `make deploy` to reach the cloud agent.

## Gotchas
- zsh: `$P:agent_logs` → `:a` is a path modifier and mangles it. Use `${P}:agent_logs`.
- `bq query "-- comment …"` parses the leading `--` as a flag. Pipe SQL via stdin.
- Trace API wants `startTime` and `endTime` in **UTC**; my laptop clock is local time.
- Telemetry mode `NO_CONTENT` keeps content out of the *spans/logs*, but the GCS upload still has full
  prompts/answers. Treat the bucket as sensitive.
