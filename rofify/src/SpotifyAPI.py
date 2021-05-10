import os
import spotipy
import pathlib
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth

from rofify.src.config import config
from rofify.src.PlaybackControls import Playback
from rofify.src.DeviceControls import Device

import sys
import asyncio

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
    # TODO add appropriate exception handling

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

    cache_dir = pathlib.Path(os.path.dirname(config.cache_path))
    if not cache_dir.exists():
        cache_dir.mkdir(parents=True)

    # Token used in credential flow
    token = util.prompt_for_user_token(
        username=config.username,
        scope=' '.join(scope),
        client_id=config.client_id,
        client_secret=config.client_secret,
        redirect_uri=config.redirect_uri,
        cache_path=config.cache_path,
    )

    if token:
        client = spotipy.Spotify(auth=token)
    else:
        sys.stderr.write(f"Can't get token for {config.username}")
    
    def __init__(self):
        self.device = Device(parent=self)
        self.playback = Playback(parent=self)

    # TODO settle on using normal or async consistently
    def all_playlists(self):
        return self.client.current_user_playlists()['items']

    def playlist_tracks(self, playlist_id):
        return self.client.playlist_tracks(playlist_id)

    async def async_all_playlists(self):
        return self.client.current_user_playlists()['items']

    async def async_playlist_tracks(self, playlist_id):
        """
        Aqcuire all playlist tracks for a given playlist 
        """

        # The API at present only allows the retrieval of 
        # 100 playlist tracks at a time
        # The spotipy next() function can be used to retrieve
        # all of the entries

        track_page = self.client.playlist_tracks(playlist_id)
        playlist_tracks = track_page
        while track_page['next']:
            track_page = self.client.next(track_page)
            playlist_tracks['items'] += track_page['items']

        return playlist_tracks

    async def async_all_saved_tracks(self):
        """
        Aqcuire all saved tracks 
        """

        # The API at present only allows the retrieval of 
        # 50 tracks at a time
        # The spotipy next() function can be used to retrieve
        # all of the entries

        track_page = self.client.current_user_saved_tracks()
        saved_tracks = track_page
        while track_page['next']:
            track_page = self.client.next(track_page)
            saved_tracks['items'] += track_page['items']

        return saved_tracks

    async def async_album_tracks(self, album_id):
        # TODO check to see if albums load fully,
        # if not then this needs to be paged like the tracks
        # from playlist method
        return self.client.album_tracks(album_id)

    async def async_search(self, search, limit=50, type='track', pages=4):
        """
        Construct a query and return the results
        """

        query = "+".join(search.split())
        search_content = self.client.search(query, limit=limit, type=type)[type+'s']
        pages_left = pages - 1
        while pages_left and search_content['next']:
            next_page = self.client.next(search_content)[type+'s']
            search_content.update({
                'next':next_page['next'],
            })
            search_content['items'] += next_page['items']
            pages_left -= 1

        return search_content

    async def artist_albums(self, artist_id):
        # TODO see it this needs to collected by pages
        return self.client.artist_albums(artist_id)

    async def playback_state(self):
        return self.client.current_playback()

    async def get_recently_played(self):
        tracks = self.client.current_user_recently_played()
        items = tracks['items']
        # set used to identify unique tracks, prevent duplication of results
        track_uris = set()
        tracks = []
        # iterate through the items and add the unique tracks to the list
        for index,item in enumerate(items):
            if item['track']['uri'] not in track_uris \
                and (track_uris.add(item['track']['uri']) or True):

                item['track'].update({'offset':index})
                tracks.append(item['track'])

        return tracks

spotify = SpotifyAPI()
