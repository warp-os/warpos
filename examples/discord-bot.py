"""
Discord Bot Example with WarpOS

Requirements:
    pip install warpos discord.py

Set your environment variables:
    export DISCORD_TOKEN=your-bot-token
    export OPENAI_API_KEY=your-api-key
"""

import os
import discord
from warpos import Agent, Memory, tool

# Tools for the bot
@tool
def roll_dice(sides: int = 6) -> str:
    """Roll a die with the given number of sides."""
    import random
    result = random.randint(1, sides)
    return f"🎲 You rolled a {result} (d{sides})"


@tool
def flip_coin() -> str:
    """Flip a coin."""
    import random
    result = random.choice(["Heads", "Tails"])
    return f"🪙 {result}!"


# Memory per channel
memories: dict[int, Memory] = {}


def get_agent(channel_id: int) -> Agent:
    if channel_id not in memories:
        memories[channel_id] = Memory(max_messages=100)
    return Agent(
        name="WarpBot",
        model="gpt-4o",
        instructions=(
            "You are a friendly Discord bot. Keep responses short and fun. "
            "Use emoji when appropriate."
        ),
        tools=[roll_dice, flip_coin],
        memory=memories[channel_id],
    )


# Discord setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"✅ {client.user} is online!")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    # Only respond when mentioned
    if client.user not in message.mentions:
        return

    # Remove the mention from the message
    content = message.content.replace(f"<@{client.user.id}>", "").strip()

    if not content:
        await message.channel.send("Hey! Mention me with a question. 👋")
        return

    # Get or create agent for this channel
    agent = get_agent(message.channel.id)

    # Show typing indicator
    async with message.channel.typing():
        response = agent.run(content)

    await message.channel.send(response)


def main():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("Error: Set DISCORD_TOKEN environment variable")
        return
    client.run(token)


if __name__ == "__main__":
    main()
