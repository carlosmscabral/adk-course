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
    global_instruction: str | InstructionProvider = "",   # DEPRECATED — use GlobalInstructionPlugin
    static_instruction: types.ContentUnion | None = None,
    description: str = "",
    tools: list[ToolUnion] = [],   # ToolUnion = Union[Callable, BaseTool, BaseToolset]
    sub_agents: list[BaseAgent] = [],
    output_key: str | None = None,
    input_schema: type[BaseModel] | None = None,
    output_schema: type[BaseModel] | None = None,
    include_contents: Literal["default", "none"] = "default",
    mode: Literal["chat", "task", "single_turn"] | None = None,
    parallel_worker: bool | None = None,
    disallow_transfer_to_parent: bool = False,
    disallow_transfer_to_peers: bool = False,
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
| `global_instruction` | **DEPRECATED** — instructions for the whole agent tree (only the root agent's value takes effect). Use `GlobalInstructionPlugin` at the App level instead. | `global_instruction="Always reply in French."` |
| `static_instruction` | Static prompt content (str / `types.Content` / `types.Part` / list) sent literally as system instruction at the front of the request. No interpolation. Intended for context-cache optimization. When set, the regular `instruction` moves into user content. | `static_instruction="You are a helpful assistant."` |
| `description` | One-line summary used by *other agents* to decide whether to route to this one. Critical for multi-agent — the parent LLM reads this to pick a child. | `description="Answers questions about currencies"` |
| `tools` | List of `ToolUnion = Union[Callable, BaseTool, BaseToolset]`. (Bare callables auto-wrap to `FunctionTool`; `BaseToolset` includes `MCPToolset`.) | `tools=[get_weather, MCPToolset(...)]` |
| `sub_agents` | Composition slot — child agents the LLM can delegate to via `transfer_to_agent`. | `sub_agents=[critic, reviser]` |
| `output_key` | If set, the final text of each turn is written to `state[output_key]`. Shortcut for the most common state-write pattern. | `output_key="critique"` |
| `input_schema` / `output_schema` | Pydantic models for structured I/O. When set, the LLM is constrained to the schema. | `output_schema=SearchResult` |
| `include_contents` | `"default"` passes session history into the LLM call; `"none"` skips it (one-shot agents). | `include_contents="none"` |
| `mode` | Delegation mode: `"chat"` (default for sub-agents — reachable via `transfer_to_agent`), `"task"` (chats with user to accomplish a task), `"single_turn"` (one shot, no user dialogue — default for workflow nodes). | `mode="single_turn"` |
| `parallel_worker` | When `True`, this agent runs in parallel worker mode (used inside `ParallelAgent` fan-out). | `parallel_worker=True` |
| `disallow_transfer_to_parent` | If `True`, the LLM cannot transfer control back up to the parent agent. Note: also prevents this agent from replying to the end-user on subsequent turns. | `disallow_transfer_to_parent=True` |
| `disallow_transfer_to_peers` | If `True`, the LLM cannot transfer to sibling agents. | `disallow_transfer_to_peers=True` |
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
