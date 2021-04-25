from rofi_menu import Menu, BackItem
from rofify.src.TrackMenu import TrackMenu, TrackItem
from rofify.src.SpotifyAPI import spotify
from rofify.src.utils import playlist_track_label

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