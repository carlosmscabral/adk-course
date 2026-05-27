"""Solution to Notes/02_FirstAgent/08_MiniDrill — gate-keeper.

Run:
    python Solutions/02_FirstAgent/hello_agent.py "say hi in pirate"

Requires GOOGLE_API_KEY in a .env at the project root (or any parent dir).
"""

from __future__ import annotations

import asyncio
import sys
import uuid

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

APP_NAME = "hello"
USER_ID = "cli"


async def main(user_text: str) -> None:
    load_dotenv()

    agent = LlmAgent(
        name="greeter",
        model="gemini-2.5-flash",
        instruction="Reply in one short sentence. Be friendly.",
        description="Greets the user.",
    )

    session_service = InMemorySessionService()
    session_id = str(uuid.uuid4())
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session_id,
    )

    runner = Runner(
        app_name=APP_NAME, agent=agent, session_service=session_service,
    )

    new_message = types.Content(
        role="user", parts=[types.Part(text=user_text)],
    )

    final_text: str | None = None
    async for event in runner.run_async(
        user_id=USER_ID, session_id=session_id, new_message=new_message,
    ):
        if (
            event.is_final_response()
            and event.content
            and event.content.parts
            and event.content.parts[0].text
        ):
            final_text = event.content.parts[0].text

    if final_text is None:
        sys.exit("no final response from agent")

    print(final_text)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('usage: hello_agent.py "your message here"')
    asyncio.run(main(sys.argv[1]))
