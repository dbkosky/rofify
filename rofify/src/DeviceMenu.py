from rofify.src.SpotifyAPI import spotify
from rofify.src.Hotkeys import hotkeys
from rofify.src.config import config
import rofi_menu
import asyncio

active_label = lambda x: "<span foreground='{}'>".format(config.get_format('active-item-colour')) + str(x) + " (active)</span>"

class DeviceItem(rofi_menu.Item):
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


class DeviceMenu(rofi_menu.Menu):
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

        items = [rofi_menu.BackItem()]

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

        await hotkeys.handle_user_input()
        return rofi_menu.Operation(rofi_menu.constants.OP_REFRESH_MENU)
