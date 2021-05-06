from rofi_menu import Menu, Operation, constants, Item, BackItem
from rofify.src.DynamicNestedMenu import DynamicNestedMenu
from rofify.src.AlbumMenu import AlbumMenu
from rofify.src.ArtistMenu import ArtistMenu, ArtistPage
from rofify.src.PlaylistMenu import PlaylistMenu
from rofify.src.SpotifyAPI import spotify
from rofify.src.TrackMenu import TrackItem, TrackMenu
from rofify.src.config import config

class SearchItem(Item):
        """ Show the user what they searched, clear the search on select """
        async def render(self, meta):
            entered_text = meta.session.get("search", None)
            if entered_text:
                return f"<b>Clear Search</b>: <i>{entered_text}</i>"
            else:
                return f"<b>Search results will show up bellow</b>"

        async def on_select(self, meta):
            """ Clear the search """
            meta.session['search'] = ""
            back_item = BackItem()
            back_item.id = [meta.selected_id][:-1] + ['0']
            self.id = [meta.selected_id][:-1] + ['1']
            self.parent_menu.items = [back_item, self]
            return await super().on_select(meta)


class SearchTrackMenu(TrackMenu):
    """
    Menu that allows users to type in content.
    """
    allow_user_input = True

    def __init__(self):
        super().__init__(track_formatter=config.playlist_track_label)

    async def generate_menu_items(self, meta):
        """ Generate track items from search according to user input """

        await self.update_popup_meta(meta)

        if meta.user_input:
            meta.session['search'] = meta.user_input
        elif meta:
            pass

        items = [BackItem(), SearchItem(),]
        tracks = await spotify.async_search(
            meta.session['search'],
            ) \
            if meta.session['search'] else {'items':[]}
        
        for track in tracks['items']:
            items.append(
                TrackItem(
                    track=track,
                    offset=None,
                    text=track['name'],
                )
            )
        return items

    async def on_user_input(self, meta):
        
        if not meta.user_input in [item.text for item in self.items]:
            meta.session['search'] = meta.user_input
        return Operation(constants.OP_REFRESH_MENU)


class SearchAlbumMenu(AlbumMenu):
    """

    """
    allow_user_input = True

    def __init__(self):
        super().__init__()

    async def generate_menu_items(self, meta):
        """
        Generate album items from search according to user input
        """
        if meta.user_input:
            meta.session['search'] = meta.user_input

        items = [BackItem(), SearchItem(),]
        albums = await spotify.async_search(
            meta.session['search'],
            type='album',
        ) if meta.session.get('search') else {'items':[]}

        for album in albums['items']:
            items.append(
                DynamicNestedMenu(text=album['name'], sub_menu_type=TrackMenu.from_album, album=album)
            )

        return items

    async def on_user_input(self, meta):
        if not meta.user_input in [item.text for item in self.items]:
            meta.session['search'] =  meta.user_input
        return Operation(constants.OP_REFRESH_MENU)


class SearchArtistMenu(TrackMenu, ArtistMenu):
    """

    """
    allow_user_input = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def generate_menu_items(self, meta):

        if meta.user_input:
            meta.session['search'] = meta.user_input

        items = [BackItem(), SearchItem()]
        artists = await spotify.async_search(
            meta.session['search'],
            type='artist',
        ) if meta.session.get('search') else {'items':[]}

        for artist in artists['items']:
            items.append(
                DynamicNestedMenu(
                    text=artist['name'],
                    sub_menu_type=ArtistPage,
                    artist=artist,
                )
        )
        return items


class SearchPlaylistMenu(PlaylistMenu):
    """

    """
    allow_user_input = True

    def __init__(self, **kwargs):
        super().__init__(self, **kwargs)

    async def generate_menu_items(self, meta):

        if meta.user_input:
            meta.session['search'] = meta.user_input

        items = [BackItem(), SearchItem()]
        playlists = await spotify.async_search(
            meta.session['search'],
            type='playlist',
        ) if meta.session.get('search') else {'items':[]}

        for playlist in playlists['items']:
            items.append(
                DynamicNestedMenu(
                    sub_menu_type=TrackMenu.from_playlist,
                    playlist=playlist,
                    text=playlist['name'],
                )
        )

        return items
