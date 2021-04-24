## TODO: 
# set log file location (Config.json?)
# Read file up to present
# Read any new lines written to file
# Pass information from within log files to log_parser.py
# avoid duplicates? 

import os
import discord
import logging
import time
import aiofiles
import asyncio

from utils import default, http
from data.mongoDB import MongoDB_Context
from .log_parser import LogLine
# from . import steam_api
from utils.default import s_print

SLEEP_SECONDS = 1

class ValheimLogDog:

    def __init__(self, bot):
        self.config = default.config()
        self.bot = bot
        self.data = {
            'SteamID':'',
            'SteamName':'',
            'ZDOID':'',
            'steam_login_time':'',
            'ZDOID_login_time':'',
            'online':False,
        }
        self.active = True
        self.start()

    def set_activity_state(self):
        # Closes this thread when program exits
        s_print("Kill signal set: ")
        self.active = False

    def start(self):
        s_print(f"Fetching log file at: {self.config['log_file']}")
        while self.active == True:
            with open(self.config['log_file'], 'r') as log_file:
                s_print(f'opened context for log file at: {log_file}')
                for new_lines in self.line_watcher(log_file):
                    s_print(f'Processing the lines found...')
                    new_lines = self.filter_lines(new_lines)
                    s_print(f'\t> Processed lines: {new_lines}')

                    for line in new_lines:
                        #parse lines read here:
                        s_print(f'OG Line: {line}')
                        log_line = LogLine.remove_text_inside_brackets(line)
                        s_print(f'log_line?: {log_line}')
                        date, message = LogLine.remove_date(log_line)
                        if date or message == 1:
                            s_print('no date found, ignoring')
                        else:
                            self.extract_log_parts(message, date)
        s_print('closing log file')                            
        log_file.close()

    def line_watcher(self, file):
        """Generator function that returns the new line entered."""

        file.seek(0, os.SEEK_END)

        while True:
            # Reads last line
            new_lines = file.readlines()
            # sleep if file hasn't been updated
            if not new_lines:
                s_print(f'No new lines. Sleeping {SLEEP_SECONDS}')
                time.sleep(SLEEP_SECONDS) # sleep handled by asyncio event loop in /cogs/valheim_log_cog.py
                #await asyncio.sleep(1)
                continue
            s_print('New line(s) found!')

            for l in new_lines:
                s_print('\t> {}'.format(l.replace('\n', '')))

            yield new_lines
    
    def filter_lines(self, lines):
        """Filters the log lines to only return the ones that have actual values."""
        return [l for l in lines if l != '\n' and len(l) > 1]

    def extract_log_parts(self, message, date):
        """Get the goods from the valheim log message"""
        # Trailing space on the end is intentional, needed to remove that part of the log message
        # Return messages are used to verify data in the tests
        steam_connect_msg = 'Got connection SteamID '
        zDOID_connect = 'Got character ZDOID from '
        current_connections = 'Connections'
        disconnect = "Closing Socket "
        s_print(f'message: {message}')
        if steam_connect_msg in message:
            self.data['SteamID'] = message.replace(steam_connect_msg, '')
            default.s_print(f"STEAMID: {self.data['SteamID']}")
            self.data['steam_login_time'] = date
            self.data['SteamName'] = self.get_steam_persona(self.data['SteamID'])
            return self.data['SteamID']
        elif zDOID_connect in message:
            # Death message: Got character ZDOID from Bytes : 0:0
            if message[-1] == "0":
                split = message.split(' ')
                toon = split[4] # Should be ZDOID (in game toon name)
                # Don't want to update database while testing...
                new_death_count = MongoDB_Context.update_death_count(1)
                default.s_print(f'new death count: {new_death_count}')
                self.bot.dispatch('on_death', new_death_count, toon) ## Emmit death event: 
                return f'{toon} death!'
            else: 
                full_message = message.replace(zDOID_connect,'')
                full_message = full_message.split(' ')
                self.data['ZDOID'] = full_message[0]
                self.data['ZDOID_login_time'] = date
                return self.data['ZDOID']
        elif current_connections in message: 
            s_print(f'current connections: {message}')
            connections = message.split(' ')
            # log message should look like: 'Connections 1 ZDOS:130588  sent:0 recv:422'
            return connections[1]
        elif disconnect in message:
            return message.replace(disconnect,'') # Should be steamID of player who disconnected

    def compare_login_time(self, steam_login_time, zdoid_login_time):
        # TODO: Convert strings to datetime objects here: 
        # Reasoning: It's easier to deal with strings, only need actual datetime objects for this calculation: 
        time_diff = steam_login_time - zdoid_login_time
        time_diff = abs(time_diff.total_seconds()) # steam login comes first, value SHOULD be negative.
        if time_diff < 120:
            return True
        else:
            return False

    async def get_steam_persona(self, steamID):
        # More import errors I don't feel like debugging anymore: 
        # Instead I"ll just utalize the http class and make requests the old fashioned way
        # SteamWebAPI: https://developer.valvesoftware.com/wiki/Steam_Web_API
        # try:
        #     self.data['SteamName'] = SteamIDToVanityName(steamID)
        #     s_print(f"Found Steam Name: {self.data['SteamName']}")
        # except Exception as e:
        #     s_print(f'Error getting Steam Name: {e}')
        if steamID is None or " ":
            steamID = self.data['SteamID']
        steam_url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={self.config['steam_api_key']}&steamids={steamID}"
        response = http.get(steam_url) 
        return await response['response']['players'][0]['personaname']
