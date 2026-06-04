"""WarpOS CLI — warp init, warp serve."""

from __future__ import annotations

import os
import click
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="warp")
def main():
    """WarpOS — The open-source platform for AI agents."""
    pass


@main.command()
@click.argument("name", default="my-agent")
def init(name: str):
    """Scaffold a new agent project."""
    os.makedirs(name, exist_ok=True)

    agent_py = f'''"""Your WarpOS agent."""

from warpos import Agent, tool


@tool
def search(query: str) -> str:
    """Search the web for information."""
    # Replace with real implementation
    return f"Results for: {{query}}"


agent = Agent(
    name="{name}",
    instructions="You are a helpful research assistant. Answer questions clearly and concisely.",
    model="gpt-4o-mini",
    tools=[search],
    memory=True,
)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        agent.serve()
    else:
        # Interactive mode
        print(f"Agent '{{name}}' ready. Type 'quit' to exit.\\n")
        while True:
            msg = input("You: ")
            if msg.lower() in ("quit", "exit", "q"):
                break
            response = agent.run(msg)
            print(f"\\n{{name}}: {{response}}\\n")
'''

    with open(os.path.join(name, "agent.py"), "w") as f:
        f.write(agent_py)

    env_file = os.path.join(name, ".env")
    with open(env_file, "w") as f:
        f.write("# WarpOS — Set your API keys here\n")
        f.write("OPENAI_API_KEY=\n")
        f.write("# ANTHROPIC_API_KEY=\n")
        f.write("# GROQ_API_KEY=\n")

    console.print(Panel(
        f"[green]✓[/] Created project: [bold]{name}/[/]\n"
        f"  → {name}/agent.py\n"
        f"  → {name}/.env\n\n"
        f"[dim]Next steps:[/]\n"
        f"  cd {name}\n"
        f"  # Edit .env with your API key\n"
        f"  python agent.py          # interactive mode\n"
        f"  python agent.py serve    # start chat UI on localhost:3000",
        title="[bold]warp init[/]",
        border_style="yellow",
    ))


@main.command()
@click.argument("path", default="agent.py")
@click.option("--port", "-p", default=3000, help="Port to serve on")
@click.option("--host", "-h", default="0.0.0.0", help="Host to bind to")
def serve(path: str, port: int, host: str):
    """Serve an agent with chat UI."""
    import importlib.util

    if not os.path.exists(path):
        console.print(f"[red]Error:[/] Agent file not found: {path}")
        return

    # Load the agent module
    spec = importlib.util.spec_from_file_location("agent_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Find the Agent instance
    from warpos.agent import Agent
    agent = None
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, Agent):
            agent = attr
            break

    if not agent:
        console.print("[red]Error:[/] No Agent instance found in the file.")
        return

    console.print(Panel(
        f"[green]✓[/] Agent: [bold]{agent.config.name}[/]\n"
        f"  Model: {agent.config.model}\n"
        f"  Tools: {', '.join(agent._tool_defs.keys()) or 'none'}\n"
        f"  Memory: {'on' if agent.config.memory else 'off'}\n\n"
        f"  [dim]Chat UI: http://localhost:{port}[/]",
        title="[bold]warp serve[/]",
        border_style="yellow",
    ))

    agent.serve(host=host, port=port)


if __name__ == "__main__":
    main()
