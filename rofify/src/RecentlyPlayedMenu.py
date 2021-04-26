from rofi_menu import Menu, BackItem, NestedMenu, Operation, constants
from rofify.src.TrackMenu import TrackMenu, TrackItem
from rofify.src.SpotifyAPI import spotify
from rofify.src.utils import playlist_track_label
from rofify.src.config import config


class NestedRecentlyPlayedMenu(NestedMenu):
    """
    Item used to provide selectable recently played menu that only builds when selected.
    """
    def __init__(self, **kwargs):
        super().__init__(text=f"{config.recently_played_menu_icon} Recently Played")
        
    async def build(self, parent_menu, item_id, meta):
        """
        The normal implementation of this function builds the submenu by default.
        Since the subenu is only needed upon selection (or selection of items within the submenu), 
        we will only build the submenu at this point if the meta.selected_id is deeper than this level, 
        and matches the nested menu.

        """
        obj = await super().build(parent_menu=parent_menu, item_id=item_id, meta=meta)

        if item_id is not None and meta.selected_id is not None and\
            len(item_id) < len(meta.selected_id) and\
            meta.selected_id[len(item_id)-1] == item_id[-1]:

            self.sub_menu = RecentlyPlayedMenu()
            obj.sub_menu = await self.sub_menu.build(menu_id=obj.id, meta=meta)

        return obj

    async def on_select(self, meta):
        """
        This differs to the normal nested menu implementation. Recently played menu 
        to be built only upon being selected.
        """
        self.sub_menu = RecentlyPlayedMenu()
        self.sub_menu = await self.sub_menu.build(menu_id=meta.selected_id, meta=meta)

        return Operation(constants.OP_OUTPUT, await self.sub_menu.handle_render(meta))

class RecentlyPlayedMenu(TrackMenu):
    """
    Display the user a list of their recently played tracks that they can
    listen to by selecting. Should be accessible from the top menu.
    """
    def __init__(self):
        super().__init__(
            prompt="Recently Played", 
            track_formatter=playlist_track_label
        )

    async def generate_menu_items(self, meta):
        
        self.tracks = await spotify.get_recently_played()
        track_items = []
        for track in self.tracks:    
            track_items.append(
                TrackItem(
                    track=track, 
                    offset=track['offset'], 
                    text=track['name']
                )
            )
        return [BackItem()] + track_items
