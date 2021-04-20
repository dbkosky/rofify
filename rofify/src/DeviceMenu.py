
from rofify.src.SpotifyAPI import spotify
from rofi_menu import Menu, Item, BackItem, Operation, constants
import asyncio
import sys

# Formatting for currently active device
ACTIVE_COLOR = "#48cf5c"
active_label = lambda x: f"<span foreground='{ACTIVE_COLOR}'>" + str(x) + " (active)" + "</span>" 

class DeviceItem(Item):
    
    def __init__(self, text=None, device=None):
        super().__init__(text=text)
        self.device = device

    async def load(self, meta):
        await super().load(meta)
        if meta.session['active_device'] is not None and \
            meta.session['active_device'] == self.device['id']:
            self.text = active_label(self.device['name'])
        else:
            self.text = self.device['name']


    async def on_select(self, meta):
        spotify.device.transfer_playback(self.device['id'])
        meta.session['active_device'] = self.device['id']
        return await super().on_select(meta)

class DeviceMenu(Menu):
    
    async def generate_menu_items(self, meta):

        items = [BackItem()] 

        # This is used to keep track of which device is active between user input
        meta.session.setdefault('active_device', None)

        # Populate items with DeviceItems for each device
        devices = spotify.device.all_devices()
        for device in devices:
            if device['is_active']:
                meta.session['active_device'] = device['id']
            items.append(DeviceItem(device=device))
        
        return items

    async def on_user_input(self, meta):
        return Operation(constants.OP_REFRESH_MENU)
