import rofi_menu
import asyncio

from rofify.src.SpotifyAPI import spotify
from rofify.src.Hotkeys import Hotkeys
from rofify.src.config import config

import sys

class PlayPauseItem(rofi_menu.Item):

    def __init__(self, text=None):
        super().__init__(text=text)

    async def load(self, meta):
         """
         Item text should be play or pause depending on if the
         current track is either paused or playing respectively
         """
         self.text = "<b><u>Playing</u></b> Paused" if \
             spotify.playback.meta.session['is_playing'] \
             else "Playing <b><u>Paused</u></b>"
         await super().load(meta)

    async def on_select(self, meta):
        """ This should pause/play the current item on the active device
        """
        await spotify.playback.play_pause()
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

class ShuffleItem(rofi_menu.Item):

    text_on = "Shuffle: <b><u>on</u></b> off"
    text_off = "Shuffle: on <b><u>off</u></b>"
    async def on_select(self, meta):
        """ Toggle the shuffle setting
        """
        await spotify.playback.toggle_shuffle()
        return await super().on_select(meta)

    async def load(self, meta):
        self.text = self.text_on if \
            spotify.playback.meta.session['shuffle_state'] else self.text_off
        await super().load(meta)

class RepeatItem(rofi_menu.Item):

    repeat_text = {
        'off':"Repeat: <b><u>off</u></b> context track",
        'context':"Repeat: off <b><u>context</u></b> track",
        'track':"Repeat: off context <b><u>track</u></b>",
    }

    async def on_select(self, meta):
        """ Cycle between the different types of repeat
        """
        await spotify.playback.cycle_repeat()
        return await super().on_select(meta)

    async def load(self, meta):
        self.text = self.repeat_text[spotify.playback.meta.session['repeat_state']]
        await super().load(meta)

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

        items = [
            rofi_menu.BackItem(),
            PlayPauseItem(),
            NextItem(),
            PreviousItem(),
            ShuffleItem(),
            RepeatItem(),
                ]

        return items
