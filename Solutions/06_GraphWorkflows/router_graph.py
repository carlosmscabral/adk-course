"""Gate-keeper solution for Module 06 mini-drill.

Builds a 3-node graph that routes on input length:

    START → router → (expert_A | expert_B) → merger

  ≤ 10 words → expert_A (concise specialist)
  > 10 words → expert_B (in-depth specialist)

Run with: python router_graph.py
Requires: ADK 2.0, a configured Gemini API key (or Vertex auth).
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from uuid import uuid4

from google.adk.agents import LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.run_config import RunConfig
from google.adk.agents.workflow.base_node import START
from google.adk.agents.workflow.events.event import Event
from google.adk.agents.workflow.function_node import FunctionNode
from google.adk.agents.workflow.workflow_agent import WorkflowAgent
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai.types import Content, ModelContent, Part

MODEL = "gemini-2.5-flash"
APP_NAME = "router_graph"


# ── Route labels as constants (no magic strings) ────────────────────


class Routes:
    SHORT = "SHORT"
    LONG = "LONG"


# ── Experts ─────────────────────────────────────────────────────────


expert_a = LlmAgent(
    name="expert_a_concise",
    model=MODEL,
    description="Concise specialist. Answers in one short sentence.",
    instruction=(
        "Answer the user's question in exactly one short sentence. "
        "No lists. No preamble. ≤ 25 words."
    ),
)

expert_b = LlmAgent(
    name="expert_b_indepth",
    model=MODEL,
    description="In-depth specialist. Multi-paragraph explanations.",
    instruction=(
        "Answer the user's question with a thorough multi-paragraph "
        "explanation. Include relevant trade-offs and at least one "
        "concrete example."
    ),
)


# ── Router (FunctionNode) ───────────────────────────────────────────


async def route_by_length(node_input: Content) -> AsyncGenerator:
    """Decide SHORT vs LONG by word count of the user's text."""
    text = ""
    if node_input and node_input.parts:
        text = node_input.parts[0].text or ""
    n_words = len(text.split())
    route = Routes.SHORT if n_words <= 10 else Routes.LONG

    # Stash the routing decision in state for inspection.
    yield Event(state={"route": route, "n_words": n_words})

    # Pass the user's content to the chosen expert.
    yield Content(parts=[Part(text=text)])

    # Signal which branch to take.
    yield Event(route=route)


router_node = FunctionNode(route_by_length, name="LengthRouter")


# ── Mergers (one per expert, prepends a label) ──────────────────────


async def label_short(node_input: Content) -> AsyncGenerator:
    text = ""
    if node_input and node_input.parts:
        text = node_input.parts[0].text or ""
    yield ModelContent(parts=[Part.from_text(text=f"SHORT-ANSWER: {text}")])


async def label_long(node_input: Content) -> AsyncGenerator:
    text = ""
    if node_input and node_input.parts:
        text = node_input.parts[0].text or ""
    yield ModelContent(parts=[Part.from_text(text=f"LONG-ANSWER: {text}")])


merger_short = FunctionNode(label_short, name="MergerShort")
merger_long = FunctionNode(label_long, name="MergerLong")


# ── Workflow ────────────────────────────────────────────────────────


root_agent = WorkflowAgent(
    name="router_graph",
    edges=[
        (START, router_node),
        (router_node, expert_a, merger_short, Routes.SHORT),
        (router_node, expert_b, merger_long, Routes.LONG),
    ],
)


# ── Driver ──────────────────────────────────────────────────────────


async def run_one(prompt: str) -> None:
    print(f"\n=== INPUT: {prompt!r} ===")
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, user_id="drill_user"
    )

    user_content = Content(role="user", parts=[Part(text=prompt)])
    ctx = InvocationContext(
        session_service=session_service,
        agent=root_agent,
        invocation_id=str(uuid4()),
        session=session,
        user_content=user_content,
        run_config=RunConfig(),
    )

    async for event in root_agent.run_async(parent_context=ctx):
        if isinstance(event, ModelContent) and event.parts:
            print(f"AGENT_OUTPUT: {event.parts[0].text}")

    print(
        f"STATE: route={session.state.get('route')!r} "
        f"n_words={session.state.get('n_words')}"
    )


async def main() -> None:
    prompts = [
        "What is Python?",  # 3 words → SHORT
        "Define recursion.",  # 2 words → SHORT
        (
            "Explain how Python's GIL works and the trade-offs against "
            "free-threaded builds."
        ),  # 12 words → LONG
    ]
    for p in prompts:
        await run_one(p)


if __name__ == "__main__":
    asyncio.run(main())
