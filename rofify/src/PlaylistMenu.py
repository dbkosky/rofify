from rofi_menu import NestedMenu, Menu, Operation, constants, BackItem
from rofify.src.DynamicNestedMenu import DynamicNestedMenu
from rofify.src.TrackMenu import TrackMenu
from rofify.src.SpotifyAPI import spotify
from rofify.src.config import config

class PlaylistMenu(Menu):
    """
    Menu the provides the user the option to select from their playlists.
    Should be accessible from the main menu.
    """

    def __init__(self, prompt=None):
        super().__init__()
        self.prompt="Playlists"

    async def generate_menu_items(self,meta):
        """ All playlists from the current user as nested menus
        """
        nested_playlist_menus = [BackItem()]
        for playlist in (await spotify.async_all_playlists()):
            nested_playlist_menus.append(
                DynamicNestedMenu(
                    sub_menu_type=TrackMenu.from_playlist,
                    playlist=playlist,
                    text=config.playlist_item_label(playlist),
                )
            )
        return nested_playlist_menus
