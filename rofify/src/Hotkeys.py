from rofify.src.SpotifyAPI import spotify
import os

class Hotkeys:

    # Map of corresponding actions for custom keybindings
    input_map = {
        '10':spotify.playback.previous,
        '11':spotify.playback.next,
        '12':spotify.playback.play_pause,
        '13':spotify.playback.toggle_shuffle,
        '14':spotify.playback.cycle_repeat,
    }

    async def handle_user_input(self):
        """
        Compare the rofi environment variable to find what kind of user input was given
        i.e. was it simply return, or one of the specified hotkeys
        """
        retcode = os.getenv("ROFI_RETV")
        if retcode and retcode.isnumeric():
            action = self.input_map.get(retcode)
            if action is not None:
                await action()

hotkeys = Hotkeys()
