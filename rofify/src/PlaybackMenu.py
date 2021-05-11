import rofi_menu
import asyncio

from rofify.src.SpotifyAPI import spotify
from rofify.src.Hotkeys import Hotkeys
from rofify.src.config import config

class PlayPauseItem(rofi_menu.Item):

    def __init__(self, text=None):
        super().__init__(text=text)

    async def load(self, meta):
         """
         Item text should be play or pause depending on if the
         current track is either paused or playing respectively
         """
         self.text = "Pause" if spotify.playback.playing else "Play"
         await super().load(meta)

    async def on_select(self, meta):
        """ This should pause/play the current item on the active device
        """
        is_playing = spotify.playback._playback['is_playing']
        await spotify.playback.play_pause()
        spotify.playback._playback['is_playing'] = not is_playing

        return await super().on_select(meta)

class NextItem(rofi_menu.Item):

    def __init__(self):
        super().__init__(text="Next")

    async def on_select(self, meta):
        """ This should play the next track
        """
        await spotify.playback.next()
        return await super().on_select(meta)

class PreviousItem(rofi_menu.Item):

    def __init__(self):
        super().__init__(text="Previous")

    async def on_select(self, meta):
        """ This should play the next track
        """
        await spotify.playback.previous()
        return await super().on_select(meta)

class PlaybackMenu(rofi_menu.Menu):
    icon = None
    prompt = None
    allow_user_input = True

    async def on_user_input(self, meta):
        """
        Check ROFI_RETV to see if one of the mapped hotkeys has been pressed
        """
        await hotkeys.handle_user_input()
        return rofi_menu.Operation(rofi_menu.OP_REFRESH_MENU)

    async def generate_menu_items(self, meta):
        if not spotify.playback._playback:
            await spotify.playback.update_playback()

        items = [rofi_menu.BackItem(),
                 PlayPauseItem(),
                 NextItem(),
                 PreviousItem(),
                ]

        return items
