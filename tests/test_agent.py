"""Tests for the Agent class."""

from unittest.mock import MagicMock, patch

import pytest

from warpos import Agent, Memory, tool


@tool
def echo(text: str) -> str:
    """Echo the input text."""
    return text


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


class TestAgentInit:
    def test_agent_requires_name(self):
        with pytest.raises(TypeError):
            Agent()

    def test_agent_requires_model(self):
        with pytest.raises(TypeError):
            Agent(name="Test")

    def test_agent_default_values(self):
        agent = Agent(name="Test", model="gpt-4o")
        assert agent.name == "Test"
        assert agent.model == "gpt-4o"
        assert agent.instructions == ""
        assert agent.tools == []
        assert agent.memory is None

    def test_agent_with_tools(self):
        agent = Agent(name="Test", model="gpt-4o", tools=[echo, add])
        assert len(agent.tools) == 2

    def test_agent_with_memory(self):
        memory = Memory()
        agent = Agent(name="Test", model="gpt-4o", memory=memory)
        assert agent.memory is memory


class TestAgentRun:
    @patch("warpos.agent.Provider")
    def test_run_returns_string(self, mock_provider_class):
        mock_provider = MagicMock()
        mock_provider.complete.return_value = "Hello!"
        mock_provider_class.return_value = mock_provider

        agent = Agent(name="Test", model="gpt-4o")
        result = agent.run("Hi")
        assert isinstance(result, str)

    def test_run_with_memory_stores_messages(self):
        memory = Memory()
        agent = Agent(name="Test", model="gpt-4o", memory=memory)

        with patch.object(agent, "_get_provider") as mock_get:
            mock_provider = MagicMock()
            mock_provider.complete.return_value = "Hi there!"
            mock_get.return_value = mock_provider
            agent.run("Hello")

        messages = memory.get()
        assert len(messages) >= 2
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello"
