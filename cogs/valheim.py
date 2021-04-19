import discord
import asyncio
import subprocess
import aiohttp
import requests

from datetime import datetime
from requests import get
from discord.ext import commands
from utils import permissions, default
from data.mongoDB import MongoDB_Context

mongo = MongoDB_Context()

class Valheim(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()

    def parse_systemctl_time(time):
        days = [
            'Mon',
            'Tue',
            'Wed',
            'Thur',
            'Fri',
            'Sat',
            'Sun'
        ]
        timezone = [
            'CDT'
        ]
        for day in days:
            if day in time:
                time = time.replace(day,'')
        for tz in timezone:
            if tz in time: 
                time = time.replace(tz,'')
        # Remove trailing whitespace: 
        time = time.strip()
        print(f"time: {time}")
        return time

    @commands.command(aliases=['status','valheim_stats','valheim_info'])
    @commands.has_any_role('Valheim','Admin')
    async def valheim(self, ctx):
        """Gets Valheim server status"""
        print("getting valheim server status:")
        result = subprocess.run(['systemctl show -p ActiveState,SubState,ExecMainStartTimestamp --value valheim'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        print(result.returncode)
        if result.stdout:
            test = result.stdout.splitlines()
            if test[0] != '':
                format_time = Valheim.parse_systemctl_time(test[0])
                format_time = datetime.strptime(format_time, '%Y-%m-%d %H:%M:%S')
            else:
                test[0] = 'N/A' 
            embedColour = discord.Embed.Empty
            if hasattr(ctx, 'guild') and ctx.guild is not None:
                embedColour = ctx.me.top_role.colour
            embed = discord.Embed(colour=embedColour)
            embed.add_field(name="Server State", value=test[2], inline=True)
            embed.add_field(name="Sub State", value=test[1], inline=True)
            embed.add_field(name="Up Time", value=default.timeago(datetime.now() - format_time))
            await ctx.send(content="**Valheim Server Status**", embed=embed)
        if result.stderr:
            print(f'stderr: {result.stderr}')
            await ctx.send(f'Error retreiving server status')
    
    @commands.command(aliases=['valheim_restart'])
    @commands.has_any_role('Valheim','Admin')
    async def restart_valheim(self,ctx):
        """Restart Valheim Service"""
        print(f"restart initated by: {ctx.message.author}")
        result = subprocess.run(['systemctl restart valheim'],stdout=subprocess.PIPE,stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        if result.returncode == 0:
            await ctx.send("Server restart initiated, please allow 30 seconds for the service to start back up")
        else:
            await ctx.send(f"Server couldn't be restarted, exit code {result.returncode}\nError:{result.stderr}")

    @commands.command()
    @commands.has_any_role('Valheim','Admin')
    async def address(self,ctx):
        """ DM's you server public IP, must have Valheim or Admin role"""
        ip=""
        try:
            r = get('https://api.ipify.org').text
            if r != None:
                ip = r
        except requests.exceptions.ConnectionError:
            return await ctx.send("error communicating with API")
        except  requests.exceptions.HTTPError:
            return await ctx.send("Bad response from API")
        if hasattr(ctx, 'guild') and ctx.guild is not None:
            await ctx.send(f"Sending you a private message with server public IP **{ctx.author.name}**")
        await ctx.author.send(f"🎁 **Public IP:**\n{ip}")

    @commands.command()
    @commands.is_owner()
    async def update_death(self,ctx):
        """Bytes utility method to artificially increase total death count"""
        count = MongoDB_Context.update_death_count(mongo,1)
        await ctx.send(f"Increased death count, we up to: {count}")

 
def setup(bot):
    bot.add_cog(Valheim(bot))