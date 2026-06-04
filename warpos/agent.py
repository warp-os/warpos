"""Core Agent class and @tool decorator."""

from __future__ import annotations

import json
import inspect
import traceback
from typing import Any, Callable
from dataclasses import dataclass, field

from warpos.memory import Memory
from warpos.provider import Provider, Message, ToolCall


# ── @tool decorator ──────────────────────────────────────────────────────────

@dataclass
class ToolDef:
    name: str
    description: str
    parameters: dict[str, Any]
    fn: Callable

    def to_openai_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


_TOOL_REGISTRY: dict[str, ToolDef] = {}


def tool(fn: Callable = None, *, name: str = None, description: str = None):
    """Decorator to register a function as an agent tool.

    Usage:
        @tool
        def search(query: str) -> str:
            \"\"\"Search the web.\"\"\"
            return results

        @tool(name="custom_name", description="Custom description")
        def my_func(x: int) -> str: ...
    """
    def decorator(func: Callable) -> Callable:
        tool_name = name or func.__name__
        tool_desc = description or (func.__doc__ or "").strip() or f"Call {tool_name}"
        tool_desc = tool_desc.split("\n")[0].strip()

        # Build JSON schema from type hints
        sig = inspect.signature(func)
        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            param_type = param.annotation
            prop: dict[str, Any] = {"type": "string"}  # default

            if param_type is int:
                prop["type"] = "integer"
            elif param_type is float:
                prop["type"] = "number"
            elif param_type is bool:
                prop["type"] = "boolean"
            elif param_type is list:
                prop["type"] = "array"
            elif param_type is dict:
                prop["type"] = "object"

            # Try to get description from docstring
            prop["description"] = f"The {param_name} parameter"
            properties[param_name] = prop

            if param.default is inspect.Parameter.empty:
                required.append(param_name)

        parameters = {
            "type": "object",
            "properties": properties,
            "required": required,
        }

        tool_def = ToolDef(
            name=tool_name,
            description=tool_desc,
            parameters=parameters,
            fn=func,
        )

        _TOOL_REGISTRY[tool_name] = tool_def
        func._warpos_tool = tool_def
        return func

    if fn is not None:
        return decorator(fn)
    return decorator


# ── Agent ────────────────────────────────────────────────────────────────────

@dataclass
class AgentConfig:
    name: str = "agent"
    instructions: str = "You are a helpful assistant."
    model: str = "gpt-4o-mini"
    provider: str = "openai"  # openai | anthropic | groq | ollama
    api_key: str = None
    base_url: str = None
    tools: list = field(default_factory=list)
    memory: bool = True
    memory_db: str = None
    max_iterations: int = 10
    temperature: float = 0.7


class Agent:
    """An AI agent with memory, tools, and provider routing.

    Usage:
        agent = Agent(
            name="my-agent",
            instructions="You are a research assistant.",
            model="gpt-4o-mini",
            tools=[search_web],
            memory=True,
        )

        response = agent.run("What is the capital of France?")
        agent.serve()  # Start chat UI on localhost:3000
    """

    def __init__(
        self,
        name: str = "agent",
        instructions: str = "You are a helpful assistant.",
        model: str = "gpt-4o-mini",
        provider: str = "openai",
        api_key: str = None,
        base_url: str = None,
        tools: list = None,
        memory: bool = True,
        memory_db: str = None,
        max_iterations: int = 10,
        temperature: float = 0.7,
    ):
        self.config = AgentConfig(
            name=name,
            instructions=instructions,
            model=model,
            provider=provider,
            api_key=api_key,
            base_url=base_url,
            tools=tools or [],
            memory=memory,
            memory_db=memory_db,
            max_iterations=max_iterations,
            temperature=temperature,
        )

        # Register tools
        self._tool_defs: dict[str, ToolDef] = {}
        for t in (tools or []):
            if callable(t) and hasattr(t, "_warpos_tool"):
                td: ToolDef = t._warpos_tool
                self._tool_defs[td.name] = td
            elif isinstance(t, ToolDef):
                self._tool_defs[t.name] = t

        # Memory
        self._memory: Memory | None = None
        if memory:
            db_path = memory_db or f".warpos/{name}/memory.db"
            self._memory = Memory(db_path)

        # Provider
        self._provider = Provider(
            name=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
        )

        # Conversation state
        self._messages: list[Message] = []

    def run(self, message: str, session_id: str = "default") -> str:
        """Run a single turn: send a message, get a response.

        Handles tool calls in a loop until the model produces a final text response.
        """
        # Add user message
        self._messages.append(Message(role="user", content=message))

        # Retrieve memories
        memory_context = ""
        if self._memory:
            memories = self._memory.search(message, limit=5)
            if memories:
                memory_context = "\n\nRelevant memories:\n" + "\n".join(
                    f"- {m}" for m in memories
                )

        # Build system prompt
        system = self.config.instructions
        if memory_context:
            system += memory_context

        # Tool schemas
        tool_schemas = [td.to_openai_schema() for td in self._tool_defs.values()]

        # Agent loop
        for _ in range(self.config.max_iterations):
            response = self._provider.chat(
                messages=self._messages,
                system=system,
                tools=tool_schemas if tool_schemas else None,
                temperature=self.config.temperature,
            )

            if response.tool_calls:
                # Add assistant message with tool calls
                self._messages.append(Message(
                    role="assistant",
                    content=response.content or "",
                    tool_calls=response.tool_calls,
                ))

                # Execute each tool call
                for tc in response.tool_calls:
                    result = self._execute_tool(tc)
                    self._messages.append(Message(
                        role="tool",
                        tool_call_id=tc.id,
                        content=result,
                    ))
                continue

            # Final text response
            self._messages.append(Message(role="assistant", content=response.content))

            # Save to memory
            if self._memory:
                self._memory.add(
                    text=f"User: {message}\nAssistant: {response.content}",
                    session_id=session_id,
                )

            return response.content

        return "Max iterations reached."

    def _execute_tool(self, tc: ToolCall) -> str:
        """Execute a tool call and return the result as a string."""
        tool_def = self._tool_defs.get(tc.name)
        if not tool_def:
            return f"Error: Unknown tool '{tc.name}'"

        try:
            args = json.loads(tc.arguments) if isinstance(tc.arguments, str) else tc.arguments
            result = tool_def.fn(**args)
            return str(result)
        except Exception as e:
            return f"Error: {traceback.format_exc()}"

    def chat(self, message: str, session_id: str = "default") -> str:
        """Alias for run()."""
        return self.run(message, session_id=session_id)

    def reset(self):
        """Clear conversation history."""
        self._messages = []

    def serve(self, host: str = "0.0.0.0", port: int = 3000):
        """Start the agent server with auto-generated chat UI."""
        from warpos.server import create_app
        app = create_app(self)
        import uvicorn
        uvicorn.run(app, host=host, port=port, log_level="info")

    def __repr__(self):
        return f"Agent(name={self.config.name!r}, model={self.config.model!r}, tools={list(self._tool_defs.keys())})"
