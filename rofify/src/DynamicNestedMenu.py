import asyncio
from rofi_menu import NestedMenu, Operation, constants
from rofify.src.SpotifyAPI import spotify

class DynamicNestedMenu(NestedMenu):
    """
    Item used to provide selectable playlists in the playlist menu 
    """
    def __init__(self, text=None, sub_menu_type=None, **sub_menu_args):
        super().__init__(text=text)
        self.sub_menu_type = sub_menu_type
        self.sub_menu_args = sub_menu_args
        
    async def build(self, parent_menu, item_id, meta):
        """
        The normal implementation of this function builds the submenu by default.
        Since the subenu is only needed upon selection (or selection of items within the submenu), 
        we will only build the submenu at this point if the meta.selected_id is deeper than this level, 
        and matches the nested menu. 
        """
        obj = await super().build(parent_menu=parent_menu, item_id=item_id, meta=meta)
        # Only build the sub menu if the item has been selected or the nested menu was part of the
        # previous menu selection and there is no selected item (i.e. there was user input)
        if (item_id is not None and meta.selected_id is not None and\
            len(item_id) < len(meta.selected_id) and\
            meta.selected_id[len(item_id)-1] == item_id[-1])\
            or\
            (meta.selected_id is None and\
             meta.session.get('last_active_menu') and\
             meta.session['last_active_menu'][:len(item_id)] == item_id):

            if asyncio.iscoroutinefunction(self.sub_menu_type):
                self.sub_menu = await self.sub_menu_type(**self.sub_menu_args)
                obj.sub_menu = await self.sub_menu.build(menu_id=obj.id, meta=meta)
            else:
                self.sub_menu = self.sub_menu_type(**self.sub_menu_args)
                obj.sub_menu = await self.sub_menu.build(menu_id=obj.id, meta=meta)

        return obj

    async def on_select(self, meta):
        """
        This differs to the normal nested menu implementation. Depending on the application, menus 
        be large. Building a large menus at the start has a noticable effect on performance, 
        so instead the menus are going to be built only if they have been selected.
        """
        if asyncio.iscoroutinefunction(self.sub_menu_type):
            self.sub_menu = await self.sub_menu_type(**self.sub_menu_args)
            self.sub_menu = await self.sub_menu.build(menu_id=meta.selected_id, meta=meta)
        else:
            self.sub_menu = self.sub_menu_type(**self.sub_menu_args)
            self.sub_menu = await self.sub_menu.build(menu_id=meta.selected_id, meta=meta)        
            
        return Operation(constants.OP_OUTPUT, await self.sub_menu.handle_render(meta))
