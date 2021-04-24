from steam.webapi import WebAPI
from utils import default

config = default.config()

# SteamWebAPI: https://developer.valvesoftware.com/wiki/Steam_Web_API 

class SteamIntegration():
    def __init__(self):
        self.api = WebAPI(key=config['steam_api_key'])

    async def SteamIDToVanityName(self, steamID):
        response = await self.api.ISteamUser.GetPlayerSummaries(steamids=steamID)
        #print(response)
        #Example Response: 
        #{'response': {'players': [{'steamid': '76561198015390537', 'communityvisibilitystate': 3, 'profilestate': 1, 'personaname': 'AnxietyBytes', 'profileurl': 'https://steamcommunity.com/id/AnxietyBytes/', 'avatar': 'https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/ae/ae514e872d5abd2ae0980345bb44dae634f92338.jpg', 'avatarmedium': 'https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/ae/ae514e872d5abd2ae0980345bb44dae634f92338_medium.jpg', 'avatarfull': 'https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/ae/ae514e872d5abd2ae0980345bb44dae634f92338_full.jpg', 'avatarhash': 'ae514e872d5abd2ae0980345bb44dae634f92338', 'lastlogoff': 1618186955, 'personastate': 0, 'realname': 'N/A', 'primaryclanid': '103582791429521408', 'timecreated': 1257719203, 'personastateflags': 0, 'loccountrycode': 'US', 'locstatecode': 'TX'}]}}
        # Path to friendly name for first profile found: 
        return response['response']['players'][0]['personaname']