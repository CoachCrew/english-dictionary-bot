# CoachCrew English Dictionary Bot

The repository contains a Telegram. The bot uses [OpenAI api](https://openai.com) 
to write english meaning of words given to the bot, with examples. 

To use the bot, first create a bot using @Botfather, and set the following 
two environment variables: `TELEGRAM_TOKEN`, `OPENAI_API_KEY`. The run
the programming using the following command.
```bash
export TELEGRAM_TOEKN=xxx
export OPENAI_API_KEY=xxx
export GOOGLE_APPLICATION_CREDENTIALS=xxx
python3 src/bot.py
```

Here's an example output from the bot

> crew
>
> A group of people working together towards a common 
> goal or performing specific tasks, typically on a ship 
> or aircraft.
>
> ------
>
> 1. The film crew worked tirelessly to capture the perfect shot.
>
> 2. The rescue crew arrived just in time to save the stranded hikers.
>
> 3. The airline crew ensured the passengers had a comfortable and safe flight.
>
> 
> Follow @CoachCrew to be updated :D
