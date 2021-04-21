import rofi_menu
import asyncio

from rofify.src.utils import playlist_track_label, substitute_pango_escape
from rofi_menu.constants import OP_EXIT, OP_REFRESH_MENU
from rofify.src.SpotifyAPI import spotify
from rofify.src.config import config

class TrackItem(rofi_menu.Item):
    """
    The track item is meant to assist in quick selection of songs
    from playlists and searches. It starts playback of the track 
    when selected  
    """
    nonselectable = False

    def __init__(self, text=None, track=None, offset=None, **kwargs):
        super().__init__(text=text)
        # The spotify api track dictionary
        self.track = track
        # The offset locates the track within the context
        # (e.g. the 5th track in the playlist, the 11th track in the album)
        self.offset = offset

    async def load(self, meta):
        await super().load(meta)
        if self.parent_menu.track_formatter is not None:
            self.text = self.parent_menu.track_formatter(self.track)
        else:
            # In the case where no formatter is provided, just 
            # display the track name
            
            self.text = config.track_item_icon + \
                substitute_pango_escape(self.track['name'])
        self.state = meta.get_state(self.id)

    async def on_select(self, meta):
        # This could be in the context of a playlist, album, etc
        if self.parent_menu.context:
            await spotify.playback.play_content(
                device_id=spotify.device.current_device['id'],
                context_uri=self.parent_menu.context,
                offset={"position":self.offset}
                )
        # Otherwise we just assume that only the selected track should be played
        elif self.track:
            await spotify.playback.play_content(
                device_id=spotify.device.current_device['id'],
                uris=[self.track['uri']],
            )
        return await super().on_select(meta)

class TrackMenu(rofi_menu.Menu):

    allow_user_input=False

    def __init__(self, tracks=[], prompt=None, context=None, track_formatter=None):
        super().__init__(
            prompt = self.prompt 
        )
        # Tracks are a list of dicts as returned by the spotify api 
        self.tracks = tracks
        self.prompt = prompt
        # The context is a uri used to control playback (i.e. is the 
        # song being played from a playlist, album, etc) 
        self.context = context
        # Used to format the track info into columns in the rofi menu
        self.track_formatter = track_formatter

    async def generate_menu_items(self, meta):
        tracks = []
        for offset,track in enumerate(self.tracks):
            tracks.append(TrackItem(
                track=track, 
                offset=offset, 
                text=track['name']
                )   
            )
        return [rofi_menu.BackItem()] + tracks

    @classmethod
    async def from_playlist(cls, playlist):
        """
        Create a track menu from a playlist (as returned by spotipy)
        """
        prompt = "Search in {}".format(playlist['name'])
        playlists = (await spotify.async_playlist_tracks(playlist['id']))['items']
        return cls(
                prompt=prompt, 
                tracks=[playlist_item['track'] for playlist_item in playlists],
                context=playlist['uri'],
                track_formatter=playlist_track_label
            )
