#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import os
import openai
import logging
import csv
import sys
import asyncio

from telegram import __version__ as TG_VER

openai.api_key = os.getenv('OPENAI_API_KEY') 
telegram_token = os.getenv('TELEGRAM_TOKEN')

async def ask_question(prompt):
    messages = [
        {"role": "user", "content": prompt}
    ]

    try:
        # Call the OpenAI API to get a response in German
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use the ChatGPT model
            messages=messages
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return str(e)

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        "Hi!\nWelcome to @CoachCrew! \n\nThis bot will write English definition of English words with examples.\nJust write an English word in single message.\n\n e.g. hello"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("To make the most of this bot, please ask for the definition of only one word at a time!");


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("echo called with message : " + update.message.text)
    word = update.message.text
    english_task = asyncio.create_task(ask_question(f"What is the concise meaning of word : {word}\n:"))
    examples_task = asyncio.create_task(ask_question(f"Write three concise examples with the word {word}"))

    english_response = await english_task
    examples_response = await examples_task

    await update.message.reply_text(english_response 
            + "\n------\n" + examples_response
            + "\n\nFollow @CoachCrew to be updated :D")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(telegram_token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
