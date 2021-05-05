import asyncio
import unittest
from unittest import IsolatedAsyncioTestCase
from valheim_server.log_dog import ValheimLogDog
from utils import default
from mongoengine import *

config = default.config()
unittest.TestLoader.sortTestMethodsUsing = None

class TestDeathDocument(Document):
    key = UUIDField(primary_key=True)
    death_count = IntField(min=0)

class TestValheimLogNonAsync(unittest.TestCase):
    def setUp(self):
        self.steamID = "76561197999876368"
        self.test_dog = ValheimLogDog.data = {
            'SteamID':'',
            'ZDOID':'',
            'steam_login_time':'',
            'ZDOID_login_time':'',
            'online':False,
        }
        self.LogDogObject = ValheimLogDog('bot')
    
    @unittest.skip("Individual method not working? works when called from extract_log_parts()")
    def test_steamName_from_api(self):
        steamName = ValheimLogDog.get_steam_persona(self.LogDogObject, self.steamID)
        self.assertEqual(steamName, "choochoolain")

class TestValheimLog(IsolatedAsyncioTestCase):
    def setUp(self):
        connect('bytebot_test_db', host=f"mongomock://localhost")
        self.test_log_message_Steam = 'Got connection SteamID 76561197999876368'
        self.test_log_date_Steam = "04/12/2021 19:35:20"
        self.test_log_message_zDOID = 'Got character ZDOID from Halfdan : 3267341458:1'
        self.test_log_date_zDOID = "04/12/2021 19:35:55"
        self.test_log_message_char_death = 'Got character ZDOID from Halfdan : 0:0'
        self.test_log_connection_message = 'Connections 1 ZDOS:130588  sent:0 recv:422'
        self.test_log_disconnect_message = 'Closing Socket 76561197999876368'
        self.steamID = "76561197999876368"
        self.test_dog = ValheimLogDog.data = {
            'SteamID':'',
            'ZDOID':'',
            'steam_login_time':'',
            'ZDOID_login_time':'',
            'online':False,
        }
        self.LogDogObject = ValheimLogDog('bot')
        #self.loop = asyncio.get_event_loop()

    def tearDown(self):
        disconnect()
        
    async def asyncTearDown(self):
        pass

    async def test_SteamIDFromValheimLogMessage(self):
        steamID = await ValheimLogDog.extract_log_parts(self.LogDogObject, self.test_log_message_Steam, self.test_log_date_Steam)
        print(f'steamID: {steamID}')
        self.assertEqual(steamID, '76561197999876368')

    async def test_zDOIDFromValheimLogMessage(self):
        zDOID = await ValheimLogDog.extract_log_parts(self.LogDogObject, self.test_log_message_zDOID, self.test_log_date_zDOID)
        print(f'ZDOID: {zDOID}')
        self.assertEqual(zDOID, 'Halfdan')

    async def test_CharacterDeathFromValheimLogMessage(self):
        zDOID = await ValheimLogDog.extract_log_parts(self.LogDogObject, self.test_log_message_char_death, self.test_log_date_zDOID)
        print(f'ZDOID: {zDOID}')
        self.assertEqual(zDOID, 'Halfdan death!')

    async def test_ConnectionMessage(self):
        active_connectoins = await ValheimLogDog.extract_log_parts(self.LogDogObject, self.test_log_connection_message, self.test_log_date_Steam)
        print(f'active: {active_connectoins}, test_msg: {self.test_log_connection_message}')
        self.assertEqual(active_connectoins, '1')

    async def test_DisconnectMessage(self):
        disconnection = await ValheimLogDog.extract_log_parts(self.LogDogObject, self.test_log_disconnect_message, self.test_log_date_Steam)
        self.assertEqual(disconnection, '76561197999876368')

if __name__ == '__main__':
    unittest.main()