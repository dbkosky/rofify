from rofi_menu import Menu, BackItem, NestedMenu, Operation, constants
from rofify.src.TrackMenu import TrackMenu, TrackItem
from rofify.src.SpotifyAPI import spotify
from rofify.src.config import config

class RecentlyPlayedMenu(TrackMenu):
    """
    Display the user a list of their recently played tracks that they can
    listen to by selecting. Should be accessible from the top menu.
    """
    def __init__(self):
        super().__init__(
            prompt="Recently Played", 
            track_formatter=config.playlist_track_label
        )

    async def generate_menu_items(self, meta):

        await self.update_popup_meta(meta)

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
