# ruff: noqa
"""Day 04 — the Day 03 agent, packaged by Agent Starter Pack for Agent Engine.

Differences from Day 03:
  * Runs on Vertex AI (Google Cloud auth via ADC) instead of a Gemini API key.
  * Billing is enabled, so Google Search grounding works on Gemini 3.x.
  * Exposes `app = App(...)`, which agent_engine_app.py wraps for deployment.
"""

import os
from datetime import datetime
from zoneinfo import ZoneInfo

import google.auth
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

# Project comes from GOOGLE_CLOUD_PROJECT (app/.env locally, set by Agent Engine in the cloud),
# falling back to the ADC / gcloud default.
_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"  # Gemini 3.x models are served from the global endpoint
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

# Template default; override with AGENT_MODEL in app/.env (e.g. gemini-3.5-flash also works here).
MODEL_NAME = os.getenv("AGENT_MODEL", "gemini-3-flash-preview")


def _model() -> Gemini:
    return Gemini(model=MODEL_NAME, retry_options=types.HttpRetryOptions(attempts=3))


# Cities whose IANA zone name differs from the city name (models often guess "Asia/Hanoi").
CITY_ALIASES = {
    "hanoi": "Asia/Ho_Chi_Minh", "ha noi": "Asia/Ho_Chi_Minh", "saigon": "Asia/Ho_Chi_Minh",
    "ho chi minh": "Asia/Ho_Chi_Minh", "vietnam": "Asia/Ho_Chi_Minh", "da nang": "Asia/Ho_Chi_Minh",
}


def get_current_time(timezone: str = "Asia/Ho_Chi_Minh") -> dict:
    """Return the current date and time.

    Args:
        timezone: An IANA timezone such as 'Asia/Ho_Chi_Minh', 'Europe/London', 'America/New_York',
            or a Vietnamese city name like 'Hanoi'. Vietnam uses 'Asia/Ho_Chi_Minh'.
    """
    tz = CITY_ALIASES.get(timezone.split("/")[-1].replace("_", " ").lower(), timezone)
    try:
        now = datetime.now(ZoneInfo(tz))
    except Exception:
        return {
            "status": "error",
            "message": f"Unknown timezone '{timezone}'. Retry with a valid IANA name, e.g. 'Asia/Ho_Chi_Minh'.",
        }
    return {"status": "ok", "timezone": tz, "datetime": now.isoformat(timespec="seconds")}


search_agent = Agent(
    name="google_search_agent",
    model=_model(),
    description="Searches Google for current information and facts.",
    instruction=(
        "Use the google_search tool to answer the question with up-to-date information. "
        "Answer concisely and mention the sources you used."
    ),
    tools=[google_search],
)

root_agent = Agent(
    name="root_agent",
    model=_model(),
    description="A helpful assistant that can search Google and tell the time.",
    instruction=(
        "You are a helpful assistant.\n"
        "- For news, recent events, or facts you are unsure about, call google_search_agent.\n"
        "- For the current date or time, call get_current_time.\n"
        "Answer in the same language the user writes in."
    ),
    tools=[AgentTool(agent=search_agent), get_current_time],
)

app = App(
    root_agent=root_agent,
    name="app",
)
