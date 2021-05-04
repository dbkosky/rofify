from rofify.src.DynamicNestedMenu import DynamicNestedMenu
from rofify.src.TrackMenu import TrackMenu, TrackItem
from rofify.src.AlbumMenu import AlbumMenu
from rofify.src.SpotifyAPI import spotify
from rofi_menu import Menu, BackItem, Item
from rofify.src.utils import playlist_track_label, substitute_pango_escape

class ArtistMenu(Menu):
    """
    Provide a list of album items
    """
    def __init__(self, artists=None):
        self.artists = artists
        super().__init__()

    async def generate_menu_items(self, meta):
        """
        Generate a list of selected album items
        """
        items = [BackItem()]
        for artist in self.artists['items']:
            items.append(
                DynamicNestedMenu(
                    text=artist['name'],
                    sub_menu_type=ArtistPage,
                    artist=artist,
                )
            )

        return items


class ArtistPage(Menu):
    # This menu should have a combination of the artist's top tracks and
    # all of the artists albums.

    def __init__(self, artist=None, track_formatter=playlist_track_label):
        self.artist = artist
        self.track_formatter=track_formatter
        self.context=None
        super().__init__()

    async def generate_menu_items(self, meta):

        # Set the element to bring up device menu if there is no set device
        meta.session.setdefault('popup_device_menu', False)
        if not spotify.device.current_device:
            meta.session['popup_device_menu'] = True
        else:
            meta.session['popup_device_menu'] = False

        items = [BackItem()]

        top_tracks = Item(nonselectable=True, text=f"{self.artist['name']} Top Tracks:")
        items.append(top_tracks)

        top_tracks = spotify.client.artist_top_tracks(self.artist['id'])['tracks']
        albums = spotify.client.artist_albums(self.artist['id'])['items']

        for track in top_tracks:
            items.append(
                TrackItem(
                    track=track
                )
            )

        artist_albums = Item(nonselectable=True, text=f"{self.artist['name']} Albums:")
        items.append(artist_albums)

        for album in albums:
            items.append(
                DynamicNestedMenu(
                    text=substitute_pango_escape(album['name']),
                    sub_menu_type=TrackMenu.from_album,
                    album=album,
                )
            )

        return items
