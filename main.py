import os
import db as db

import disnake
import datetime

from dotenv import load_dotenv
from disnake.ext.commands import Bot


async def install_database():
    await db.database.connect()
    await db.db_setup(db.metadata)
    print("Database installed")


bot = Bot(command_prefix="!", intents=disnake.Intents.all(), reload=True)
bot.loop.run_until_complete(install_database())
bot.remove_command("help")


@bot.event
async def on_ready():
    date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"Bot is ready. Logged in at {date}")

@bot.event
async def on_resumed():
    date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"Bot resumed. Logged in at {date}")

@bot.event
async def on_disconnected():
    date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"Bot disconnected. Logged in at {date}")


for filename in os.listdir("./cogs") + os.listdir("./listeners"):
    if filename.endswith(".py") and not filename.startswith("_"):
        if filename in os.listdir("./cogs"):
            folder = "cogs"
        else:
            folder = "listeners"

        bot.load_extension(f"{folder}.{filename[:-3]}")
        print(f"Loaded {filename[:-3]}")


if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")
    database_url = os.getenv("DATABASE_URL")
    if not token or token == "" or not database_url or database_url == "":
        raise EnvironmentError("Please set the DISCORD_TOKEN and DATABASE_URL environment variables before running this bot.")

    bot.run(token)
