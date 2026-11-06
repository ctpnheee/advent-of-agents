"""Day 03 — Gemini + ADK in Python.

Based on the Advent of Agents Day 3 demo (gemini-3-pro-agent-demo), extended to show:
  * a custom Python function tool (get_current_time)
  * Google Search wrapped in its own agent and used via AgentTool,
    because the built-in google_search tool can't share an agent with other tools.
"""

import os
from datetime import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

# Free tier: Search grounding only had quota on gemini-2.5-flash-lite (see day-02/NOTES.md).
# With billing enabled, set AGENT_MODEL=gemini-3.5-flash (or a Gemini 3 Pro model) in .env.
MODEL = os.getenv("AGENT_MODEL", "gemini-2.5-flash-lite")


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
    model=MODEL,
    description="Searches Google for current information and facts.",
    instruction=(
        "Use the google_search tool to answer the question with up-to-date information. "
        "Answer concisely and mention the sources you used."
    ),
    tools=[google_search],
)

root_agent = Agent(
    name="assistant",
    model=MODEL,
    description="A helpful assistant that can search Google and tell the time.",
    instruction=(
        "You are a helpful assistant.\n"
        "- For news, recent events, or facts you are unsure about, call google_search_agent.\n"
        "- For the current date or time, call get_current_time.\n"
        "Answer in the same language the user writes in."
    ),
    tools=[AgentTool(agent=search_agent), get_current_time],
)
