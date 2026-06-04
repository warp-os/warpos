# Tools

Tools let your agent call Python functions. WarpOS uses the `@tool` decorator to make any function available to the agent.

## Basic Usage

```python
from warpos import Agent, tool

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    # Your implementation
    return f"Sunny, 72°F in {city}"

agent = Agent(
    name="WeatherBot",
    model="gpt-4o",
    tools=[get_weather]
)

response = agent.run("What's the weather in Tokyo?")
```

## Type Hints

Type hints are required — they tell the agent what arguments to expect:

```python
@tool
def search_database(query: str, limit: int = 10) -> list[dict]:
    """Search the database for records matching the query."""
    # Implementation
    return results
```

## Docstrings

The docstring becomes the tool's description shown to the agent. Keep it clear and specific:

```python
@tool
def fetch_url(url: str) -> str:
    """Fetch the content of a URL. Returns the response body as a string."""
    import httpx
    return httpx.get(url).text
```

## Async Tools

Tools can be async:

```python
@tool
async def fetch_data(url: str) -> str:
    """Fetch data from a URL asynchronously."""
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text
```

## Error Handling

If a tool raises an exception, WarpOS catches it and returns the error message to the agent. The agent can then decide how to handle it:

```python
@tool
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    return a / b  # ZeroDivisionError is caught automatically
```

## Tool Organization

For larger projects, organize tools in separate files:

```python
# tools/web.py
from warpos import tool

@tool
def fetch_url(url: str) -> str:
    """Fetch a URL."""
    ...

# tools/db.py
from warpos import tool

@tool
def query(sql: str) -> list:
    """Run a SQL query."""
    ...

# main.py
from warpos import Agent
from tools.web import fetch_url
from tools.db import query

agent = Agent(
    name="Assistant",
    model="gpt-4o",
    tools=[fetch_url, query]
)
```
