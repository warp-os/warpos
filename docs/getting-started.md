# Getting Started with WarpOS

This guide walks you through installing WarpOS and building your first agent.

## Installation

```bash
pip install warpos
```

For development:

```bash
pip install "warpos[dev]"
```

## Setting Up Your Provider

WarpOS supports multiple LLM providers. Set the appropriate API key:

```bash
# OpenAI
export OPENAI_API_KEY=sk-...

# Anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# Groq
export GROQ_API_KEY=gsk_...

# DeepSeek
export DEEPSEEK_API_KEY=sk-...
```

For local models with Ollama, no API key is needed — just run `ollama serve`.

## Your First Agent

Create a file called `main.py`:

```python
from warpos import Agent

agent = Agent(
    name="MyAgent",
    model="gpt-4o",
    instructions="You are a helpful assistant."
)

response = agent.run("What is the capital of France?")
print(response)
```

Run it:

```bash
python main.py
```

## Adding Tools

Tools let your agent call Python functions:

```python
from warpos import Agent, tool

@tool
def calculate(expression: str) -> str:
    """Evaluate a math expression."""
    return str(eval(expression))

agent = Agent(
    name="MathBot",
    model="gpt-4o",
    tools=[calculate],
    instructions="You are a math assistant. Use the calculate tool for computations."
)

response = agent.run("What is 234 * 567?")
print(response)
```

## Using Memory

Memory gives your agent conversation history:

```python
from warpos import Agent, Memory

memory = Memory()
agent = Agent(
    name="ChatBot",
    model="gpt-4o",
    memory=memory,
    instructions="You are a friendly chatbot."
)

agent.run("My name is Alice.")
print(agent.run("What's my name?"))  # Remembers: "Your name is Alice."
```

## Scaffolding with the CLI

Use the CLI to bootstrap a project:

```bash
warp init my-agent
cd my-agent
```

This creates:

```
my-agent/
├── main.py
├── tools/
│   └── __init__.py
├── .env
└── warpos.yaml
```

Start the dev server:

```bash
warp serve
```

Your agent is now available at `http://localhost:8000`.

## Next Steps

- [Providers](providers.md) — Configure different LLM providers
- [Tools](tools.md) — Build custom tools
- [API Reference](api-reference.md) — Full API documentation
