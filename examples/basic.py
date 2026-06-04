"""Example: Basic WarpOS agent."""

from warpos import Agent, tool


@tool
def search(query: str) -> str:
    """Search the web for information."""
    # This is a placeholder — replace with real search (Tavily, SerpAPI, etc.)
    return f"Search results for '{query}': [1] Example result about {query}. [2] Another relevant finding."


@tool
def calculate(expression: str) -> str:
    """Evaluate a math expression."""
    try:
        result = eval(expression)  # noqa: S307
        return str(result)
    except Exception as e:
        return f"Error: {e}"


agent = Agent(
    name="demo-agent",
    instructions=(
        "You are a helpful research assistant. "
        "Use tools when needed. Answer clearly and keep responses concise."
    ),
    model="gpt-4o-mini",  # Change to your preferred model
    tools=[search, calculate],
    memory=True,
)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        agent.serve(port=3000)
    else:
        print(f"Agent '{agent.config.name}' ready. Type 'quit' to exit.\n")
        while True:
            msg = input("You: ")
            if msg.lower() in ("quit", "exit", "q"):
                break
            response = agent.run(msg)
            print(f"\n{agent.config.name}: {response}\n")
