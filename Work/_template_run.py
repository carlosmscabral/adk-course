"""
Work/_template_run.py — the engine-first starter the rest of the course builds on.

This script wires the four bare-metal primitives of an ADK turn BY HAND so you
can see what a Runner / Session / LlmAgent / Event actually do before you
trust any abstraction:

    InMemorySessionService()          → makes a session
    LlmAgent(...)                     → makes the agent
    Runner(app_name, agent, session)  → glues them together
    runner.run_async(...)             → yields Events; the last one has final text

Run with:

    python Work/_template_run.py

You will need either GOOGLE_API_KEY (AI Studio) or GOOGLE_APPLICATION_CREDENTIALS
(Vertex AI ADC) set in your environment. See Notes/00_Setup/01_InstallAndKey.md.

Copy this file for every new mini-drill — replace the agent and tools, keep the
scaffolding. The repeated typing is the lesson (engine-first per the course's
pedagogy — see ../AGENTS.md).
"""

from __future__ import annotations

import asyncio

# ── 1. The agent type ─────────────────────────────────────────────────────────
# LlmAgent (aliased as Agent) is the workhorse. See the cheat sheet at
# ../Reference/CheatSheets/llmagent_signature.md for every kwarg.
from google.adk.agents import LlmAgent

# ── 2. The runtime ────────────────────────────────────────────────────────────
# Runner drives one turn at a time. It does not own state — it asks the
# session_service to load/save the Session around each run_async call.
from google.adk.runners import Runner

# ── 3. The session service ────────────────────────────────────────────────────
# InMemorySessionService is the dev default. Persistence lives in the process,
# so it dies when the script exits. Swap for DatabaseSessionService or
# VertexAiSessionService in production — see Notes/04_SessionsState/.
from google.adk.sessions import InMemorySessionService

# ── 4. The wire format for messages ───────────────────────────────────────────
# Gemini's Content/Part shape. role="user" for input from the user;
# role="model" comes back from the LLM. See Notes/Detours/GeminiPayload.md.
from google.genai import types


# ── Constants you will edit per drill ─────────────────────────────────────────
APP_NAME = "adk_course_template"
USER_ID = "student"
MODEL_ID = "gemini-2.5-flash"  # the course default; pin a -001 in prod.


def build_agent() -> LlmAgent:
    """Construct the agent for this turn.

    TODO: replace with your agent. Add tools=, sub_agents=, callbacks=, etc.
    as you progress through the course.
    """
    return LlmAgent(
        name="template",
        model=MODEL_ID,
        instruction=(
            "You are a helpful assistant. Answer the user's question concisely. "
            "If you do not know, say so plainly."
        ),
        description="Template agent — replace me per drill.",
        # tools=[...],          # ← Module 03
        # sub_agents=[...],     # ← Module 05
        # before_tool_callback=...,  # ← Module 07
    )


async def main() -> None:
    # 1. Build the session service (one per process is fine for dev).
    session_service = InMemorySessionService()

    # 2. Build the agent (one per Runner; you can have many Runners).
    agent = build_agent()

    # 3. Build the Runner — the glue that hands user messages to the agent
    #    and applies state mutations back to the session.
    runner = Runner(
        app_name=APP_NAME,
        agent=agent,
        session_service=session_service,
    )

    # 4. Create a session. The session id is what you pass back on every
    #    subsequent turn to continue the conversation.
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        # state={"user:name": "Alice"},  # optional seed; see state_prefixes cheat sheet
    )

    # 5. Compose one user message in the Gemini wire format.
    user_message = types.Content(
        role="user",
        parts=[types.Part(text="Hello — say hi back in one sentence.")],
    )

    # 6. Run ONE turn. run_async is an async generator — async for, not await.
    #    Each Event has .author, .content, .actions. Only the last has
    #    is_final_response() == True.
    print(f"--- session_id: {session.id} ---")
    final_text = ""
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=user_message,
    ):
        # Uncomment to see every intermediate event (model thoughts, tool calls):
        # print(f"[event] author={event.author!r} final={event.is_final_response()}")
        if event.is_final_response() and event.content and event.content.parts:
            final_text = event.content.parts[0].text or ""

    print(f"\n--- agent reply ---\n{final_text}\n")


if __name__ == "__main__":
    # asyncio.run is the entrypoint — main() is an async function.
    # See Notes/Detours/PY_async.md if `async for` feels hand-wavy.
    asyncio.run(main())
