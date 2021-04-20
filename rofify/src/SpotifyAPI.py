import os
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth

from rofify.src.config import config, cache_location
from rofify.src.PlaybackControls import Playback
from rofify.src.DeviceControls import Device

import sys
import asyncio
lock = asyncio.Lock()


# TODO CONFIG maximum limit for retrieving songs


class SpotifyAPI:
    """
    Some of the data structures retrieved from the spotify api (provided 
    by spotipy) can be complex to parse. 

    This class contains methods used to relate data in a more relevant fashion,
    and handles initialising the api client        
    """

    # TODO reduce the scope to only the required permissions 
    # for operation

    scope = [
    # Playback reading permissions
    "user-read-playback-state",
    "user-read-playback-position",
    "user-read-currently-playing",
    
    # Permissions for track selection
    "user-read-recently-played",
    "user-library-read",
    # Optionals for playlist track selection
    "playlist-read-collaborative",
    "playlist-read-private",

    # Playback modification permissions
    "user-modify-playback-state",
    
    # Playlist/ Library modification permssions
    "user-library-modify",
    "playlist-modify-public",
    "playlist-modify-private",
    ]

    # Token used in credential flow
    token = util.prompt_for_user_token(
        config['credentials']['username'],
        ' '.join(scope),
        client_id=config['credentials']['client_id'],
        client_secret=config['credentials']['client_secret'],
        redirect_uri=config['credentials']['redirect_uri'],
        cache_path=cache_location,
    )

    if token:
        client = spotipy.Spotify(auth=token)
    else:
        sys.stderr.write("Can't get token for", config['credentials']['username'])

    
    def __init__(self):
        self.device = Device(client=self.client)
        self.playback = Playback(client=self.client)

    # TODO settle on using normal or async consistently
    def all_playlists(self):
        return self.client.current_user_playlists()['items']

    def playlist_tracks(self, playlist_id):
        return self.client.playlist_tracks(playlist_id)

    async def async_all_playlists(self):
        return self.client.current_user_playlists()['items']

    async def async_playlist_tracks(self, playlist_id, offset=0, items=[]):
        """
        Aqcuire all playlist tracks for a given playlist 
        """

        # The API at present only allows the retrieval of 
        # 100 playlist tracks at a time
        limit = 100
        # obtain the playlist piecemeal, construct it, 
        # return it as a singluar dictionary

        playlist_tracks = self.client.playlist_tracks(playlist_id)
        if playlist_tracks['total'] > limit:
            items = playlist_tracks['items']
            for offset in range(limit, playlist_tracks['total'], limit):
                items += self.client.playlist_tracks(playlist_id, offset=offset)['items']
            
            playlist_tracks.update({'items':items})

        return playlist_tracks    
        
    async def playback_state(self):
        return self.client.current_playback()


spotify = SpotifyAPI()
