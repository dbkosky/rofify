import rofi_menu
import asyncio
import sys
import os

from rofify.src.RecentlyPlayedMenu import RecentlyPlayedMenu
from rofify.src.PlaylistMenu import NestedPlaylistTrackMenu, PlaylistMenu
from rofify.src.DeviceMenu import DeviceMenu
from rofify.src.SpotifyAPI import spotify
from rofify.src.config import config

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

    # Map of corresponding actions for custom keybindings
    input_map = {
        '10':spotify.playback.previous,
        '11':spotify.playback.next,
        '12':spotify.playback.play_pause,
    }

    async def pre_render(self,meta):
        # TODO fix formatting on playback label (e.g. for longer songs)
        self.prompt = await spotify.playback.get_playback_label()

    async def on_user_input(self, meta):
        """ 
        Compare the rofi environment variable to find what kind of user input was given
        i.e. was it simply return, or one of the specified hotkeys
        """
        if os.getenv('ROFI_RETV') is not None:

            await self.input_map[os.getenv('ROFI_RETV')]() 
            

        meta.session['text'] = meta.user_input 
        await asyncio.sleep(0.2)

        return rofi_menu.Operation(rofi_menu.OP_REFRESH_MENU)

    async def generate_menu_items(self,meta):
        # get icons for the labels
        playlists_icon = config.playlist_menu_icon
        devices_icon = config.device_menu_icon
        recently_played_menu_icon = config.recently_played_menu_icon

        return [
            CustomItem(), 
            rofi_menu.NestedMenu(text=f"{playlists_icon} Playlists", menu=PlaylistMenu()), 
            rofi_menu.NestedMenu(text=f"{recently_played_menu_icon}  Recently Played", menu=RecentlyPlayedMenu()),
            rofi_menu.NestedMenu(text=f"{devices_icon} Devices", menu=DeviceMenu())]
