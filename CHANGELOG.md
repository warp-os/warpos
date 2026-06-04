# Changelog

All notable changes to WarpOS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-01

### Added

- **Agent** — Core agent class with instruction-based prompting and tool orchestration
- **Tool system** — `@tool` decorator for exposing Python functions to agents
- **Multi-provider support** — OpenAI, Anthropic, Groq, DeepSeek, Ollama, Cerebras
- **Memory** — In-memory conversation history with pluggable backends
- **Streaming** — Real-time token streaming for all supported providers
- **CLI** — `warp init` for project scaffolding and `warp serve` for running agents
- **HTTP Server** — REST API and WebSocket support for agent interactions
- **Type safety** — Full type hints and Pydantic model integration
- **Documentation** — Getting started guide, provider docs, tool docs, API reference
- **Examples** — Advanced agent, Discord bot, Telegram bot examples
- **Tests** — Comprehensive test suite for agents, tools, memory, and providers
