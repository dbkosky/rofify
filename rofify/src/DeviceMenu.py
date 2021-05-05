from rofify.src.SpotifyAPI import spotify
from rofify.src.config import config
from rofi_menu import Menu, Item, BackItem, Operation, constants
import asyncio

import sys

active_label = lambda x: "<span foreground='{}'>".format(config.get_format('active-item-colour')) + str(x) + " (active)</span>"

class DeviceItem(Item):
    """
    Representing a device in the device menu. Should display the item differently 
    if the device is active, and allow the user to transfer playback to the related
    device when selected. 
    """
    def __init__(self, text=None, device=None):
        super().__init__(text=text)
        # as a dictionary provided by the spotify api
        self.device = device

    async def load(self, meta):
        await super().load(meta)
        # Check the session meta to se if the device is active and format the
        # menu item text accordingly
        if meta.session['active_device'] is not None and \
            meta.session['active_device'] == self.device['id']:
            self.text = active_label(self.device['name'])
        else:
            self.text = self.device['name']

    async def on_select(self, meta):
        # Transfer playback to the selected device
        spotify.device.transfer_playback(self.device['id'])
        meta.session['active_device'] = self.device['id']
        return await super().on_select(meta)


class DeviceMenu(Menu):
    """
    Menu accessible from the top menu that allows user to see the available devices and 
    transfer playback between them
    """
    def __init__(self, prompt=None):
        if prompt:
            super().__init__(prompt=prompt)
        elif not spotify.device.current_device:
            super().__init__(prompt="Select a device")
        else:
            super().__init__()

    # TODO add a method to allow user to favourite devices and cache device id
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
