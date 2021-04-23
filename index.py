import os, tracemalloc, sys
import discord
import logging
import concurrent.futures

from utils import default
from utils.data import Bot, HelpFormat
from data.mongoDB import MongoDB_Context
from valheim_server.log_dog import ValheimLogDog

# tracemalloc.start()
config = default.config()
print("Logging in...")

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

# try:
#     print(f"Testing connection to mongoDB instance at {config['db_url']}")
#     db = MongoDB_Context()
# #
# except Exception as e:
#     print(f'Error connecting to database: {e}')

# try:
#     print(f'opening log file:')
#     bot.loop.create_task(ValheimLogCog(bot))
# except Exception as e:
#     print(f'error getting log file: {e}')
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    try:
        print('starting log_dog: ')
        log = "null?"
        try:
            log = executor.submit(ValheimLogDog.start, bot)
        except Exception as e:
            print(f'log thread state?: {log.running()}\nERROR: {e}')
        print(f'log_thread state: {log.running()}')
        executor.submit(bot.run(config["token"]))
    except Exception as e:
        print(f'other error: {e}')
        sys.exit()
    
