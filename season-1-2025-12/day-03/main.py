"""Run the Day 03 agent from code (no web UI), the way the Day 3 demo does.

Usage:  uv run python main.py "what's the latest AI news?"
"""

import asyncio
import sys

from dotenv import load_dotenv

load_dotenv("search_agent/.env")

from google.adk.runners import Runner  # noqa: E402
from google.adk.sessions import InMemorySessionService  # noqa: E402
from google.genai import types  # noqa: E402

from search_agent.agent import root_agent  # noqa: E402

APP_NAME, USER_ID, SESSION_ID = "day03_app", "user_default", "session_01"


async def ask(query: str) -> None:
    session_service = InMemorySessionService()
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

    message = types.Content(role="user", parts=[types.Part(text=query)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        for call in event.get_function_calls():
            print(f"[tool call] {call.name}({call.args})")
        if event.is_final_response() and event.content and event.content.parts:
            print("Agent:", event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(ask(" ".join(sys.argv[1:]) or "What time is it in Hanoi, and what's the latest AI news?"))
