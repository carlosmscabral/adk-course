---
module: 03_Tools
page: 06_ComputerUse
title: Computer Use toolset — letting the agent drive a browser (preview)
estimated_minutes: 20
prereqs: [03_Tools/05]
concepts: [ComputerUseToolset, BaseComputer, screenshot-loop, browser-automation]
icon: 🛠
in_production: false
detours_suggested: []
---

[← Prev: 03_Tools/05_BuiltInTools](05_BuiltInTools.md)  [↑ Map](../../MAP.md)  [Next: 03_Tools/07_ToolLimitations →]

You are here: 🗺 Foundation Track ▸ 03 Tools ▸ 06 Computer Use (preview)

# 🛠 Computer Use — the agent grows hands

`google_search` lets the agent *read* the web. **Computer Use lets the agent *drive* it.** Preview surface in ADK 2.0 — flagged `@experimental` in source — but the API is stable enough to play with.

## 🧠 The shape

Three pieces:

1. **`BaseComputer`** — an abstract base class with 16 async abstract methods: `screen_size`, `open_web_browser`, `click_at(x,y)`, `hover_at(x,y)`, `type_text_at(x,y,text)`, `scroll_document(direction)`, `scroll_at(x,y,direction,magnitude)`, `wait(seconds)`, `go_back`, `go_forward`, `search`, `navigate(url)`, `key_combination(keys)`, `drag_and_drop`, `current_state`, and `environment`. (`prepare`, `initialize`, `close` are concrete hooks you can override.) You implement these against whatever automation backend you like.
2. **`ComputerUseToolset`** — wraps a `BaseComputer` instance and turns each method into a tool the LLM can call.
3. **The model loop** — Gemini 2.x emits `click_at(...)`, your `BaseComputer` executes it, returns a `ComputerState` (screenshot bytes + URL), Gemini sees the new screenshot, decides what to click next. The screenshot *is* the agent's vision.

## 🛠 The minimal runnable

```python
# Work/computer_use_demo.py — run with: uv run python Work/computer_use_demo.py
# requires: pip install playwright && playwright install chromium
import asyncio
from typing import Literal
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.adk.tools.computer_use.base_computer import (
    BaseComputer,
    ComputerEnvironment,
    ComputerState,
)
from google.adk.tools.computer_use.computer_use_toolset import ComputerUseToolset
# NOTE: tools/computer_use/__init__.py is empty — import from the submodules.
from google.genai import types


class PlaywrightComputer(BaseComputer):
    """A toy BaseComputer impl backed by Playwright + Chromium."""

    def __init__(self):
        self._browser = None
        self._page = None

    async def initialize(self) -> None:
        from playwright.async_api import async_playwright
        self._pw = await async_playwright().start()
        self._browser = await self._pw.chromium.launch(headless=True)
        self._page = await self._browser.new_page(viewport={"width": 1280, "height": 800})

    async def close(self) -> None:
        await self._browser.close()
        await self._pw.stop()

    async def environment(self) -> ComputerEnvironment:
        return ComputerEnvironment.ENVIRONMENT_BROWSER

    async def screen_size(self) -> tuple[int, int]:
        return (1280, 800)

    async def current_state(self) -> ComputerState:
        return ComputerState(screenshot=await self._page.screenshot(), url=self._page.url)

    async def open_web_browser(self) -> ComputerState:
        await self._page.goto("about:blank")
        return await self.current_state()

    async def navigate(self, url: str) -> ComputerState:
        await self._page.goto(url)
        return await self.current_state()

    async def click_at(self, x: int, y: int) -> ComputerState:
        await self._page.mouse.click(x, y)
        return await self.current_state()

    async def type_text_at(self, x, y, text, press_enter=True, clear_before_typing=True) -> ComputerState:
        await self._page.mouse.click(x, y)
        if clear_before_typing:
            await self._page.keyboard.press("Control+A")
            await self._page.keyboard.press("Delete")
        await self._page.keyboard.type(text)
        if press_enter:
            await self._page.keyboard.press("Enter")
        return await self.current_state()

    async def scroll_document(self, direction) -> ComputerState:
        dy = {"down": 400, "up": -400}.get(direction, 0)
        dx = {"right": 400, "left": -400}.get(direction, 0)
        await self._page.mouse.wheel(dx, dy)
        return await self.current_state()

    # The remaining abstract methods (hover_at, scroll_at, wait, go_back,
    # go_forward, search, key_combination, drag_and_drop) are stubs for this demo;
    # implement them when your agent actually needs them.
    async def hover_at(self, x, y): return await self.current_state()
    async def scroll_at(self, x, y, direction, magnitude): return await self.current_state()
    async def wait(self, seconds):
        await asyncio.sleep(seconds); return await self.current_state()
    async def go_back(self):
        await self._page.go_back(); return await self.current_state()
    async def go_forward(self):
        await self._page.go_forward(); return await self.current_state()
    async def search(self): return await self.navigate("https://www.google.com")
    async def key_combination(self, keys):
        await self._page.keyboard.press("+".join(keys)); return await self.current_state()
    async def drag_and_drop(self, x, y, destination_x, destination_y):
        await self._page.mouse.move(x, y)
        await self._page.mouse.down()
        await self._page.mouse.move(destination_x, destination_y)
        await self._page.mouse.up()
        return await self.current_state()


async def main():
    toolset = ComputerUseToolset(computer=PlaywrightComputer())
    agent = LlmAgent(
        name="browser_pilot",
        model="gemini-2.5-flash",
        instruction="Use the browser to look up the answer to the user's question.",
        tools=[toolset],   # NOTE: pass the toolset, not individual tools
    )
    runner = InMemoryRunner(agent=agent, app_name="cu_demo")
    session = await runner.session_service.create_session(app_name="cu_demo", user_id="u1")
    msg = types.Content(role="user", parts=[types.Part(text="Find Python's release notes for 3.13.")])
    async for ev in runner.run_async(user_id="u1", session_id=session.id, new_message=msg):
        if ev.is_final_response():
            print(ev.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
```

