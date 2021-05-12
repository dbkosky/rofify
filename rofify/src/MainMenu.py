import rofi_menu
import asyncio
import os

from rofify.src.SearchMenu import SearchTrackMenu, SearchAlbumMenu, SearchArtistMenu, SearchPlaylistMenu
from rofify.src.RecentlyPlayedMenu import RecentlyPlayedMenu
from rofify.src.DynamicNestedMenu import DynamicNestedMenu
from rofify.src.SavedTracksMenu import SavedTracksMenu
from rofify.src.PlaylistMenu import PlaylistMenu
from rofify.src.PlaybackMenu import PlaybackMenu
from rofify.src.DeviceMenu import DeviceMenu
from rofify.src.SpotifyAPI import spotify
from rofify.src.Hotkeys import hotkeys
from rofify.src.config import config

class MainMenu(rofi_menu.Menu):
    icon = None
    prompt = None
    allow_user_input = True

    async def pre_render(self,meta):
        """ Display information regarding the current playback in the prompt
        """
        self.prompt = await config.header_playback_label(spotify.playback)

    async def on_user_input(self, meta):
        """ 

        """
        await hotkeys.handle_user_input()
        return rofi_menu.Operation(rofi_menu.OP_REFRESH_MENU)

    async def generate_menu_items(self,meta):
        # set meta defaults
        meta.session.setdefault('search', "")

        if not spotify.playback.meta:
            spotify.playback.meta = meta
            meta.session.setdefault('is_playing', False)
            meta.session.setdefault('shuffle_state', 'off')
            meta.session.setdefault('repeat_state', 'off')

        # get icons for the labels
        playlists_icon = config.get_icon('playlist-menu-icon')
        devices_icon = config.get_icon('device-menu-icon')
        recently_played_icon = config.get_icon('recently-played-menu-icon')
        saved_tracks_icon = config.get_icon('saved-tracks-menu-icon')
        search_tracks_icon = config.get_icon('search-tracks-menu-icon')
        playback_menu_icon = config.get_icon('playback-menu-icon')
        return [
            DynamicNestedMenu(f"{playback_menu_icon} Playback Menu", sub_menu_type=PlaybackMenu),
            DynamicNestedMenu(f"{playlists_icon} Playlists", sub_menu_type=PlaylistMenu),
            DynamicNestedMenu(f"{recently_played_icon} Recently Played", sub_menu_type=RecentlyPlayedMenu),
            DynamicNestedMenu(f"{devices_icon} Devices", sub_menu_type=DeviceMenu),
            DynamicNestedMenu(f"{saved_tracks_icon} Saved Tracks", sub_menu_type=SavedTracksMenu),
            DynamicNestedMenu(f"{search_tracks_icon} Search Tracks", sub_menu_type=SearchTrackMenu),
            DynamicNestedMenu(f"{search_tracks_icon} Search Albums", sub_menu_type=SearchAlbumMenu),
            DynamicNestedMenu(f"{search_tracks_icon} Search Artists", sub_menu_type=SearchArtistMenu),
            DynamicNestedMenu(f"{search_tracks_icon} Search Playlists", sub_menu_type=SearchPlaylistMenu),
        ]
