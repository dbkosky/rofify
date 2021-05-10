import rofi_menu
import sys
from rofify.src.config import config

if __name__ == "__main__":

    if "--create-config" in sys.argv:
        config._create_default_config()

    elif "--create-token" in sys.argv:
        import spotipy.util as util

        scope = [
        # Playback reading permissions
        "user-read-playback-state",
        "user-read-playback-position",
        "user-read-currently-playing",

        # Permissions for track selection
        "user-read-recently-played",
        "user-library-read",
        # Optionals for playlist track selection
        "playlist-read-collaborative",
        "playlist-read-private",

        # Playback modification permissions
        "user-modify-playback-state",

        # Playlist/ Library modification permssions
        "user-library-modify",
        "playlist-modify-public",
        "playlist-modify-private",
        ]

        util.prompt_for_user_token(
            username      = config.username,
            client_id     = config.client_id,
            client_secret = config.client_secret,
            redirect_uri  = config.redirect_uri,
            cache_path    = config.cache_path,
            scope         = ' '.join(scope),
            show_dialog=True,
    )

    else:
        from rofify.src.MainMenu import MainMenu
        rofi_menu.run(MainMenu(),debug=True)
