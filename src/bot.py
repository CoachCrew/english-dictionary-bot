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
import datetime
import sqlite3
import google.cloud.texttospeech as tts

from telegram import __version__ as TG_VER

openai.api_key = os.getenv('OPENAI_API_KEY') 
telegram_token = os.getenv('TELEGRAM_TOKEN')
words = {}

connection = sqlite3.connect('coachcrew.db')
mycursor = connection.cursor()

def create_table():
  create_table_query = '''
    CREATE TABLE IF NOT EXISTS german_words (
        word TEXT, 
        examples TEXT, 
        english TEXT, 
        persian TEXT,
        word_voice TEXT,
        examples_voice TEXT
    )
  '''
  mycursor.execute(create_table_query)

def insert_word(word, example, english, persian, word_voice, examples_voice):
  insert_query = '''
    INSERT INTO german_words 
      (word, examples, english, persian, word_voice, examples_voice) 
      VALUES (?, ?, ?, ?, ?, ?)
  '''
  values = (word, example, english, persian, word_voice, examples_voice)
  mycursor.execute(insert_query, values)
  connection.commit()

def find_word(word):
  select_query = '''
    SELECT * FROM german_words WHERE word = ? 
  '''
  mycursor.execute(select_query, (word,))
  rows = mycursor.fetchall()
  if rows:
    return rows[0]
  else:
    return None

def text_to_wav(voice_name: str, text: str, filename: str):
    voice_file = "wav/" + filename.replace(' ', '')
    language_code = "-".join(voice_name.split("-")[:2])
    text_input = tts.SynthesisInput(text=text)
    voice_params = tts.VoiceSelectionParams(
        language_code=language_code, name=voice_name
    )
    audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

    client = tts.TextToSpeechClient()
    response = client.synthesize_speech(
        input=text_input,
        voice=voice_params,
        audio_config=audio_config,
    )

    filename = f"{voice_file}.wav"
    with open(filename, "wb") as out:
        out.write(response.audio_content)
        print(f'Generated speech saved to "{filename}"')
    return filename


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

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        "Hi!\nWelcome to @CoachCrew! \n\nThis bot will write English and German definition of German words.\nJust write a German word in single message.\n\n e.g. hallo"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("To make the most of this bot, please ask for the definition of only one word at a time!");


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(update.effective_user)
    print(update.message.text)
    word = update.message.text.lower().lstrip().rstrip()

    examples_response = ""
    english_response = ""
    persian_response = "" 
    word_voice_file = ""
    examples_voice_file = ""

    search_result = find_word(word.lower()) 
    if (search_result == None):
        await update.message.reply_text(
            f"Searching for the definition of {word}. Please wait a few seconds."
        )
        await update.message.reply_text(
            f"Subscribe to our channel @CoachCrew to get the latest news."
        )

        english_task  = asyncio.create_task(ask_question(f"What is the meaning of word : {word}\n:"))
        examples_task = asyncio.create_task(ask_question(f"Write three examples with the word: {word}\n:"))
        persian_task  = asyncio.create_task(ask_question(f"معنی کلمه {word} در فارسی چیست?\n"))

        examples_response = await examples_task
        english_response = await english_task
        persian_response = await persian_task

        word_voice_file = text_to_wav("en-US-Neural2-C", word, word[:20])
        examples_voice_file = text_to_wav("en-US-Neural2-C", examples_response, word[:20] + "examples")

        insert_word(word, examples_response, english_response, persian_response, word_voice_file, examples_voice_file)
    else:
        examples_response = search_result[1]
        english_response = search_result[2]
        persian_response = search_result[3]
        word_voice_file = search_result[4]
        examples_voice_file = search_result[5]

    word = word.lower()

    response = english_response \
            + "\n------\n" + examples_response \
            + "\n\n------\n فارسی: " + persian_response \
            + "\n\nFollow @CoachCrew to be updated :D"

    chunk_size = 4000
    for i in range(0, len(response), chunk_size):
        await update.message.reply_text(response[i:i+chunk_size])

    await context.bot.send_voice(update.message.chat_id, word_voice_file)

    await context.bot.send_voice(update.message.chat_id, examples_voice_file)


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
    create_table()
    main()
