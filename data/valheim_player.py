from mongoengine import *

class Player(Document):
    steamID = StringField(max_length=17,required=True,primary_key=True)
    steam_name = StringField(max_length=48)
    valheim_name = StringField(max_length=25)
    death_count = IntField(min_value=0)
    last_login_time = DateTimeField()
    online_state = BooleanField(default=False)

class TotalDeaths(Document):
    # We'll only be keeping one record of all deaths in the server, so only need one key: 472bc69c-e35b-4f5a-b3d7-999def8c4e27
    key = UUIDField(primary_key=True,default_value="472bc69c-e35b-4f5a-b3d7-999def8c4e27")
    death_count = IntField(min_value=0)

class PlayerServerStats(Document):
    key = UUIDField(primary_key=True, default_value="242c7b80-314b-4d38-b92b-839035f62382")
    online_count = IntField(min_value=0)
    offline_count = IntField(min_value=0)
    total = IntField(min_value=0)

