"""Tests for providers."""

import pytest

from warpos.providers import Provider


class TestProviderInterface:
    def test_provider_is_abstract(self):
        with pytest.raises(TypeError):
            Provider()

    def test_openai_provider_import(self):
        from warpos.providers import OpenAIProvider
        assert OpenAIProvider is not None

    def test_anthropic_provider_import(self):
        from warpos.providers import AnthropicProvider
        assert AnthropicProvider is not None

    def test_groq_provider_import(self):
        from warpos.providers import GroqProvider
        assert GroqProvider is not None

    def test_deepseek_provider_import(self):
        from warpos.providers import DeepSeekProvider
        assert DeepSeekProvider is not None

    def test_ollama_provider_import(self):
        from warpos.providers import OllamaProvider
        assert OllamaProvider is not None

    def test_cerebras_provider_import(self):
        from warpos.providers import CerebrasProvider
        assert CerebrasProvider is not None


class TestProviderSelection:
    def test_resolve_openai_model(self):
        from warpos.providers import resolve_provider
        provider = resolve_provider("gpt-4o")
        assert provider.__class__.__name__ == "OpenAIProvider"

    def test_resolve_anthropic_model(self):
        from warpos.providers import resolve_provider
        provider = resolve_provider("anthropic/claude-3-5-sonnet-20241022")
        assert provider.__class__.__name__ == "AnthropicProvider"

    def test_resolve_groq_model(self):
        from warpos.providers import resolve_provider
        provider = resolve_provider("groq/llama3-70b-8192")
        assert provider.__class__.__name__ == "GroqProvider"

    def test_resolve_ollama_model(self):
        from warpos.providers import resolve_provider
        provider = resolve_provider("ollama/llama3")
        assert provider.__class__.__name__ == "OllamaProvider"

    def test_unknown_model_raises(self):
        from warpos.providers import resolve_provider
        with pytest.raises(ValueError, match="Unknown provider"):
            resolve_provider("unknown/model")
