import asyncio

class Device:

    def __init__(self, client=None):
        self._client = client
        self.current_device = self.get_active_device()

    def transfer_playback(self, to_device_id):
        self._client.transfer_playback(to_device_id, force_play=False)
        self.current_device = self.get_active_device()

    def get_active_device(self):
        for device in self._client.devices()['devices']:
            if device['is_active']:
                return device
        return None

    def all_devices(self):
        return self._client.devices()['devices']
    