from mongoengine import *

class Player(Document):
    steamID = StringField(max_length=17,required=True,primary_key=True)
    steam_name = StringField(max_length=48)
    valheim_player_id = StringField(max_length=25)
    valheim_name = StringField(max_length=25)
    death_count = IntField(min_value=0)
    def __init__(self, steamID, steam_name, valheim_player_id, valheim_name, death_count):
        self.steamID = steamID
        self.steam_name = steam_name
        self.valheim_player_id = valheim_player_id
        self.valheim_name = valheim_name
        self.death_count = death_count

class TotalDeaths(Document):
    # We'll only be keeping one record of all deaths in the server, so only need one key: 472bc69c-e35b-4f5a-b3d7-999def8c4e27
    key = UUIDField(primary_key=True,default_value="472bc69c-e35b-4f5a-b3d7-999def8c4e27")
    death_count = IntField(min_value=0)
    # def __init__(self, death_count):
    #     self.death_count = death_count

class PlayerServerStats(Document):
    online_count = IntField(min_value=0)
    offline_count = IntField(min_value=0)
    total = IntField(min_value=0)

