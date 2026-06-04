# API Reference

## Agent

The core class for creating AI agents.

```python
from warpos import Agent

agent = Agent(
    name: str,                    # Agent name
    model: str,                   # Model identifier (e.g., "gpt-4o", "anthropic/claude-3-5-sonnet-20241022")
    instructions: str = "",       # System prompt / instructions
    tools: list[Tool] = [],       # List of tools available to the agent
    memory: Memory | None = None, # Memory instance for conversation history
    provider: Provider | None = None,  # Custom provider instance
    temperature: float = 0.7,     # Sampling temperature
    max_tokens: int | None = None # Max tokens in response
)
```

### Methods

#### `agent.run(message: str) -> str`

Run the agent with a user message. Returns the agent's response as a string.

```python
response = agent.run("Hello!")
```

#### `agent.run_stream(message: str) -> AsyncIterator[str]`

Stream the agent's response token by token.

```python
async for token in agent.run_stream("Tell me a story"):
    print(token, end="", flush=True)
```

#### `agent.reset()`

Clear the agent's memory and start fresh.

---

## Tool

Create tools with the `@tool` decorator.

```python
from warpos import tool

@tool
def my_function(arg1: str, arg2: int = 0) -> str:
    """Description of what this tool does."""
    return "result"
```

The decorator:
- Extracts the function name, docstring, and type hints
- Registers it as a tool callable by agents
- Wraps error handling automatically

---

## Memory

Manages conversation history.

```python
from warpos import Memory

memory = Memory(
    max_messages: int | None = None  # Limit conversation length
)
```

### Methods

#### `memory.add(role: str, content: str)`

Add a message to memory. `role` is `"user"`, `"assistant"`, or `"system"`.

#### `memory.get() -> list[dict]`

Get all messages as a list of `{"role": str, "content": str}` dicts.

#### `memory.clear()`

Clear all messages.

---

## Provider

Providers handle communication with LLM APIs.

```python
from warpos.providers import Provider
```

All providers implement:

#### `provider.complete(messages, model, tools=None, stream=False) -> str`

Send a completion request. Returns the model's response as a string.

#### `provider.stream(messages, model, tools=None) -> AsyncIterator[str]`

Stream a completion request. Yields tokens as they arrive.

### Built-in Providers

- `OpenAIProvider` — OpenAI API
- `AnthropicProvider` — Anthropic API
- `GroqProvider` — Groq API
- `DeepSeekProvider` — DeepSeek API
- `OllamaProvider` — Ollama (local)
- `CerebrasProvider` — Cerebras API
