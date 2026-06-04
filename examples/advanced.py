"""
Advanced WarpOS Example

Demonstrates:
- Multiple tools
- Custom provider configuration
- Memory usage
- Streaming responses
"""

import asyncio
from warpos import Agent, Memory, tool


# Define multiple tools
@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    # In production, call a real search API
    return f"Results for '{query}': Top 3 results from the web."


@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression)  # noqa: S307
        return str(result)
    except Exception as e:
        return f"Error: {e}"


@tool
def get_current_time() -> str:
    """Get the current date and time."""
    from datetime import datetime
    return datetime.now().isoformat()


@tool
def save_note(title: str, content: str) -> str:
    """Save a note with a title."""
    # In production, save to a database
    return f"Note '{title}' saved successfully."


async def main():
    # Set up memory
    memory = Memory(max_messages=50)

    # Create agent with multiple tools
    agent = Agent(
        name="ResearchAssistant",
        model="gpt-4o",
        instructions="""You are a research assistant with access to tools.
        Always use tools when relevant. Be concise and factual.
        When you find useful information, save it as a note.""",
        tools=[search_web, calculate, get_current_time, save_note],
        memory=memory,
        temperature=0.3,
    )

    # Run a multi-step task
    response = agent.run(
        "Search for the latest developments in quantum computing, "
        "then save a summary as a note."
    )
    print("Response:", response)

    # Stream a response
    print("\n--- Streaming ---")
    async for token in agent.run_stream("What time is it?"):
        print(token, end="", flush=True)
    print()

    # Check memory
    print("\n--- Memory ---")
    for msg in memory.get():
        print(f"[{msg['role']}] {msg['content'][:80]}...")


if __name__ == "__main__":
    asyncio.run(main())
