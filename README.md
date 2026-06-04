<p align="center">
  <br/>
  <img src="https://img.shields.io/pypi/v/warpos?color=blue&logo=pypi&logoColor=white&style=for-the-badge" alt="PyPI" />
  <img src="https://img.shields.io/pypi/pyversions/warpos?color=blue&logo=python&logoColor=white&style=for-the-badge" alt="Python" />
  <img src="https://img.shields.io/github/license/warp-os/warpos?color=green&style=for-the-badge" alt="License" />
  <img src="https://img.shields.io/github/stars/warp-os/warpos?color=yellow&logo=github&style=for-the-badge" alt="GitHub Stars" />
  <br/>
  <br/>
</p>

<h1 align="center">
  <pre>
 ██╗    ██╗ █████╗ ██████╗ ██████╗  ██████╗ ███████╗
 ██║    ██║██╔══██╗██╔══██╗██╔══██╗██╔═══██╗██╔════╝
 ██║ █╗ ██║███████║██████╔╝██████╔╝██║   ██║███████╗
 ██║███╗██║██╔══██║██╔══██╗██╔══██╗██║   ██║╚════██║
 ╚███╔███╔╝██║  ██║██║  ██║██████╔╝╚██████╔╝███████║
  ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚══════╝
  </pre>
</h1>

<p align="center">
  <strong>The open-source platform for AI agents.<br/>Write logic, deploy everything.</strong>
</p>

<p align="center">
  <a href="https://warpos.dev">Website</a> · <a href="https://github.com/warp-os/warpos">GitHub</a> · <a href="https://pypi.org/project/warpos/">PyPI</a>
</p>

---

## What is WarpOS?

WarpOS is a lightweight framework for building AI agents that actually work in production. It handles the messy parts — provider routing, tool orchestration, memory management, and server deployment — so you can focus on writing agent logic. Ship a working agent in minutes, not days.

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
    instructions="You are a helpful weather assistant."
)

response = agent.run("What's the weather in San Francisco?")
print(response)
```

## ⚡ Quick Start

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

## 🚀 Features

- **Multi-provider support** — OpenAI, Anthropic, Groq, DeepSeek, Ollama, Cerebras, and more
- **Tool calling** — Decorate any Python function as a tool with `@tool`
- **Memory** — Built-in conversation memory with persistent storage options
- **CLI** — `warp init` scaffolds a project, `warp serve` starts an API server
- **Streaming** — Real-time token streaming for all providers
- **Type-safe** — Full type hints and Pydantic model support
- **Lightweight** — Minimal dependencies, fast startup, production-ready

## 🔌 Providers

WarpOS supports multiple LLM providers out of the box. Swap providers with one line:

| Provider | Models | Streaming | Tool Calling |
| --- | --- | --- | --- |
| **OpenAI** | GPT-4o, GPT-4, GPT-3.5 | ✅ | ✅ |
| **Anthropic** | Claude 3.5 Sonnet, Claude 3 Opus | ✅ | ✅ |
| **Groq** | Llama 3, Mixtral | ✅ | ✅ |
| **DeepSeek** | DeepSeek-V2, DeepSeek Coder | ✅ | ✅ |
| **Ollama** | Llama 3, Mistral, any local model | ✅ | ✅ |
| **Cerebras** | Llama 3, custom models | ✅ | ✅ |

```python
# Switch providers easily
agent = Agent(name="Bot", model="anthropic/claude-3-5-sonnet-20241022")
agent = Agent(name="Bot", model="groq/llama3-70b-8192")
agent = Agent(name="Bot", model="ollama/llama3")
```

## 🖥️ CLI

WarpOS includes a CLI for scaffolding and running agents:

```bash
# Create a new project
warp init my-agent

# Start the development server
warp serve

# Run with hot reload
warp serve --reload
```

## 🏗️ Architecture

WarpOS is built around five core components:

- **Agent** — The orchestrator. Takes instructions, manages context, calls tools, returns responses.
- **Tools** — Python functions exposed to the agent via the `@tool` decorator. Type-hinted, self-documenting.
- **Memory** — Conversation history and long-term storage. Pluggable backends (in-memory, SQLite, Redis).
- **Provider** — Abstraction layer over LLM APIs. Handles routing, retries, rate limits, and streaming.
- **Server** — HTTP server with REST API and WebSocket support for real-time agent interactions.

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
               └─────────────┘
```

## 📖 Examples

Check out the `examples/` directory:

- **[Advanced Agent](examples/advanced.py)** — Multiple tools, custom provider, memory
- **[Discord Bot](examples/discord-bot.py)** — Build a Discord bot with WarpOS
- **[Telegram Bot](examples/telegram-bot.py)** — Build a Telegram bot with WarpOS

## 🤝 Contributing

We welcome contributions of all kinds. See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, coding standards, and how to submit a PR.

```bash
git clone https://github.com/warp-os/warpos.git
cd warpos
pip install -e ".[dev]"
pytest
```

## 📄 License

WarpOS is released under the [MIT License](LICENSE).

## ⭐ Star History

If you find WarpOS useful, consider giving it a star on GitHub!

[![Star History Chart](https://api.star-history.com/svg?repos=warp-os/warpos&type=Date)](https://star-history.com/#warp-os/warpos&Date)
