import os
import configparser

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

    formatting_defaults = {
        'playlist-track-label':'<name><album><artists>',
        'search-track-label':'<name><artists><type>',
        'header-playback-label':'<isplaying><name><artists><shuffle><repeat>',
        'active-item-colour':'#1f782c'
    }

    icon_defaults = {
        'playlist-menu-icon':'蘿',
        'track-item-icon':'',
        'device-menu-icon':'',
        'recently-played-menu-icon':'',
        'saved-tracks-menu-icon':'',
        'search-tracks-menu-icon':'',
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

config = Config()
