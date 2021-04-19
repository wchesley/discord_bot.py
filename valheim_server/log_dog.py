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

from utils import default
from data.mongoDB import MongoDB_Context
from .log_parser import LogLine

SLEEP_SECONDS = 1

class ValheimLogDog:

    def __init__(self, bot):
        self.config = default.config()
        self.bot = bot
        self.data = {
            'SteamID':'',
            'ZDOID':'',
            'steam_login_time':'',
            'ZDOID_login_time':'',
            'online':False,
        }

    async def start(self):
        print(f"Fetching log file at: {self.config['log_file']}")
        with await open(self.config['log_file'], 'r') as log_file:
            print(f'opened context for log file at: {log_file}')
            for new_lines in self.line_watcher(log_file):
                print(f'Processing the lines found...')
                new_lines = self.filter_lines(new_lines)
                print(f'\t> Processed lines: {new_lines}')

                for line in new_lines:
                    #parse lines read here:
                    log_line = LogLine(line)
                    self.extract_log_parts(log_line.message,log_line.date)

    def line_watcher(self, file):
        """Generator function that returns the new line entered."""

        file.seek(0, os.SEEK_END)

        while True:
            # Reads last line
            new_lines = file.readlines()
            # sleep if file hasn't been updated
            if not new_lines:
                print(f'No new lines. Sleeping {SLEEP_SECONDS}')
                time.sleep(SLEEP_SECONDS)
                continue
            print('New line(s) found!')

            for l in new_lines:
                print('\t> {}'.format(l.replace('\n', '')))

            yield new_lines
    
    def filter_lines(self, lines):
        """Filters the log lines to only return the ones that have actual values."""
        return [l for l in lines if l != '\n' and len(l) > 1]

    def extract_log_parts(self, message, date):
        """Get the goods from the valheim log message"""
        # Trailing space on the end is intentional, needed to remove that part of the log message
        steam_connect_msg = 'Got connection SteamID '
        zDOID_connect = 'Got character ZDOID from '
        current_connections = 'Connections'
        disconnect = "Closing Socket "
        print(f'message: {message}')
        if steam_connect_msg in message:
            self.data['SteamID'] = message.replace(steam_connect_msg, '')
            self.data['steam_login_time'] = date
            return self.data['SteamID']
        elif zDOID_connect in message:
            # Death message: Got character ZDOID from Bytes : 0:0
            if message[-1] == "0":
                split = message.split(' ')
                toon = split[4] # Should be ZDOID (in game toon name)
                # Don't want to update database while testing...
                new_death_count = MongoDB_Context.update_death_count(1)
                self.bot.emmit('on_death',toon,new_death_count) ## Emmit death event: 
                return f'{toon} death!' 
            full_message = message.replace(zDOID_connect,'')
            full_message = full_message.split(' ')
            return full_message[0]
        elif current_connections in message: 
            print(f'current connections: {message}')
            connections = message.split(' ')
            # log message should look like: 'Connections 1 ZDOS:130588  sent:0 recv:422'
            return connections[1]
        elif disconnect in message:
            return message.replace(disconnect,'') # Should be steamID of player who disconnected

    def compare_login_time(self, steam_login_time, zdoid_login_time):
        time_diff = steam_login_time - zdoid_login_time
        time_diff = abs(time_diff.total_seconds()) # steam login comes first, value SHOULD be negative.
        if time_diff < 120:
            pass