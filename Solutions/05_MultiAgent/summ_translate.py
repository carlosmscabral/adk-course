"""Gate-keeper solution for Module 05 mini-drill.

Clones the shape of `llm-auditor`: a SequentialAgent that runs a
summarizer followed by a translator. The translator reads the
summarizer's output via state-key substitution ({summary}).

Run with: python summ_translate.py
Requires: ADK 2.0, a configured Gemini API key (or Vertex auth).
"""

import asyncio

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

MODEL = "gemini-2.5-flash"
APP_NAME = "summ_translate"
USER_ID = "drill_user"

# ── Sub-agents ───────────────────────────────────────────────────────

summarizer_agent = LlmAgent(
    name="summarizer_agent",
    model=MODEL,
    description=(
        "Reads a paragraph of English prose and produces a single-sentence "
        "summary that preserves the most important fact."
    ),
    instruction=(
        "You are a precise summarizer. Read the user's paragraph and reply "
        "with exactly one English sentence (max 25 words) that captures the "
        "central fact. Do not add commentary or restate the request."
    ),
    output_key="summary",
)

translator_agent = LlmAgent(
    name="translator_agent",
    model=MODEL,
    description=(
        "Translates a single English sentence into idiomatic French. "
        "Expects the sentence to be present in session state under 'summary'."
    ),
    instruction=(
        "Translate the following English sentence into idiomatic French. "
        "Output only the French translation — no preamble, no quotes.\n\n"
        "Sentence: {summary}"
    ),
    output_key="translation",
)

# ── Pipeline ─────────────────────────────────────────────────────────

root_agent = SequentialAgent(
    name="summ_translate",
    description="Summarize an English paragraph, then translate the summary to French.",
    sub_agents=[summarizer_agent, translator_agent],
)


# ── Runner ──────────────────────────────────────────────────────────


async def main() -> None:
    paragraph = (
        "The Apollo program was a series of crewed spaceflights run by NASA "
        "between 1961 and 1972. Its primary objective, set by President "
        "Kennedy in 1961, was to land humans on the Moon and return them "
        "safely to Earth, which it accomplished with Apollo 11 in July 1969. "
        "The program also produced significant scientific and technological "
        "advances."
    )

    runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
    session = await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )

    user_msg = types.Content(role="user", parts=[types.Part(text=paragraph)])

    final_text = ""
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=user_msg,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = event.content.parts[0].text or ""
            print(f"[{event.author}] {final_text}")

    # Inspect final state to confirm both keys plumbed correctly.
    final_session = await runner.session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session.id
    )
    print("\n--- final session.state ---")
    print(f"summary     = {final_session.state.get('summary')!r}")
    print(f"translation = {final_session.state.get('translation')!r}")


if __name__ == "__main__":
    asyncio.run(main())
