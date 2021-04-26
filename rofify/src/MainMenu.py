import rofi_menu
import asyncio
import os

from rofify.src.Hotkeys import hotkeys
from rofify.src.DynamicNestedMenu import DynamicNestedMenu
from rofify.src.RecentlyPlayedMenu import RecentlyPlayedMenu
from rofify.src.PlaylistMenu import PlaylistMenu
from rofify.src.DeviceMenu import DeviceMenu
from rofify.src.SpotifyAPI import spotify
from rofify.src.config import config
from rofify.src.utils import header_playback_label 

playlist = spotify.all_playlists()[0]

class CustomItem(rofi_menu.Item):
    # TODO Cusom item should provide user info on what they're doing
    async def render(self, meta):
        entered_text = meta.session.get("text", "[ no text ]")
        return f"You entered: {entered_text}"

class MainMenu(rofi_menu.Menu):
    icon = None
    prompt = None
    allow_user_input=False

    async def pre_render(self,meta):
        self.prompt = await header_playback_label(spotify.playback)

    async def on_user_input(self, meta):
        """ 

        """
        await hotkeys.handle_user_input()

        # TODO use the meta to store useful information about the input of commands
        # then the custom item at the top of the menu to display last command entered
        meta.session['text'] = meta.user_input

        return rofi_menu.Operation(rofi_menu.OP_REFRESH_MENU)

    async def generate_menu_items(self,meta):
        # get icons for the labels
        playlists_icon = config.playlist_menu_icon
        devices_icon = config.device_menu_icon
        recently_played_icon = config.recently_played_menu_icon
        return [
            CustomItem(),
            DynamicNestedMenu(f"{playlists_icon} Playlists", sub_menu_type=PlaylistMenu), 
            DynamicNestedMenu(f"{recently_played_icon} Recently Played", sub_menu_type=RecentlyPlayedMenu),
            DynamicNestedMenu(f"{devices_icon} Devices", sub_menu_type=DeviceMenu),
            ]
