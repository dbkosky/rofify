import rofi_menu
from rofify.src.DynamicNestedMenu import DynamicNestedMenu
from rofify.src.TrackMenu import TrackMenu
from rofify.src.SpotifyAPI import spotify
from rofify.src.Hotkeys import hotkeys
from rofify.src.config import config

class PlaylistMenu(rofi_menu.Menu):
    """
    Menu the provides the user the option to select from their playlists.
    Should be accessible from the main menu.
    """

    def __init__(self, prompt=None):
        super().__init__()
        self.prompt="Playlists"


    async def pre_render(self, meta):
        """
        The playback label contains info about the current playback.
        """
        self.prompt = await config.header_playback_label(spotify.playback)
        await super().pre_render(meta)

    async def generate_menu_items(self, meta):
        """ All playlists from the current user as nested menus
        """
        nested_playlist_menus = [rofi_menu.BackItem()]
        for playlist in (await spotify.async_all_playlists()):
            nested_playlist_menus.append(
                DynamicNestedMenu(
                    sub_menu_type=TrackMenu.from_playlist,
                    playlist=playlist,
                    text=config.playlist_item_label(playlist),
                )
            )
        return nested_playlist_menus

    async def on_user_input(self, meta):
        await hotkeys.handle_user_input()
        return rofi_menu.Operation(rofi_menu.OP_REFRESH_MENU)
