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
import asyncio
import random
import json
import steam.webapi

from utils import default, http
from data.mongoDB import MongoDB_Context
from .log_parser import LogLine
from datetime import datetime
# from . import steam_api

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
    
    async def start(self):
        default.s_print(f"Fetching log file at: {self.config['log_file']}")
        while True:
            with open(self.config['log_file'], 'r', os.O_NONBLOCK) as log_file:
                default.s_print(f'opened context for log file at: {log_file}')
                async for new_lines in self.line_watcher(log_file):
                    default.s_print(f'Processing the lines found...')
                    new_lines = self.filter_lines(new_lines)
                    default.s_print(f'\t> Processed lines: {new_lines}')

                    for line in new_lines:
                        #parse lines read here:
                        default.s_print(f'OG Line: {line}')
                        log_line = LogLine.remove_text_inside_brackets(line)
                        default.s_print(f'log_line?: {log_line}')
                        date, message = LogLine.remove_date(log_line)
                        default.s_print(f'DATE: {date}\nMESSAGE: {message}')
                        await self.extract_log_parts(message, date)
                        default.s_print(f'****Processed log lines COMPLETE*****\nBEGIN DATA CHECK:')
                        if self.data['steam_login_time'] and self.data['ZDOID_login_time']:
                            default.s_print('Have login times! ')
                            if self.compare_login_time(self.data['steam_login_time'], self.data['ZDOID_login_time']):
                                default.s_print('login times are within two minutes, close enough for a match!')
                                MongoDB_Context.update_player(self.data)
                                default.s_print(f'data obj with player: {self.data}')
                                default.s_print(f'added or updated player!')
                                self.clear_data()
                                default.s_print(f'data cleared')
                            else:
                                default.s_print(f'Times arent close enough')
                        else:
                            default.s_print(f'do not have one or the other login time. ')
        default.s_print('closing log file')                            
        log_file.close()

    async def line_watcher(self, file):
        """Generator function that returns the new line entered."""

        file.seek(0, os.SEEK_END)

        while True:
            # Reads last line
            new_lines = file.readlines()
            # sleep if file hasn't been updated
            if not new_lines:
                # default.s_print(f'No new lines. Sleeping {SLEEP_SECONDS}') # Too spammy for testing
                #time.sleep(SLEEP_SECONDS) # sleep handled by asyncio event loop in /cogs/valheim_log_cog.py
                await asyncio.sleep(SLEEP_SECONDS)
                continue
            default.s_print('New line(s) found!')

            for l in new_lines:
                default.s_print('\t> {}'.format(l.replace('\n', '')))

            yield new_lines
    
    def filter_lines(self, lines):
        """Filters the log lines to only return the ones that have actual values."""
        return [l for l in lines if l != '\n' and len(l) > 1]

    async def extract_log_parts(self, message, date):
        """Get the goods from the valheim log message"""
        # Trailing space on the end is intentional, needed to remove that part of the log message
        # Return messages are used to verify data in the tests
        steam_connect_msg = 'Got connection SteamID '
        zDOID_connect = 'Got character ZDOID from '
        current_connections = 'Connections'
        disconnect = "Closing Socket "
        default.s_print(f'message: {message}')
        default.s_print(f'Date: {date}')
        # if/elif block to determine what we found in log message: 
        if steam_connect_msg in message:
            self.data['SteamID'] = message.replace(steam_connect_msg, '')
            self.data['steam_login_time'] = date
            steam_name = 'no async error maybe?'
            try:
                steam_name = self.get_steam_persona(self.data['SteamID'])
                default.s_print(f'RECEIVED: {steam_name} FROM STEAM')
            except Exception as e:
                default.s_print(f'ASYNC ERROR: {e}')
            return self.data['SteamID']
        elif zDOID_connect in message:
            # Death message: Got character ZDOID from Bytes : 0:0
            if message[-1] == "0":
                split = message.split(' ')
                toon = split[4] # Should be ZDOID (in game toon name)
                # Don't want to update database while testing...
                new_death_count = MongoDB_Context.update_death_count()
                default.s_print(f'new death count: {new_death_count}')
                death_event = 'no async error maybe?'
                
                try:
                    MongoDB_Context.update_player_death_count(toon)
                    # object NoneType can't be used in 'await' expression: 
                    #await self.bot.dispatch('on_death', new_death_count, toon) ## Emmit death event: Not working atm? Dunnow why?
                    # 
                    await self.manual_on_death_event(toon, new_death_count)
                except Exception as e:
                    default.s_print(f'ASYNC ERROR: {e}')
                return f'{toon} death!'
            else: 
                full_message = message.replace(zDOID_connect,'')
                full_message = full_message.split(' ')
                self.data['ZDOID'] = full_message[0]
                self.data['ZDOID_login_time'] = date
                return self.data['ZDOID']
        elif current_connections in message: 
            default.s_print(f'current connections: {message}')
            connections = message.split(' ')
            # log message should look like: 'Connections 1 ZDOS:130588  sent:0 recv:422'
            return connections[1]
        elif disconnect in message:
            default.s_print(f'Disconnect message received!: {message}')
            disconnection = message.replace(disconnect,'') # Should be steamID of player who disconnected
            MongoDB_Context.player_disconnect(disconnection)
            return disconnection

    def compare_login_time(self, steam_login_time, zdoid_login_time):
        # TODO: Convert strings to datetime objects here: 
        # Reasoning: It's easier to deal with strings, only need actual datetime objects for this calculation:
        default.s_print(f'*****Comparing: {steam_login_time} to {zdoid_login_time}')
        steam_dto = ''
        zdoid_dto = ''
        try:
            steam_dto = datetime.strptime(steam_login_time, "%m/%d/%Y %H:%M:%S")
        except Exception as e:
            default.s_print(f'could not parse steam login time:{steam_login_time}\nERROR: {e}')
            return False
        try:
            zdoid_dto = datetime.strptime(zdoid_login_time, "%m/%d/%Y %H:%M:%S")
        except Exception as e:
            default.s_print(f'could not parse zdoid login time:{zdoid_login_time}\nERROR: {e}')
            return False
        if isinstance(steam_dto, str) or isinstance(zdoid_dto, str):
            default.s_print(f'Someone was a string? ')
            return False
        else:
            time_diff = steam_dto - zdoid_dto
            time_diff = abs(time_diff.total_seconds()) # steam login comes first, value SHOULD be negative.
            if time_diff < (60 * 2): # 5 minute timeout
                self.data['steam_login_time'] = steam_dto
                return True
            else:
                return False

    def get_steam_persona(self, steamID):
        # More import errors I don't feel like debugging anymore: 
        # Instead I"ll just utalize the http class and make requests the old fashioned way
        # SteamWebAPI: https://developer.valvesoftware.com/wiki/Steam_Web_API
        # try:
        #     self.data['SteamName'] = SteamIDToVanityName(steamID)
        #     default.s_print(f"Found Steam Name: {self.data['SteamName']}")
        # except Exception as e:
        #     default.s_print(f'Error getting Steam Name: {e}')
        steam_api = steam.webapi.WebAPI(key=self.config['steam_api_key'])
        default.s_print(f'Getting steam name for {steamID}')
        if steamID is None or " ":
            steamID = self.data['SteamID']
        steam_url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={self.config['steam_api_key']}&steamids={steamID}"
        try:
            # response = await http.get(steam_url)
            response = steam_api.call('ISteamUser.GetPlayerSummaries',steamids=steamID)
            default.s_print(f'RESPONSE OBJECT: {response}')
            #response = json.loads(response)
            first_player = response['response']['players'][0]
            self.data['SteamName'] = first_player['personaname']
        except Exception as e:
            default.s_print(f'Error {e}')
        default.s_print(f'SteamName?: {self.data["SteamName"]}')
        return self.data['SteamName']

    async def manual_on_death_event(self, player_name, death_count):
        """ Announce death of player in valheim Server """
        death_message = [ 
            "was squased by a troll",
            "fell victim to gredwarves",
            "ascended to the 10th dead world",
            "was fondled by greylings",
            "took a deathsquito from behind",
            "was collected by the Valkyrie",
            "failed Odin's test",
            "In Soviet Russia, tree fell you!"
        ]
        rng_death_msg = random.choice(death_message)
        # Knights of Ni Bot Spam Channel ID: 831250902470885406
        default.s_print(f'MANUAL Death event for {player_name} {rng_death_msg}')
        bot_spam = self.bot.get_channel(831250902470885406)
        await bot_spam.send(f'RIP {player_name} {rng_death_msg}\nTotal Vikings lost: {death_count}')

    def clear_data(self):
        """ Clear out self.data store after flushing data to DB """
        self.data = {
            'SteamID':'',
            'SteamName':'',
            'ZDOID':'',
            'steam_login_time':'',
            'ZDOID_login_time':'',
            'online':False,
        }
        default.s_print(f'data obj: {self.data}')