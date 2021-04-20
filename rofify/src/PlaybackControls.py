import asyncio

class Playback:
    """
    Subdivision of the SpotifyAPI class. Delegates functions relating to controlling
    the current user's playback and getting information regarding the user's playback
    """

    def __init__(self, client=None):
        # Playback as dictionary provided by the spotify api
        self._playback = None
        self._client = client


    async def update_playback(self):
        # The playback is updated this way in order to control
        # the number of calls made to the api
        self._playback = self._client.current_playback()

    @property
    def song_name(self):
        return self._playback['item']['name']

    @property
    def artist_names(self):
        return ', '.join([artist['name'] for artist in self._playback['item']['artists']])

    async def play_content(self, device_id, context_uri=None, uris=None, offset=None):
        self._client.start_playback(device_id, context_uri=context_uri, uris=uris, offset=offset)

    async def get_playback_label(self):
        """
        Get playback for the label displaying the currently playing song at the top 
        of the rofi menu
        """
        await self.update_playback()
        if self._playback is not None:
            if self._playback['is_playing']:
                return "Playing: {} - {}".format(self.song_name, self.artist_names)
            else:
                return "Paused: {} - {}".format(self.song_name, self.artist_names)
        else:
            return "Nothing is playing"

    async def play_pause(self):
        await self.update_playback()
        if self._playback is not None:
            if self._playback['is_playing']:
                self._client.pause_playback()
            else:
                self._client.start_playback()

    async def previous(self):
        await self.update_playback()
        if self._playback is not None:
            self._client.previous_track()

    async def next(self):
        await self.update_playback()
        if self._playback is not None:
            self._client.next_track()

 