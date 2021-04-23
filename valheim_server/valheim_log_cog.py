import os, signal
import concurrent.futures
from threading import Thread
import discord 
from discord.ext import commands, tasks
from utils import default 
from valheim_server.log_dog import ValheimLogDog

class ValheimLogCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.log_dog = ValheimLogDog(self.bot)
        self.start_log_dog()
        #self.lock = asyncio.Lock()
        #self.log_task = self.loop.create_task(self.log_dog_loop())

    # async def run_log_dog(self):
    #     await ValheimLogDog(self.bot).start()

   
    def log_dog_loop(self):
        print('started log event loop')
        self.log_dog.start()
    
    def start_log_dog(self):
        try:
            self.executor.submit(self.log_dog_loop)
        except (KeyboardInterrupt, SystemExit, InterruptedError):
            self.stop_log_dog()

    # Clean up file connection, DB connection and exit gracefully...I hope? 
    def stop_log_dog(self):
        self.log_dog.set_activity_state()
        self.executor.shutdownNow()
        

# def setup(bot):
#     bot.add_cog(ValheimLogCog(bot))