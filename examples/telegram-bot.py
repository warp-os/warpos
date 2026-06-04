"""
Telegram Bot Example with WarpOS

Requirements:
    pip install warpos python-telegram-bot

Set your environment variables:
    export TELEGRAM_TOKEN=your-bot-token
    export OPENAI_API_KEY=your-api-key
"""

import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from warpos import Agent, Memory, tool

# Tools for the bot
@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    # In production, call a weather API
    return f"☀️ 22°C and sunny in {city}"


@tool
def translate(text: str, target_language: str) -> str:
    """Translate text to the target language."""
    # In production, call a translation API
    return f"[Translated to {target_language}]: {text}"


# Memory per user
memories: dict[int, Memory] = {}


def get_agent(user_id: int) -> Agent:
    if user_id not in memories:
        memories[user_id] = Memory(max_messages=50)
    return Agent(
        name="WarpBot",
        model="gpt-4o",
        instructions=(
            "You are a helpful Telegram assistant. "
            "Keep responses concise and well-formatted. "
            "Use tools when relevant."
        ),
        tools=[get_weather, translate],
        memory=memories[user_id],
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! I'm WarpBot, powered by WarpOS.\n\n"
        "Send me any message and I'll help you out!"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    agent = get_agent(user_id)
    user_message = update.message.text

    # Show typing indicator
    await update.message.chat.send_action("typing")

    # Run the agent
    response = agent.run(user_message)

    await update.message.reply_text(response)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in memories:
        memories[user_id].clear()
    await update.message.reply_text("🔄 Memory cleared!")


def main():
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        print("Error: Set TELEGRAM_TOKEN environment variable")
        return

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot started!")
    app.run_polling()


if __name__ == "__main__":
    main()
