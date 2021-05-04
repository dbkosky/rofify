from rofify.src.DynamicNestedMenu import DynamicNestedMenu
from rofify.src.TrackMenu import TrackMenu
from rofify.src.SpotifyAPI import spotify
from rofi_menu import Menu, BackItem

class AlbumMenu(Menu):
    """
    Provide a list of album items
    """
    def __init__(self, albums=None):
        self.albums = albums
        super().__init__()

    async def generate_menu_items(self, meta):
        """
        Generate a list of selected album items
        """
        items = [BackItem()]
        for album in self.albums['items']:
            items.append(
                DynamicNestedMenu(
                    text=album['name'],
                    sub_menu_type=TrackMenu.from_album,
                    album=album,
                )
            )

        return items

    @classmethod
    async def from_artist(cls, artist=None):
        """
        Build an album menu displaying all the avaliable albums for the
        given artist.
        """
        return cls(albums=(await spotify.artist_albums(artist['id'])))
