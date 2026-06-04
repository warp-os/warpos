# Providers

WarpOS supports multiple LLM providers. You specify the provider as part of the model string.

## OpenAI

```python
from warpos import Agent

agent = Agent(name="Bot", model="gpt-4o")
```

**Environment variable**: `OPENAI_API_KEY`

**Supported models**: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `gpt-4`, `gpt-3.5-turbo`

## Anthropic

```python
agent = Agent(name="Bot", model="anthropic/claude-3-5-sonnet-20241022")
```

**Environment variable**: `ANTHROPIC_API_KEY`

**Supported models**: `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`, `claude-3-haiku-20240307`

## Groq

```python
agent = Agent(name="Bot", model="groq/llama3-70b-8192")
```

**Environment variable**: `GROQ_API_KEY`

**Supported models**: `llama3-70b-8192`, `llama3-8b-8192`, `mixtral-8x7b-32768`

## DeepSeek

```python
agent = Agent(name="Bot", model="deepseek/deepseek-chat")
```

**Environment variable**: `DEEPSEEK_API_KEY`

**Supported models**: `deepseek-chat`, `deepseek-coder`

## Ollama (Local)

No API key needed. Make sure Ollama is running:

```bash
ollama serve
ollama pull llama3
```

```python
agent = Agent(name="Bot", model="ollama/llama3")
```

**Default host**: `http://localhost:11434`

To use a custom host:

```python
from warpos.providers import OllamaProvider

provider = OllamaProvider(host="http://192.168.1.100:11434")
agent = Agent(name="Bot", model="ollama/llama3", provider=provider)
```

## Cerebras

```python
agent = Agent(name="Bot", model="cerebras/llama3-8b")
```

**Environment variable**: `CEREBRAS_API_KEY`

## Custom Providers

You can create your own provider by implementing the `Provider` interface:

```python
from warpos.providers import Provider

class MyProvider(Provider):
    async def complete(self, messages, model, tools=None, stream=False):
        # Your implementation here
        pass

    async def stream(self, messages, model, tools=None):
        # Your streaming implementation here
        pass
```

See the [API Reference](api-reference.md) for full details.
