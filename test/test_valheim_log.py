import unittest
from valheim_server.log_dog import ValheimLogDog

class TestValheimLog(unittest.TestCase):
    def setUp(self):
        self.test_log_message_Steam = 'Got connection SteamID 76561197999876368'
        self.test_log_date_Steam = "04/12/2021 19:35:20"
        self.test_log_message_zDOID = 'Got character ZDOID from Halfdan : 3267341458:1'
        self.test_log_date_zDOID = "04/12/2021 19:35:55"
        self.test_log_message_char_death = 'Got character ZDOID from Halfdan : 0:0'
        self.test_log_connection_message = 'Connections 1 ZDOS:130588  sent:0 recv:422'
        self.test_log_disconnect_message = 'Closing Socket 76561197999876368'
        self.test_dog = ValheimLogDog.data = {
            'SteamID':'',
            'ZDOID':'',
            'steam_login_time':'',
            'ZDOID_login_time':'',
            'online':False,
        } 

    def test_SteamIDFromValheimLogMessage(self):
        steamID = ValheimLogDog.extract_log_parts(ValheimLogDog, self.test_log_message_Steam, self.test_log_date_Steam)
        print(f'steamID: {steamID}')
        self.assertEqual(steamID, '76561197999876368')

    def test_zDOIDFromValheimLogMessage(self):
        zDOID = ValheimLogDog.extract_log_parts(ValheimLogDog, self.test_log_message_zDOID, self.test_log_date_zDOID)
        print(f'ZDOID: {zDOID}')
        self.assertEqual(zDOID, 'Halfdan')

    def test_CharacterDeathFromValheimLogMessage(self):
        zDOID = ValheimLogDog.extract_log_parts(ValheimLogDog, self.test_log_message_char_death, self.test_log_date_zDOID)
        print(f'ZDOID: {zDOID}')
        self.assertEqual(zDOID, 'Halfdan death!')

    def test_ConnectionMessage(self):
        active_connectoins = ValheimLogDog.extract_log_parts(ValheimLogDog, self.test_log_connection_message, self.test_log_date_Steam)
        print(f'active: {active_connectoins}, test_msg: {self.test_log_connection_message}')
        self.assertEqual(active_connectoins, '1')

    def test_DisconnectMessage(self):
        disconnection = ValheimLogDog.extract_log_parts(ValheimLogDog, self.test_log_disconnect_message, self.test_log_date_Steam)
        self.assertEqual(disconnection, '76561197999876368')

if __name__ == '__main__':
    unittest.main()