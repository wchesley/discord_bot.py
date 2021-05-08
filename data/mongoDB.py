import logging

from data.valheim_player import Player, TotalDeaths, PlayerServerStats
from mongoengine import connect, disconnect, DoesNotExist
from utils import default
from datetime import datetime

class MongoDB_Context():
    def __init__(self):
        self.config = default.config()
        self._connection = self.connect()

    @property
    def connection(self):
        return self._connection

    def connect(self):
        connection=None
        try:
            connection = connect(
                self.config['db_name'],
                username=self.config['db_user'],
                password=self.config['db_key'],
                authentication_source=self.config['db_name'],
                host=self.config['db_url'],
                port=self.config['db_port']
            ) 
        except Exception as e:
            print(f"error occurred connecting to MongoDB {e}")
            return 0
        print(f'successful connection: {connection}')
        return connection
    
    def disconnect(self):
        print(f'disconnecting from: {self._connection}')
        return disconnect()

    def update_player(player_obj):
        """ 
        Update or create player in Valheim database. \n
        Attempts to find player by SteamID, if not found creates a new entry in the database \n
        Increments Total Player count by 1
        """
        default.s_print(f'Received player_obj:')
        for item in player_obj.items():
            default.s_print(item)
        try:
            player = Player.objects.get(steamID=player_obj['SteamID'])
            
            if player_obj['SteamName'] != player.steam_name:
                default.s_print(f'Updating steamName: {player_obj["SteamName"]}')
                player.steam_name = player_obj['SteamName']
            else:
                default.s_print(f'Values matched: {player_obj["SteamName"]} == {player.steam_name}')

            if player_obj['ZDOID'] != player.valheim_name:
                default.s_print(f'Updating steamName: {player_obj["ZDOID"]}')
                player.steam_name = player_obj['SteamName']
            else:
                default.s_print(f'Values matched: {player_obj["ZDOID"]} == {player.valheim_name}')
            
            try:
                player.last_login_time = player_obj['steam_logim_time']
            except Exception as e:
                default.s_print(f'Could not save date to DB, setting default time: \nDATETIME ERROR: {e}')
                player.last_login_time = datetime.now()

            player.online_state = True
            MongoDB_Context.update_online_count(1)
            player.save()
        except DoesNotExist:
            player = Player(
                steamID = player_obj['SteamID'],
                steam_name = player_obj['SteamName'],
                valheim_name = player_obj['ZDOID'],
                death_count = 0,
                last_login_time = player_obj['steam_login_time'],
                online_state = True
            )
            player.save()
            default.s_print(f'Created new player: \n{player.steamID} / {player.steam_name} / {player.valheim_name}')
            MongoDB_Context.update_online_count(1)
            MongoDB_Context.update_total_player_count()


    def update_online_count(count):
        """ updates online count of players, count can be positive or negative, depending if a player is coming or going. """ 
        try: 
            player_server_stats = PlayerServerStats.objects.get(key="242c7b80-314b-4d38-b92b-839035f62382")
            player_server_stats.online_count += count
            player_server_stats.save()
            default.s_print(f'Updated PlayerServerStats: {player_server_stats.online_count}')
        except DoesNotExist:
            player_server_stats = PlayerServerStats(
                key="242c7b80-314b-4d38-b92b-839035f62382",
                online_count = 1,
                offline_count = 0,
                total = 1
            )
            player_server_stats.save()
            default.s_print(f'Created playerServerStats Document')

    def update_death_count():
        # Key: 472bc69c-e35b-4f5a-b3d7-999def8c4e27
        try:
            death_object = TotalDeaths.objects.get(key='472bc69c-e35b-4f5a-b3d7-999def8c4e27')
            death_object.death_count += 1
            death_object.save()
            return death_object.death_count
        except DoesNotExist as e:
            death_object = TotalDeaths(
                key='472bc69c-e35b-4f5a-b3d7-999def8c4e27',
                death_count=1,
                )
            death_object.save()
            return death_object.death_count

    def update_total_player_count():
        player_count = len(Player.objects)
        try:
            player_server_stats = PlayerServerStats.objects.get(key="242c7b80-314b-4d38-b92b-839035f62382")
            player_server_stats.total = player_count
            player_server_stats.save()
            default.s_print(f'updated total player count: {player_count}')
        except DoesNotExist:
            player_server_stats = PlayerServerStats(
                key="242c7b80-314b-4d38-b92b-839035f62382",
                online_count = 1,
                offline_count = 0,
                total = player_count
            )
            player_server_stats.save()
            default.s_print(f'Created playerServerStats Document')

    def player_disconnect(SteamID):
        try:
            player = Player.objects.get(steamID=SteamID)
            player.online_state = False
            MongoDB_Context.update_online_count(-1)
        except DoesNotExist:
            default.s_print(f'Cannot disconnect player not in database!\n{SteamID} Was not found in Database!')
    
    def update_player_death_count(zdoid):
        try:
            player = Player.objects.get(valheim_name=zdoid)
            player.death_count += 1
            player.save()
            default.s_print(f'updated player death count: {player.death_count}')
        except Exception as e:
            default.s_print(f'Something happened? {e}')

    def get_player_by_zdoid(zdoid):
        """ Find player by their valheim name, return their player object""" 
        try: 
            player = Player.objects.get(valheim_name=zdoid)
            return player
        except Exception as e:
            default.s_print(f'Error getting player:\nget_player_death_count threw: \n\t{e}')
            return 1
    
    def get_player_by_steam_id(steamID):
        try: 
            player = Player.objects.get(steamID=steamID)
            return player
        except Exception as e:
            default.s_print(f'Error getting player:\nget_player_by_steam_id threw:\n\t {e}')
            return 1

    def get_player_by_any_means(searchQuery):
        steamIDorZdoid = searchQuery.isnumeric()
        player = 1 # assume error by default? 
        if steamIDorZdoid:
            player = MongoDB_Context.get_player_by_steam_id(searchQuery)
            return player
        elif player == 1 and steamIDorZdoid == False:
            player = MongoDB_Context.get_player_by_zdoid(searchQuery)
            return player
        elif player == 1:
            return player # should only be here if we didn't find anything at all!

    def icontains_get_player_by_zdoid(zdoid):
        """ Search for player by valheim name using mongonengine icontains. Returns all 
        possible matches for the quersy in a case INsensitive manor""" 
        try:
            player = Player.objects.get(zdoid__icontains=zdoid)
            return player
        except Exception as e:
            default.s_print(f'Error finding player via icontains: {e}')
            return 1
