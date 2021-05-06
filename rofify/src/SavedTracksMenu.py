from rofi_menu import Menu, BackItem, NestedMenu, Operation, constants
from rofify.src.TrackMenu import TrackMenu, TrackItem
from rofify.src.SpotifyAPI import spotify
from rofify.src.config import config

class SavedTracksMenu(TrackMenu):
    """
    Display the user a list of their recently played tracks that they can
    listen to by selecting. Should be accessible from the top menu.
    """
    def __init__(self):
        super().__init__(
            prompt="Saved Tracks", 
            track_formatter=config.playlist_track_label
        )

    async def generate_menu_items(self, meta):

        await self.update_popup_meta(meta)

        saved_tracks = await spotify.async_all_saved_tracks()
        self.tracks = [item['track'] for item in saved_tracks['items']]
        track_items = []
        for track in self.tracks:    
            track_items.append(
                TrackItem(
                    track=track,
                    # No offset is given for saved tracks 
                    offset=None, 
                    text=track['name']
                )
            )
        return [BackItem()] + track_items
