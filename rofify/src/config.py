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

    @property
    def playlist_menu_icon(self):
        return self._config.get(
            section='formatting', 
            option='playlist-menu-icon',
            fallback="",
        )
    
    @property
    def device_menu_icon(self):
        return self._config.get(
            section='formatting', 
            option='device-menu-icon',
            fallback="",
        )

    @property
    def track_item_icon(self):
        return self._config.get(
            section='formatting',
            option='track-item-icon',
            fallback="",
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
            self.check_credentials('username')

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