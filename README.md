<div align="center">

<br/>

```
██╗    ██╗ █████╗ ██████╗ ██████╗  ██████╗ ███████╗
██║    ██║██╔══██╗██╔══██╗██╔══██╗██╔═══██╗██╔════╝
██║ █╗ ██║███████║██████╔╝██████╔╝██║   ██║███████╗
██║███╗██║██╔══██║██╔══██╗██╔═══╝ ██║   ██║╚════██║
╚███╔███╔╝██║  ██║██║  ██║██║     ╚██████╔╝███████║
 ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚══════╝
```

### The open-source platform for AI agents.

**Write logic, deploy everything.**

[![PyPI Version](https://img.shields.io/pypi/v/warpos.svg?style=flat-square&logo=pypi&logoColor=white&color=blue)](https://pypi.org/project/warpos/)
[![Python](https://img.shields.io/pypi/pyversions/warpos.svg?style=flat-square&logo=python&logoColor=white&color=blue)](https://pypi.org/project/warpos/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/warp-os/warpos.svg?style=flat-square&logo=github&color=yellow)](https://github.com/warp-os/warpos/stargazers)

[Website](https://warpos.dev) · [Docs](https://github.com/warp-os/warpos/tree/main/docs) · [PyPI](https://pypi.org/project/warpos/) · [Examples](https://github.com/warp-os/warpos/tree/main/examples)

</div>

---

## What is WarpOS?

WarpOS is a lightweight framework for building AI agents that actually work in production. It handles the messy parts — provider routing, tool orchestration, memory management, and server deployment — so you can focus on writing agent logic.

Ship a working agent in minutes, not days.

```python
from warpos import Agent, tool

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"Sunny, 72°F in {city}"

agent = Agent(
    name="WeatherBot",
    model="gpt-4o",
    tools=[get_weather],
    instructions="You are a helpful weather assistant.",
)

response = agent.run("What's the weather in San Francisco?")
print(response)
```

---

## Quick Start

```bash
pip install warpos
```

Set your API key:

```bash
export OPENAI_API_KEY=sk-...
```

Run your first agent:

```python
from warpos import Agent

agent = Agent(name="MyAgent", model="gpt-4o")
print(agent.run("Hello! What can you do?"))
```

Or serve with a chat UI:

```bash
warp init my-agent
cd my-agent
warp serve
# → http://localhost:3000
```

---

## Features

- **Multi-provider** — OpenAI, Anthropic, Groq, DeepSeek, Ollama, Cerebras
- **Tool calling** — Decorate any Python function with `@tool`
- **Memory** — Built-in persistent conversation memory (SQLite + FTS5)
- **Chat UI** — Auto-generated WebSocket chat interface
- **CLI** — `warp init` scaffolds, `warp serve` deploys
- **Type-safe** — Full type hints, Pydantic support
- **Lightweight** — Minimal dependencies, fast startup

---

## Providers

Swap providers with one line:

```python
agent = Agent(name="Bot", provider="openai", model="gpt-4o")
agent = Agent(name="Bot", provider="anthropic", model="claude-sonnet-4-20250514")
agent = Agent(name="Bot", provider="groq", model="llama3-70b-8192")
agent = Agent(name="Bot", provider="ollama", model="llama3")
```

| Provider | Env Variable | Base URL |
|---|---|---|
| OpenAI | `OPENAI_API_KEY` | `api.openai.com` |
| Anthropic | `ANTHROPIC_API_KEY` | `api.anthropic.com` |
| Groq | `GROQ_API_KEY` | `api.groq.com` |
| DeepSeek | `DEEPSEEK_API_KEY` | `api.deepseek.com` |
| Cerebras | `CEREBRAS_API_KEY` | `api.cerebras.ai` |
| Ollama | — | `localhost:11434` |

---

## CLI

```bash
warp init my-agent     # scaffold a new project
warp serve agent.py    # serve with chat UI on :3000
warp serve -p 8080     # custom port
```

---

## Architecture

```
┌─────────────────────────────────────────────┐
│                   Agent                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Memory   │  │  Tools   │  │ Provider │  │
│  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────┘
                      │
               ┌──────┴──────┐
               │   Server    │
               │  (FastAPI)  │
               └─────────────┘
```

- **Agent** — Orchestrates context, tools, and provider calls
- **Tools** — Python functions exposed via `@tool` decorator
- **Memory** — SQLite + FTS5 persistent conversation storage
- **Provider** — Unified LLM routing with OpenAI/Anthropic compatibility
- **Server** — FastAPI + WebSocket with auto-generated chat UI

---

## Examples

- **[Basic Agent](examples/basic.py)** — Simple agent with tools
- **[Advanced Agent](examples/advanced.py)** — Multiple tools, memory, custom provider
- **[Discord Bot](examples/discord-bot.py)** — Discord integration
- **[Telegram Bot](examples/telegram-bot.py)** — Telegram integration

---

## Contributing

```bash
git clone https://github.com/warp-os/warpos.git
cd warpos
pip install -e ".[dev]"
pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

**[warpos.dev](https://warpos.dev)**

</div>
