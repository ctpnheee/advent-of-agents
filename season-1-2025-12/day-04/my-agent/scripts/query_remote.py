"""Chat with the agent deployed on Vertex AI Agent Engine.

Usage:
  uv run python scripts/query_remote.py "Mấy giờ ở Hà Nội?"
  uv run python scripts/query_remote.py            # interactive: type messages, empty line to quit
"""

import asyncio
import sys

from _common import client, deployed_agent_name

USER_ID = "nhi"


def print_event(event: dict) -> None:
    """Events come back as plain dicts (the JSON form of ADK events)."""
    for part in (event.get("content") or {}).get("parts", []):
        if call := part.get("function_call"):
            print(f"  [tool call] {call['name']}({call.get('args')})")
        elif part.get("function_response"):
            print(f"  [tool result] {part['function_response']['name']}")
        elif text := part.get("text"):
            print(f"Agent ({event.get('author')}): {text}")


async def main(first_message: str | None) -> None:
    name = deployed_agent_name()
    vertex = client()  # keep a reference: if the client is garbage-collected, its HTTP session closes
    agent = vertex.agent_engines.get(name=name)
    print(f"Connected to {name}")

    # The session lives in Agent Engine, so the agent remembers earlier turns.
    session = await agent.async_create_session(user_id=USER_ID)
    print(f"Session: {session['id']}\n")

    message = first_message
    while True:
        if message is None:
            message = input("You: ").strip()
            if not message:
                break
        async for event in agent.async_stream_query(user_id=USER_ID, session_id=session["id"], message=message):
            print_event(event)
        if first_message:
            break
        message = None


if __name__ == "__main__":
    asyncio.run(main(" ".join(sys.argv[1:]) or None))
