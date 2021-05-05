import unittest
import datetime
from data.mongoDB import MongoDB_Context
from data.valheim_player import Player, TotalDeaths, PlayerServerStats
from mongoengine import * 

class testMongoDBIntegration(unittest.TestCase):
    def setUp(self):
        connect('bytebot_test_db', host=f"mongomock://localhost")
        self.player_obj = {
            'SteamID':'1234567891011',
            'SteamName':'AnxietyBytes',
            'ZDOID':'Bytes',
            'steam_login_time':'04/20/1969',
            'ZDOID_login_time':'04/20/1969',
            'online':False,
        }
        self.player = Player(
            steamID='1234567891011',
            steam_name='TestAccount',
            valheim_name = 'Bytes',
            death_count=0,
            last_login_time=datetime.datetime.now(),
            online_state=False
        )
        self.player.save()

    def test_update_player_with_existing_player(self):
        MongoDB_Context.update_player(self.player_obj)
        player = Player.objects.get(steamID='1234567891011')
        self.assertEqual(player.steamID, '1234567891011')
        self.assertEqual(player.steam_name,'AnxietyBytes')

    def test_update_player_with_new_player(self):
        # Clone of self.data in ValheimLogDog
        test_player = {
            'SteamID':'0987654321',
            'SteamName':'Bytes',
            'ZDOID':'Bytes',
            'steam_login_time':datetime.datetime.now(),
            'ZDOID_login_time':'',
            'online':False,
        }
        MongoDB_Context.update_player(test_player)
        player = Player.objects.get(steamID='0987654321')
        self.assertEqual(player.steam_name, 'Bytes')
        self.assertTrue(player.online_state)

    def test_player_disconnect(self):
        MongoDB_Context.player_disconnect('1234567891011')
        player = Player.objects.get(steamID='1234567891011')
        self.assertFalse(player.online_state)

    def test_update_online_count(self):
        MongoDB_Context.update_online_count(1)
        online_count = PlayerServerStats.objects.get(key="242c7b80-314b-4d38-b92b-839035f62382")
        self.assertEqual(online_count.online_count, 1)
        self.assertEqual(online_count.offline_count, 0)
        self.assertEqual(online_count.total, 1)

    def test_update_player_death_count(self):
        MongoDB_Context.update_player_death_count('Bytes')
        player = Player.objects.get(steamID="1234567891011")
        self.assertEqual(player.death_count, 1)

    def test_update_total_player_count(self):
        MongoDB_Context.update_total_player_count()
        player_count = PlayerServerStats.objects.get(key="242c7b80-314b-4d38-b92b-839035f62382")
        self.assertEqual(player_count.online_count, 3)
        self.assertEqual(player_count.total, 2) 

    def test_update_death_count(self):
        MongoDB_Context.update_death_count()
        death_doc = TotalDeaths.objects.get(key="472bc69c-e35b-4f5a-b3d7-999def8c4e27")
        self.assertEqual(death_doc.death_count, 1)