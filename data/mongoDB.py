import logging
from data.valheim_player import Player, TotalDeaths, PlayerServerStats

from mongoengine import connect, disconnect, DoesNotExist
from utils import default


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

    def create_player(self):
        pass

    def update_player(self):
        pass

    def update_online_count(self):
        pass

    def update_death_count(new_count):
        # Key: 472bc69c-e35b-4f5a-b3d7-999def8c4e27
        try:
            death_object = TotalDeaths.objects.get(key='472bc69c-e35b-4f5a-b3d7-999def8c4e27')
            death_object.death_count += new_count
            death_object.save()
            return death_object.death_count
        except DoesNotExist as e:
            death_object = TotalDeaths(death_count=1,key='472bc69c-e35b-4f5a-b3d7-999def8c4e27')
            death_object.save()
            return death_object.death_count

    def update_total_player_count(self):
        pass
