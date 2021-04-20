import os
import configparser

# TODO configure user settings/config
config = configparser.ConfigParser()
user_dir = os.path.expanduser("~")
config.read(os.path.join(user_dir,'.config/rofify/config'))
cache_location = os.path.join( user_dir, '.config/rofify/rofi_spotify_token.cache' )