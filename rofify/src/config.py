import os
import re
import configparser
from rofify.src.utils import substitute_pango_escape, truncate

user_dir = os.path.expanduser("~")
cache_location = os.path.join( user_dir, '.config/rofify/rofi_spotify_token.cache')

class Config:
    """
    Class used for conveying configuration settings
    """
    def __init__(self):
        self._config = configparser.ConfigParser()
        config_dir = os.path.join(user_dir,'.config/rofify/config')
        if not self._config.read(config_dir):
            raise FileNotFoundError(f"Cannot find config file at {config_dir}")

        # Dictionary for parsing the playlist features
    playlist_features = {
        '<collaborative>'    : lambda x : "collaborative" if x['collaborative'] else "non-collaborative",
        '<description>'      : lambda x : x['description'],
        '<name>'             : lambda x : x['name'],
        '<owner_name>'       : lambda x : x['owner']['display_name'],
        '<public>'           : lambda x : "public" if x['public'] else "private",
        '<number_of_tracks>' : lambda x : str(x['tracks']['total']) + " tracks",
    }
    playlist_features_pattern = '('+'|'.join(playlist_features.keys())+ ')'

    # used in order to traverse the track dictionary structure
    track_features = {
        '<album>'           : lambda x : x['album']['name'],
        '<artists>'         : lambda x : ', '.join([artist['name'] for artist in x['artists']]),
        '<disc_number>'     : lambda x : x['disc_number'],
        '<duration>'        : lambda x : "{:0.0f}:{:0.0f}".format(*divmod(x['duration_ms']/1000,60)),
        '<episode>'         : lambda x : str(x['episode']),
        '<name>'            : lambda x : x['name'],
        '<track_number>'    : lambda x : str(x['track_number']),
        '<type>'            : lambda x : x['type'],
    }
    track_features_pattern = '('+'|'.join(track_features.keys()) + ')'

    formatting_defaults = {
        'playlist-track-label':'<name><album><artists>',
        'search-track-label':'<name><artists><type>',
        'header-playback-label':'<isplaying><name><artists><shuffle><repeat>',
        'playlist-item-label':'<name><number_of_tracks>',
        'active-item-colour':'#1f782c',
    }

    icon_defaults = {
        'playlist-menu-icon':'蘿',
        'track-item-icon':'',
        'device-menu-icon':'',
        'recently-played-menu-icon':'',
        'saved-tracks-menu-icon':'',
        'search-tracks-menu-icon':'',
        'playlist-item-icon':'蘿',
    }

    state_defaults = {
        'shuffle-off':'劣',
        'shuffle-on':'列',

        'repeat-off':'稜',
        'repeat-context':'凌',
        'repeat-track':'綾',

        'playing':'Playing:',
        'paused':'Paused:',
        'nothing-playing':'Nothing Playing',
    }

    def get_format(self, option):
        return self._config.get(
            section="formatting",
            option=option,
            fallback=self.formatting_defaults.get(option)
        )

    def get_icon(self, option):
        return self._config.get(
            section="formatting",
            option=option,
            fallback=self.icon_defaults.get(option)
        )

    def get_state(self, option):
        return self._config.get(
            section="formatting",
            option=option,
            fallback=self.state_defaults.get(option),
        )

    def check_credentials(self, credential):
        if 'credentials' not in self._config.sections():
            raise KeyError(
        "The credentials section does not exist in the config file. username could not be retrieved"
        )
        else:
            creds = [self._config.get(section='credentials', option=cred, fallback="Not found")
            for cred in ['username','client_id','client_secret','redirect_uri']]

            err_string = f" \
                {credential} credential not found \n \
                settings parsed from the config file: \n \
                username:      {creds[0]}, \n \
                client_id:     {creds[1]}, \n \
                client_secret: {creds[2]}, \n \
                redirect_uri:  {creds[3]}"
            raise KeyError(err_string)

    @property
    def username(self):
        try:
            return self._config['credentials']['username']
        except KeyError:
            self.check_redentials('username')

    @property
    def client_id(self):
        try:
            return self._config['credentials']['client_id']
        except:
            self.check_credentials('client_id')
    
    @property
    def client_secret(self):
        try:
            return self._config['credentials']['client_secret']
        except:
            self.check_credentials('client_secret')

    @property
    def redirect_uri(self):
        try:
            return self._config['credentials']['redirect_uri']
        except:
            self.check_credentials('redirect_uri')

    def playlist_track_label(self, track):
        """
        Parse the config and return a string for the provided track,
        formatted according to the config for the playlist-track-label option.
        """

        structure = self.get_format('playlist-track-label')
        matches = re.findall(self.track_features_pattern, structure)

        track_label = self.get_icon('track-item-icon') + " "

        for match in matches[:-1]:
            field_text = self.track_features[match](track)
            margin = 2
            # Substitute pango escape sequences only after the text has been
            # truncated in order to ensure that it correctly renders in the menu
            track_label += substitute_pango_escape(
                truncate(field_text, (width-1)//len(matches)-3, margin)
            )
        track_label += substitute_pango_escape(
            truncate(
                self.track_features[matches[-1]](track), (width-1)//len(matches)-3, 0
            )
        )

        return track_label

    def playlist_item_label(self, playlist):
        """
        Parse the config and return a string representing a playlist,
        formmated according to the user entry in the config.
        """
        active_playlist = lambda x: \
            "<span foreground='{}'>".format(
                self.get_format('active-item-colour'))\
            + str(x) + " (playing)</span>"

        structure = self.get_format('playlist-item-label')

        matches = re.findall(self.playlist_features_pattern, structure)
        playlist_label = self.get_icon('playlist-item-icon') + " "
        for match in matches[:-1]:
            field_text = self.playlist_features.get(match)(playlist)
            margin = 2
            playlist_label += substitute_pango_escape(
                truncate(field_text, (width-1)//len(matches)-4, margin)
            )
        field_text = self.playlist_features.get(matches[-1])(playlist)
        playlist_label += substitute_pango_escape(
            truncate(field_text, (width-1)//len(matches)-4, margin)
        )

        return playlist_label

    async def header_playback_label(self, playback):
        """
        Parse the config and return a string formatted according to the config
        for the header-playback-label option
        """
        # First check to see if anything is playing
        if playback._playback is None or playback.current_item is None:
            # Make sure that nothing really is playing
            await playback.update_playback()
            if playback._playback is None or playback.current_item is None:
                return self.get_state('nothing-playing')

        # This needs to be declared here as it uses class-specific functions
        playback_features = {
            # where x is a playback object
            '<shuffle>': lambda x : self.get_state('shuffle-off') if not x.shuffle_state else self.get_state('shuffle-on'),
            '<repeat>': lambda x : {'off': self.get_state('repeat-off'),
                                    'track':self.get_state('repeat-track'),
                                    'context':self.get_state('repeat-context')}[x.repeat_state],
            # TODO add option for nothing playing or paused
            '<isplaying>': lambda x : self.get_state('playing') if x.playing else self.get_state('paused'),
        }


        # First we need to specify what is retrieved by the playback options
        playback_pattern = "(" + '|'.join(list(self.track_features.keys()) + list(playback_features.keys())) + ")"
        structure = self.get_format('header-playback-label')
        matches = re.findall(playback_pattern, structure)
        playback_label = ""

        # Margin is going to be replaced with a seperator " - "
        margin = 0

        for index,match in enumerate(matches):

            # TODO maybe add this as seperator or somthing like that in self

            # These elements are found
            if self.track_features.get(match) is not None:
                field = self.track_features[match](playback.current_item)
                playback_label += truncate(field, ((width)//len(matches)), margin, add_whitespace=False)

                if index + 1 < len(matches) and (matches[index+1] in self.track_features.keys()):
                    playback_label += " - "

            # These elements are formatted differently (i.e. without seperator)
            elif playback_features.get(match) is not None:
                field = playback_features[match](playback)
                playback_label += f" {field} "

        return playback_label


config = Config()

# get client width, prioritise environment variable
width = os.getenv("ROFI_WIDTH")
if width is not None\
and width[1:].isnumeric():
    width = -int(width)

# then check config
elif config._config.get(section='formatting',option='formatting_width', fallback=False):
    width = config._config['formatting']['formatting_width']

# Not much else to do than assume the defualt width of 90 characters
else:
    width = 90
