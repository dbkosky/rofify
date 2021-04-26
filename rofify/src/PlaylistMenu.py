import asyncio
from rofi_menu import NestedMenu, Menu, Operation, constants, BackItem
from rofify.src.TrackMenu import TrackMenu
from rofify.src.SpotifyAPI import spotify

class NestedPlaylistTrackMenu(NestedMenu):
    """
    Item used to provide selectable playlists in the playlist menu 
    """
    def __init__(self, text=None, playlist=None, **kwargs):
        super().__init__(text=text)
        # Playlist data structure as provided by the spotify api
        self.playlist = playlist
        
    async def build(self, parent_menu, item_id, meta):
        """
        The normal implementation of this function builds the submenu by default.
        Since the subenu is only needed upon selection (or selection of items within the submenu), 
        we will only build the submenu at this point if the meta.selected_id is deeper than this level, 
        and matches the nested menu. 

        """
        obj = await super().build(parent_menu=parent_menu, item_id=item_id, meta=meta)

        # Only build the trackmenu for the playlist if the item has been selected
        if item_id is not None and meta.selected_id is not None and\
            len(item_id) < len(meta.selected_id) and\
            meta.selected_id[len(item_id)-1] == item_id[-1]:

            self.sub_menu = await TrackMenu.from_playlist(playlist=self.playlist)
            obj.sub_menu = await self.sub_menu.build(menu_id=obj.id, meta=meta)

        return obj

    async def on_select(self, meta):
        """
        This differs to the normal nested menu implementation. Depending on the user
        playlists can be large. Building a track menu for every playlist at the start 
        has a noticable effect on performance, so instead the playlist menus are going
        to be built upon being selected.
        """
        self.sub_menu = await TrackMenu.from_playlist(playlist=self.playlist)
        self.sub_menu = await self.sub_menu.build(menu_id=meta.selected_id, meta=meta)

        return Operation(constants.OP_OUTPUT, await self.sub_menu.handle_render(meta))

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
                NestedPlaylistTrackMenu(
                    playlist=playlist,
                    text=playlist['name'],
                )
            )
        return nested_playlist_menus