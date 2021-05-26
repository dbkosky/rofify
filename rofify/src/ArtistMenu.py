from rofify.src.DynamicNestedMenu import DynamicNestedMenu
from rofify.src.TrackMenu import TrackMenu, TrackItem
from rofify.src.AlbumMenu import AlbumMenu
from rofify.src.SpotifyAPI import spotify
import rofi_menu
from rofify.src.utils import substitute_pango_escape
from rofify.src.config import config
from rofify.src.Hotkeys import hotkeys

class ArtistMenu(rofi_menu.Menu):
    """
    Provide a list of album items
    """
    def __init__(self, artists=None):
        self.artists = artists
        super().__init__()

    async def pre_render(self, meta):
        """
        The playback label contains info about the current playback.
        """
        self.prompt = await config.header_playback_label(spotify.playback)
        await super().pre_render(meta)

    async def generate_menu_items(self, meta):
        """
        Generate a list of selected album items
        """
        items = [rofi_menu.BackItem()]
        for artist in self.artists['items']:
            items.append(
                DynamicNestedMenu(
                    text=artist['name'],
                    sub_menu_type=ArtistPage,
                    artist=artist,
                )
            )

        return items


class ArtistPage(rofi_menu.Menu):
    # This menu should have a combination of the artist's top tracks and
    # all of the artists albums.

    def __init__(self, artist=None, track_formatter=config.playlist_track_label):
        self.artist = artist
        self.track_formatter=track_formatter
        self.context=None
        super().__init__()

    async def pre_render(self, meta):
        """
        The playback label contains info about the current playback.
        """
        self.prompt = await config.header_playback_label(spotify.playback)
        await super().pre_render(meta)

    async def generate_menu_items(self, meta):

        # Set the element to bring up device menu if there is no set device
        meta.session.setdefault('popup_device_menu', False)
        if not spotify.device.current_device:
            meta.session['popup_device_menu'] = True
        else:
            meta.session['popup_device_menu'] = False

        items = [rofi_menu.BackItem()]

        top_tracks = rofi_menu.Item(nonselectable=True, text=f"{self.artist['name']} Top Tracks:")
        items.append(top_tracks)

        top_tracks = spotify.client.artist_top_tracks(self.artist['id'])['tracks']
        albums = spotify.client.artist_albums(self.artist['id'])['items']

        for track in top_tracks:
            items.append(
                TrackItem(
                    track=track
                )
            )

        artist_albums = rofi_menu.Item(nonselectable=True, text=f"{self.artist['name']} Albums:")
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

    async def on_user_input(self, meta):

        await hotkeys.handle_user_input()
        return rofi_menu.Operation(rofi_menu.constants.OP_REFRESH_MENU)
