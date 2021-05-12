from rofify.src.config import config
import asyncio
# TODO Make consistent what is or isn't async
import sys

class Playback:
    """
    Subdivision of the SpotifyAPI class. Delegates functions relating to controlling
    the current user's playback and getting information regarding the user's playback
    """

    def __init__(self, parent=None):
        # Playback as dictionary provided by the spotify api
        self._playback = None
        self.parent = parent
        self._client = self.parent.client

        # This is used by to update information about the playback
        # between menu executions
        self.meta = None

    async def update_playback(self):
        # The playback is updated this way in order to control
        # the number of calls made to the api
        self._playback = self._client.current_playback()
        if self.meta and self._playback:
            self.update_meta()

    def update_meta(self):
        self.meta.session['is_playing'] = self._playback['is_playing']
        self.meta.session['shuffle_state'] = self._playback['shuffle_state']
        self.meta.session['repeat_state'] = self._playback['repeat_state']

    @property
    def song_name(self):
        return self._playback['item']['name']

    @property
    def artist_names(self):
        return ', '.join([artist['name'] for artist in self._playback['item']['artists']])

    @property
    def shuffle_state(self):
        return self._playback['shuffle_state']

    @property
    def repeat_state(self):
        return self._playback['repeat_state']

    @property
    def current_item(self):
        return self._playback['item']

    @property
    def playing(self):
        return self._playback['is_playing']

    async def play_content(self, device_id, context_uri=None, uris=None, offset=None):
        self._client.start_playback(device_id, context_uri=context_uri, uris=uris, offset=offset)

    async def get_playback_label(self):
        """
        Get playback for the label displaying the currently playing song at the top 
        of the rofi menu
        """
        await self.update_playback()
        if self._playback is not None:
            if self.meta.session['is_playing']:
                return "Playing: {} - {}".format(self.song_name, self.artist_names)
            else:
                return "Paused:  {} - {}".format(self.song_name, self.artist_names)
        else:
            return "Nothing is playing"

    async def play_pause(self):
        await self.update_playback()
        if self._playback is not None:
            if self._playback['is_playing']:
                self._client.pause_playback()
            else:
                self._client.start_playback()

            self._playback['is_playing'] = not self._playback['is_playing']
            # Put this in the meta
            if self.meta:
                self.meta.session['is_playing'] = self._playback['is_playing']

    async def previous(self):
        await self.update_playback()
        if self._playback is not None:
            self._client.previous_track()
            # Wait for a short time before updating playback
            await asyncio.sleep(0.2)
            await self.update_playback()

    async def next(self):
        await self.update_playback()
        if self._playback is not None:
            self._client.next_track()
            # Wait for a short time before updating playback
            await asyncio.sleep(0.2)
            await self.update_playback()

    async def toggle_shuffle(self, device_id=None):
        await self.update_playback()
        # Shuffle state can be retrieved by the playback
        next_shuffle = not self.shuffle_state
        self._client.shuffle(
            state = next_shuffle,
            device_id=device_id,
        )
        self._playback['shuffle_state'] = next_shuffle
            # Put this in the meta
        if self.meta:
            self.meta.session['shuffle_state'] = self._playback['shuffle_state']

    async def cycle_repeat(self, device_id=None):
        await self.update_playback()
        # Repeat state can be off, context (e.g. repeat album 
        # or playlist), or track
        states = ['off', 'context', 'track']
        # find the index of the next state
        next_state = states[(states.index(self.repeat_state) + 1) % len(states)]
        self._client.repeat(
            state=next_state, 
            device_id=device_id,
        )
        self._playback['repeat_state'] = next_state
        if self.meta:
            self.meta.session['repeat_state'] = self._playback['repeat_state']

    async def header_playback_label(self):
        """
        Parse the config and return a string formatted according to the config
        for the header-playback-label option
        """
        # First check to see if anything is playing
        if self._playback is None or self.current_item is None:
            # Make sure that nothing really is playing
            await self.update_playback()
            if self._playback is None or self.current_item is None:
                return config.get_state('nothing-playing')

        # First we need to specify what is retrieved by the playback options
        playback_directory = {
            # where x is a playback object
            '<shuffle>': lambda x : config.get_state('shuffle-off') if not x.meta.session['shuffle_state'] else config.get_state('shuffle-on'),
            '<repeat>': lambda x : {'off': config.get_state('repeat-off'),
                                    'track':config.get_state('repeat-track'),
                                    'context':config.get_state('repeat-context'),}[x.meta.session['repeat_state']],
            # TODO add option for nothing playing or paused
            '<isplaying>': lambda x : config.get_state('play') if x.meta.session['playing'] else config.get_state('paused'),
        }
        playback_pattern = "(" + '|'.join(list(track_directory.keys()) + list(playback_directory.keys())) + ")"
        structure = config.header_playback_label
        matches = re.findall(playback_pattern, structure)
        playback_label = ""

        # Margin is going to be replaced with a seperator " - "
        margin = 0

        for index,match in enumerate(matches):

            # TODO maybe add this as seperator or somthing like that in config

            # These elements are found
            if track_directory.get(match) is not None:
                field = track_directory[match](playback.current_item)
                playback_label += truncate(field, ((width)//len(matches)), margin, add_whitespace=False)

                if index + 1 < len(matches) and (matches[index+1] in track_directory.keys()):
                    playback_label += " - "

            # These elements are formatted differently (i.e. without seperator)
            elif playback_directory.get(match) is not None:
                field = playback_directory[match](playback)
                playback_label += f" {field} "

        return playback_label
