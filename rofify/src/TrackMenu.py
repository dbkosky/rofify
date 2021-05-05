import rofi_menu
import asyncio

from rofify.src.utils import playlist_track_label, substitute_pango_escape
from rofi_menu.constants import OP_EXIT, OP_REFRESH_MENU, OP_OUTPUT
from rofify.src.DynamicNestedMenu import DynamicNestedMenu
from rofify.src.DeviceMenu import DeviceMenu
from rofify.src.SpotifyAPI import spotify
from rofify.src.config import config

class TrackItem(rofi_menu.Item):
    """
    The track item is meant to assist in quick selection of songs
    from playlists and searches. It starts playback of the track 
    when selected .
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
            self.text = config.get_icon('track-item-icon') + \
                substitute_pango_escape(self.track['name'])
        self.state = meta.get_state(self.id)

    async def on_select(self, meta):
        """
        This should preferably play the selected track in context
        if a context can be found, if not, it should play the track 
        without context. If a device cannot be found, it should display
        a choice of devices.
        """
        if spotify.device.current_device:
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
        else:
            # Make sure there is no active device
            device = spotify.device.get_active_device()
            
            if device is not None:
                spotify.device.current_device = device
                return await self.on_select(meta)
            else:
                return rofi_menu.Operation(OP_REFRESH_MENU)

    async def build(self, parent_menu, item_id, meta):
        """
        Build a menu item.
        It also links item to concreate menu, assigns an id and returns "bound" element.
        If the 'popup_device_menu' flag is set in meta, , build the device menu.
        """
        if meta.session.get('popup_device_menu'):
            obj = await DynamicNestedMenu(
                text=parent_menu.track_formatter(self.track),
                sub_menu_type=DeviceMenu,
                prompt='Select a device',
            ).build(
                parent_menu=parent_menu,
                item_id=item_id,
                meta=meta,
            )
            return obj
        else:
            obj = self.clone()
            obj.id = obj.id or (
                item_id if isinstance(item_id, list) else [*parent_menu.id, item_id]
            )
            obj.parent_menu = parent_menu
            return obj


class TrackMenu(rofi_menu.Menu):

    allow_user_input=False

    def __init__(self, tracks=[], prompt=None, context=None, track_formatter=None):
        super().__init__()
        # Tracks are a list of dicts as returned by the spotify api 
        self.tracks = tracks
        self.prompt = prompt
        # The context is a uri used to control playback (i.e. is the 
        # song being played from a playlist, album, etc) 
        self.context = context
        # Used to format the track info into columns in the rofi menu
        self.track_formatter = track_formatter

    async def update_popup_meta(self, meta):
        """
        Updates the meta with a boolean value representing whether a popup device
        menu should occur when the track is selected.
        """

        # Set the element to bring up device menu if there is no set device
        meta.session.setdefault('popup_device_menu', False)
        if not spotify.device.current_device:
            meta.session['popup_device_menu'] = True
        else:
            meta.session['popup_device_menu'] = False


    async def generate_menu_items(self, meta):

        await self.update_popup_meta(meta)

        tracks = []
        for offset,track in enumerate(self.tracks):    
            tracks.append(TrackItem(
                track=track, 
                offset=track['offset'] if track.get('offset') is not None else offset, 
                text=track['name']
                )
            )
        return [rofi_menu.BackItem()] + tracks

    @classmethod
    async def from_playlist(cls, playlist):
        """
        Create a track menu from a playlist (as returned by spotipy).
        """
        prompt = "Search in {}".format(playlist['name'])
        playlist_tracks = (await spotify.async_playlist_tracks(playlist['id']))['items']
        return cls(
                prompt=prompt,
                tracks=[playlist_item['track'] for playlist_item in playlist_tracks],
                context=playlist['uri'],
                track_formatter=playlist_track_label,
            )

    @classmethod
    async def from_album(cls, album):
        """
        Create a track menu from an album (as returned by spotipy)
        """
        album_tracks = (await spotify.async_album_tracks(album['id']))['items']
        [track.update({'album':album}) for track in album_tracks]
        return cls(
            tracks=[track for track in album_tracks],
            context=album['uri'],
            track_formatter=playlist_track_label,
        )
