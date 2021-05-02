from rofi_menu import Menu, Operation, constants, Item, BackItem
from rofify.src.SpotifyAPI import spotify
from rofify.src.TrackMenu import TrackItem, TrackMenu
from rofify.src.utils import playlist_track_label
import sys

class SearchMenu(TrackMenu):

    allow_user_input = True

    def __init__(self):
        super().__init__(track_formatter=playlist_track_label)

    class SearchItem(Item):
        """ Show the user what they searched, clear the search on select """
        async def render(self, meta):
            entered_text = meta.session.get("search", None)
            if entered_text:
                return f"<b>Clear Search</b>: <i>{entered_text}</i>"
            else:
                return f"<b>Search results will show up bellow</b>"

        async def on_select(self, meta):
            """ Clear the search """
            meta.session['search'] = ""
            back_item = BackItem()
            back_item.id = [meta.selected_id][:-1] + ['0']
            self.id = [meta.selected_id][:-1] + ['1']
            self.parent_menu.items = [back_item, self]
            return await super().on_select(meta)

    # async def build(self, menu_id, meta):
    #     """
    #     This needs to be different in order to allow user input, since without a specific
    #     object to provide a point to return to, we need to set the environment variable to
    #     return to this point
    #     """

    #     obj = self.clone()
    #     obj.id = menu_id
    #     obj.items = await obj.build_menu_items(meta=meta)
    #     return obj

    async def generate_menu_items(self, meta):
        """ Generate track items from search according to user input """

        # Set the element to bring up device menu if there is no set device
        meta.session.setdefault('popup_device_menu', False)
        if not spotify.device.current_device:
            meta.session['popup_device_menu'] = True
        else:
            meta.session['popup_device_menu'] = False

        if meta.user_input:
            meta.session['search'] = meta.user_input
        elif meta:
            pass

        items = [BackItem(), self.SearchItem(),]
        tracks = await spotify.async_search(
            meta.session['search'],
            ) \
            if meta.session['search'] else {'items':[]}
        
        for track in tracks['items']:
            items.append(
                TrackItem(
                    track=track,
                    offset=None,
                    text=track['name'],
                )
            )
        return items

    async def on_user_input(self, meta):
        
        if not meta.user_input in [item.text for item in self.items]:
            meta.session['search'] = meta.user_input
        return Operation(constants.OP_REFRESH_MENU)
