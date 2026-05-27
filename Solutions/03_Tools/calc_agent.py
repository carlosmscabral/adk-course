"""Solution to Notes/03_Tools/11_MiniDrill — gate-keeper.

Run:
    python Solutions/03_Tools/calc_agent.py

Asks the agent four arithmetic questions in one session. Prints one
final response per question. Bonus: prompts for a divide-by-zero so
you can see the structured-error path.
"""

from __future__ import annotations

import asyncio
import uuid

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

APP_NAME = "calc"
USER_ID = "cli"


def add(a: float, b: float) -> float:
    """Return the sum of two numbers."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Return a minus b."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Return the product of two numbers."""
    return a * b


def divide(a: float, b: float) -> dict:
    """Return a divided by b. Returns an error dict if b is 0."""
    if b == 0:
        return {"error": "division_by_zero", "a": a, "b": b}
    return {"result": a / b}


async def ask(runner: Runner, session_id: str, question: str) -> str | None:
    msg = types.Content(role="user", parts=[types.Part(text=question)])
    final_text: str | None = None
    async for event in runner.run_async(
        user_id=USER_ID, session_id=session_id, new_message=msg,
    ):
        if (
            event.is_final_response()
            and event.content
            and event.content.parts
            and event.content.parts[0].text
        ):
            final_text = event.content.parts[0].text
    return final_text


async def main() -> None:
    load_dotenv()

    agent = LlmAgent(
        name="calc",
        model="gemini-2.5-flash",
        instruction=(
            "You are a calculator. ALWAYS use the provided tools to "
            "compute arithmetic; never compute in your head. State the "
            "numeric result clearly."
        ),
        description="Performs arithmetic via tools.",
        tools=[add, subtract, multiply, divide],
    )

    session_service = InMemorySessionService()
    session_id = str(uuid.uuid4())
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session_id,
    )

    runner = Runner(
        app_name=APP_NAME, agent=agent, session_service=session_service,
    )

    questions = [
        "What is 3 + 4?",
        "What is 7 * 5?",
        "What is 20 / 4?",
        "What is 10 - 5?",
        "What is 10 / 0?",   # bonus — error path
    ]

    for q in questions:
        reply = await ask(runner, session_id, q)
        print(f"Q: {q}")
        print(f"A: {reply}\n")


if __name__ == "__main__":
    asyncio.run(main())
