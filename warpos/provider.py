"""Multi-provider LLM abstraction."""

from __future__ import annotations

import os
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Message:
    role: str  # system | user | assistant | tool
    content: str = ""
    tool_calls: list[ToolCall] = None
    tool_call_id: str = None


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: str  # JSON string


@dataclass
class Response:
    content: str = ""
    tool_calls: list[ToolCall] = None
    model: str = ""
    usage: dict = field(default_factory=dict)


class Provider:
    """Unified LLM provider that routes to OpenAI-compatible APIs.

    Supports: openai, anthropic, groq, ollama, deepseek, or any OpenAI-compatible base_url.
    """

    PROVIDERS = {
        "openai": {
            "base_url": "https://api.openai.com/v1",
            "env_key": "OPENAI_API_KEY",
        },
        "anthropic": {
            "base_url": None,  # Uses anthropic SDK
            "env_key": "ANTHROPIC_API_KEY",
        },
        "groq": {
            "base_url": "https://api.groq.com/openai/v1",
            "env_key": "GROQ_API_KEY",
        },
        "deepseek": {
            "base_url": "https://api.deepseek.com/v1",
            "env_key": "DEEPSEEK_API_KEY",
        },
        "ollama": {
            "base_url": "http://localhost:11434/v1",
            "env_key": None,
        },
        "cerebras": {
            "base_url": "https://api.cerebras.ai/v1",
            "env_key": "CEREBRAS_API_KEY",
        },
    }

    def __init__(
        self,
        name: str = "openai",
        model: str = "gpt-4o-mini",
        api_key: str = None,
        base_url: str = None,
    ):
        self.name = name
        self.model = model

        # Resolve provider config
        provider_cfg = self.PROVIDERS.get(name, {})

        # API key: explicit > env var
        env_key = provider_cfg.get("env_key")
        self.api_key = api_key or (os.environ.get(env_key) if env_key else None)

        # Base URL: explicit > provider default
        self.base_url = base_url or provider_cfg.get("base_url")

        # For anthropic, use the anthropic SDK
        self._is_anthropic = name == "anthropic"

    def chat(
        self,
        messages: list[Message],
        system: str = None,
        tools: list[dict] = None,
        temperature: float = 0.7,
    ) -> Response:
        """Send a chat completion request to the provider."""
        if self._is_anthropic:
            return self._chat_anthropic(messages, system, tools, temperature)
        return self._chat_openai(messages, system, tools, temperature)

    def _chat_openai(
        self,
        messages: list[Message],
        system: str = None,
        tools: list[dict] = None,
        temperature: float = 0.7,
    ) -> Response:
        """OpenAI-compatible API call."""
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key or "ollama", base_url=self.base_url)

        # Build messages
        api_messages = []
        if system:
            api_messages.append({"role": "system", "content": system})

        for msg in messages:
            m: dict[str, Any] = {"role": msg.role, "content": msg.content}
            if msg.tool_calls:
                m["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": tc.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ]
            if msg.tool_call_id:
                m["tool_call_id"] = msg.tool_call_id
            api_messages.append(m)

        # Build request
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": api_messages,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools

        # Call API
        completion = client.chat.completions.create(**kwargs)
        choice = completion.choices[0]

        # Parse response
        tool_calls = None
        if choice.message.tool_calls:
            tool_calls = [
                ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=tc.function.arguments,
                )
                for tc in choice.message.tool_calls
            ]

        return Response(
            content=choice.message.content or "",
            tool_calls=tool_calls,
            model=completion.model,
            usage={
                "prompt_tokens": completion.usage.prompt_tokens if completion.usage else 0,
                "completion_tokens": completion.usage.completion_tokens if completion.usage else 0,
            },
        )

    def _chat_anthropic(
        self,
        messages: list[Message],
        system: str = None,
        tools: list[dict] = None,
        temperature: float = 0.7,
    ) -> Response:
        """Anthropic API call using the anthropic SDK."""
        try:
            import anthropic
        except ImportError:
            raise ImportError("Install anthropic: pip install anthropic")

        client = anthropic.Anthropic(api_key=self.api_key)

        # Build messages
        api_messages = []
        for msg in messages:
            if msg.role == "system":
                continue  # System is passed separately
            if msg.role == "tool":
                # Anthropic uses "user" role for tool results
                api_messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": msg.tool_call_id,
                        "content": msg.content,
                    }],
                })
            elif msg.role == "assistant" and msg.tool_calls:
                content = []
                if msg.content:
                    content.append({"type": "text", "text": msg.content})
                for tc in msg.tool_calls:
                    content.append({
                        "type": "tool_use",
                        "id": tc.id,
                        "name": tc.name,
                        "input": json.loads(tc.arguments) if isinstance(tc.arguments, str) else tc.arguments,
                    })
                api_messages.append({"role": "assistant", "content": content})
            else:
                api_messages.append({"role": msg.role, "content": msg.content})

        # Convert OpenAI tool format to Anthropic format
        anthropic_tools = None
        if tools:
            anthropic_tools = []
            for t in tools:
                fn = t.get("function", {})
                anthropic_tools.append({
                    "name": fn.get("name", ""),
                    "description": fn.get("description", ""),
                    "input_schema": fn.get("parameters", {}),
                })

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": api_messages,
            "temperature": temperature,
            "max_tokens": 4096,
        }
        if system:
            kwargs["system"] = system
        if anthropic_tools:
            kwargs["tools"] = anthropic_tools

        response = client.messages.create(**kwargs)

        # Parse response
        content = ""
        tool_calls = None

        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                if tool_calls is None:
                    tool_calls = []
                tool_calls.append(ToolCall(
                    id=block.id,
                    name=block.name,
                    arguments=json.dumps(block.input),
                ))

        return Response(
            content=content,
            tool_calls=tool_calls,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
            },
        )
