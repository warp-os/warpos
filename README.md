# WarpOS

The open-source platform for AI agents. Write logic, deploy everything.

## Install

```bash
pip install warpos
```

## Quick Start

```python
from warpos import Agent, tool

@tool
def search(query: str) -> str:
    """Search the web."""
    return f"Results for: {query}"

agent = Agent(
    name="my-agent",
    instructions="You are a helpful assistant.",
    model="gpt-4o-mini",
    tools=[search],
    memory=True,
)

# Interactive mode
response = agent.run("What is Python?")

# Or serve with chat UI
agent.serve()  # → http://localhost:3000
```

## CLI

```bash
warp init my-agent    # Scaffold a new project
warp serve agent.py   # Serve with chat UI
```

## License

MIT