The framework wires every public `BaseComputer` method into the LLM's tool list automatically (`screen_size`, `environment`, `close`, `prepare` are excluded). You don't write per-tool declarations.

## 🧠 The screenshot+action loop

```
        ┌──────────────────────────────┐
        │  user: "find python 3.13     │
        │   release notes"             │
        └──────────────┬───────────────┘
                       ▼
   ┌─────────────────────────────────────┐
   │  Gemini sees: tool list + first     │
   │  screenshot (from open_web_browser) │
   └──────────────┬──────────────────────┘
                  ▼
        click_at(x=640, y=120)   ──►  PlaywrightComputer.click_at
                  ▲                          │
                  │                          ▼
                  └───── new screenshot + URL (ComputerState)
                  ▼
        type_text_at(...) → screenshot → click_at(...) → screenshot ...
                  ▼
              final answer
```

Every action returns a fresh screenshot. Gemini uses pixel coordinates against the screenshot it just received — that's why `screen_size()` must report the real dimensions of the screenshots you produce.

## 🧠 When this beats `FunctionTool` / `MCPToolset`

* **No API.** The site has no public API and you don't want to scrape HTML. Computer Use clicks like a human.
* **Auth flows.** SSO, captchas, "are you a robot?" — easier to drive interactively than to forge tokens.
* **Discovery tasks.** "Find me the best price on X across these three travel sites" — generalizing across UIs is what vision-driven models are good at.

## ⚠️ When this is the wrong hammer

* Anything with a stable JSON API — `FunctionTool` is 100× faster and 1000× cheaper per call.
* Internal tools at your company — write an `MCPToolset` (Module 08), don't drive a browser.
* Anything safety-critical (banking, healthcare records, prod infra) — model misclicks happen.

> **🚀 In Production**
>
> `ComputerUseToolset` is marked `@experimental(FeatureName.COMPUTER_USE)` in ADK 2.0. The API can shift between minor versions. Production deployments need: (1) a sandboxed browser (don't share Chromium with your host), (2) per-step approvals on destructive actions (wire `before_tool_callback` to gate `click_at` near "Delete"/"Submit" affordances), and (3) a hard timeout per invocation — runaway loops can rack up Gemini cost fast. See Module 4B's HITL patterns and [[16_ProductionSecurity/05_GuardrailsCookbook]].

> ❓ **Ask the student:** the model receives `click_at(x=640, y=120)` as a callable tool. What does the LLM actually see when it's deciding *where* to click?
> *(Expected: the screenshot bytes returned from the previous tool call — Gemini's vision model picks coordinates against that image. That's why `screen_size()` must match your viewport.)*

> 🛠 **Have the student do this:** open `adk-python/src/google/adk/tools/computer_use/base_computer.py` and list the abstract methods. Confirm the toolset wires *each one* as a separate tool (with `screen_size`, `environment`, `close`, `prepare` excluded — see `EXCLUDED_METHODS` in `computer_use_toolset.py`).

> 🤖 **Tutor:** if the student wants to actually run the script, they need Playwright installed AND a real Gemini API key. If either's missing, walk them through the file and let them see the *shape* of the loop instead. The page is here for recognition; the deep dive is Module 18 (Streaming) when we cover live UIs.

---

[← Prev: 03_Tools/05_BuiltInTools](05_BuiltInTools.md)  [↑ Map](../../MAP.md)  [Next: 03_Tools/07_ToolLimitations →]
