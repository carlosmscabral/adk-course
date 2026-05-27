# 📋 Cheat Sheet — `LlmAgent(...)` signature

The single most-used constructor in ADK. Aliased as `Agent`. This sheet is the **one-pager for tab completion**, not a tutorial — see [Notes/02_FirstAgent/](../../Notes/02_FirstAgent/) for the engine-first walk-through.

```python
from google.adk.agents import LlmAgent
# from google.adk.agents import Agent  # alias — same class
```

## Signature (most-used kwargs)

```python
LlmAgent(
    name: str,
    model: str | BaseLlm = "gemini-2.5-flash",
    instruction: str | InstructionProvider = "",
    description: str = "",
    tools: list[BaseTool] = [],
    sub_agents: list[BaseAgent] = [],
    output_key: str | None = None,
    input_schema: type[BaseModel] | None = None,
    output_schema: type[BaseModel] | None = None,
    include_contents: Literal["default", "none"] = "default",
    planner: BasePlanner | None = None,
    code_executor: BaseCodeExecutor | None = None,
    before_model_callback: Callback | None = None,
    after_model_callback: Callback | None = None,
    before_tool_callback: Callback | None = None,
    after_tool_callback: Callback | None = None,
    before_agent_callback: Callback | None = None,
    after_agent_callback: Callback | None = None,
    on_model_error_callback: Callback | None = None,
    on_tool_error_callback: Callback | None = None,
    generate_content_config: types.GenerateContentConfig | None = None,
)
```

## Parameter cheatsheet

| Param | What it does | One-line example |
|---|---|---|
| `name` | Unique identifier within an agent tree; used by `transfer_to_agent` for routing. **Must be a valid Python identifier**. | `name="critic"` |
| `model` | Model id (Gemini) or `BaseLlm` instance (LiteLlm, Claude, Gemma, OpenAI). Default is `gemini-2.5-flash`. | `model="gemini-2.5-flash"` |
| `instruction` | The system prompt. Supports `{var}` and `{var?}` interpolation from session state. May be a callable that receives `ReadonlyContext` and returns str. | `instruction="You are a helpful agent. User name: {user:name?}"` |
| `description` | One-line summary used by *other agents* to decide whether to route to this one. Critical for multi-agent — the parent LLM reads this to pick a child. | `description="Answers questions about currencies"` |
| `tools` | List of `BaseTool` instances. Bare Python functions are auto-wrapped to `FunctionTool`. | `tools=[get_weather, MCPToolset(...)]` |
| `sub_agents` | Composition slot — child agents the LLM can delegate to via `transfer_to_agent`. | `sub_agents=[critic, reviser]` |
| `output_key` | If set, the final text of each turn is written to `state[output_key]`. Shortcut for the most common state-write pattern. | `output_key="critique"` |
| `input_schema` / `output_schema` | Pydantic models for structured I/O. When set, the LLM is constrained to the schema. | `output_schema=SearchResult` |
| `include_contents` | `"default"` passes session history into the LLM call; `"none"` skips it (one-shot agents). | `include_contents="none"` |
| `planner` | Plugs in a planning strategy (e.g., `BuiltInPlanner`, `PlanReActPlanner`). | `planner=BuiltInPlanner()` |
| `code_executor` | A `BaseCodeExecutor` instance for agents that need to run code (math, data sci). | `code_executor=VertexAiCodeExecutor()` |
| `before_model_callback` | Fires before the LLM call. Return `LlmResponse` to short-circuit; return `None` to pass through. | See [Callback signatures](callback_signatures.md). |
| `after_model_callback` | Fires after the LLM call. Mutate or replace the response. | |
| `before_tool_callback` | Fires before a tool runs. Block (return `dict`) or pass through (return `None`). | |
| `after_tool_callback` | Fires after a tool runs. Inspect / modify the tool result. | |
| `before_agent_callback` | Fires before the agent starts a turn. | |
| `after_agent_callback` | Fires after the agent finishes a turn. | |
| `on_model_error_callback` | Fires on model API error — implement retry/fallback. | |
| `on_tool_error_callback` | Fires on tool exception — implement retry/fallback. | |
| `generate_content_config` | Raw `google.genai.types.GenerateContentConfig` — temperature, top_p, safety, response_modalities, etc. | `generate_content_config=types.GenerateContentConfig(temperature=0.2)` |

## Minimal example

```python
from google.adk.agents import LlmAgent

agent = LlmAgent(
    name="hello",
    model="gemini-2.5-flash",
    instruction="You are a friendly greeter. Greet the user by name if known.",
    description="Greets users",
)
```

## Where it's covered in the course

- Engine-first walk: [Notes/02_FirstAgent/01_LlmAgentByHand](../../Notes/02_FirstAgent/01_LlmAgentByHand.md)
- `tools=`: [Notes/03_Tools/02_FunctionTool](../../Notes/03_Tools/02_FunctionTool.md)
- `sub_agents=` + `description`: [Notes/05_MultiAgent/01_SubAgents](../../Notes/05_MultiAgent/01_SubAgents.md)
- `instruction` templating: [Notes/04_SessionsState/04_InstructionTemplating](../../Notes/04_SessionsState/04_InstructionTemplating.md)
- `output_key`: [Notes/04_SessionsState/04_InstructionTemplating](../../Notes/04_SessionsState/04_InstructionTemplating.md)
- Callbacks: [Notes/07_Callbacks/](../../Notes/07_Callbacks/) + [Callback signatures cheat sheet](callback_signatures.md)
- `model=` choices: [Notes/17_AdvancedModels/](../../Notes/17_AdvancedModels/)
- `code_executor=`: [Notes/12_CodeExecution/](../../Notes/12_CodeExecution/)

---

[← Cheat sheets](../CheatSheets/) · [📍 Progress](../../PROGRESS.md)
