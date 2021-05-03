import rofi_menu
import asyncio
import os

from rofify.src.RecentlyPlayedMenu import RecentlyPlayedMenu
from rofify.src.DynamicNestedMenu import DynamicNestedMenu
from rofify.src.SavedTracksMenu import SavedTracksMenu
from rofify.src.PlaylistMenu import PlaylistMenu
from rofify.src.DeviceMenu import DeviceMenu
from rofify.src.SearchMenu import SearchMenu
from rofify.src.SpotifyAPI import spotify
from rofify.src.Hotkeys import hotkeys
from rofify.src.config import config
from rofify.src.utils import header_playback_label

class MainMenu(rofi_menu.Menu):
    icon = None
    prompt = None
    allow_user_input = True

    async def pre_render(self,meta):
        """ Display information regarding the current playback in the prompt
        """
        self.prompt = await header_playback_label(spotify.playback)

    async def on_user_input(self, meta):
        """ 

        """
        await hotkeys.handle_user_input()
        return rofi_menu.Operation(rofi_menu.OP_REFRESH_MENU)

    async def generate_menu_items(self,meta):
        # set meta defaults
        meta.session.setdefault('search', "")

        # get icons for the labels
        playlists_icon = config.playlist_menu_icon
        devices_icon = config.device_menu_icon
        recently_played_icon = config.recently_played_menu_icon
        saved_tracks_icon = config.saved_tracks_menu_icon
        search_tracks_icon = config.search_tracks_menu_icon
        return [
            DynamicNestedMenu(f"{playlists_icon} Playlists", sub_menu_type=PlaylistMenu),
            DynamicNestedMenu(f"{recently_played_icon} Recently Played", sub_menu_type=RecentlyPlayedMenu),
            DynamicNestedMenu(f"{devices_icon} Devices", sub_menu_type=DeviceMenu),
            DynamicNestedMenu(f"{saved_tracks_icon} Saved Tracks", sub_menu_type=SavedTracksMenu),
            DynamicNestedMenu(f"{search_tracks_icon} Search", sub_menu_type=SearchMenu),
            ]
