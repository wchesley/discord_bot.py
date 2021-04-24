import os, tracemalloc, sys
import discord
import logging

from threading import Thread
from utils import default
from utils.data import Bot, HelpFormat
from data.mongoDB import MongoDB_Context
from valheim_server.log_dog import ValheimLogDog

# tracemalloc.start()
config = default.config()
default.s_print("Logging in...")

bot = Bot(
    command_prefix=config["prefix"], prefix=config["prefix"],
    owner_ids=config["owners"], command_attrs=dict(hidden=True), help_command=HelpFormat(),
    allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False),
    intents=discord.Intents(  # kwargs found at https://discordpy.readthedocs.io/en/latest/api.html?highlight=intents#discord.Intents
        guilds=True, members=True, messages=True, reactions=True, presences=True
    )
)

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")
        logging.info(f'Loaded extension: {name}')

try:
    log_dog = Thread(target=ValheimLogDog, args=(bot,), daemon=True)
    log_dog.start()
    bot.run(config['token'])
except (KeyboardInterrupt, SystemExit) as e:
    default.s_print(f"EXIT RECEIVED: {e}")
    sys.exit()
except Exception as e:
    default.s_print(f'Some other error? {e}')
    sys.exit()