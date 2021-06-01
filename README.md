# Rofify
## Spotify Menu in Rofi
This app is intended to provide an alternative method for controlling spotify playback. 
It's inspired by the terminal application [SpoTUI](https://github.com/ceuk/SpoTUI), and makes heavy use of 
[spotipy](https://github.com/plamere/spotipy) and [python-rofi-menu](https://github.com/miphreal/python-rofi-menu). The included theme is based on the
the rofi themes by [adi1090x](https://github.com/adi1090x/rofi).

![selecting from a playlist in rofify](previews/playlists.gif)

Before you attempt to install this, it's worth noting that, at present, you need spotify premium in order to use this. You will need create an app on [the spotify devolper site](https://developer.spotify.com) (go to dashboard, then create an app).

To install the package run: 
``` sh
pip install rofify
```

## Setup
You will need to add a few items to the configuration to get started.
To create the a config file at .config/rofify/config you can run:
``` sh
python -m rofify --create-config
```

In the config file you will need to set the values for username, client_id and client_secret.
The client_id and client_secret can be obtained on your application page on developer.spotify.com.
Redirect_uri can be left the same, unless you have changed it in the application settings on 
developer.spotify.com.

Next, run:
``` sh
python -m rofify --create-token
```
This is required, as the authentication uses this token in every reuqest made.
This creates a token using the path specified by 'cache_path' in the config file. 

Try and see if the package is working by typing running Rofi:
``` sh
rofi -modi spotify:"python -m rofify" -show spotify
```

## Hotkeys
If you want to run rofify with hotkeys you'll need to create or modify custom key bindings in your rofi config. For example:

```
! Previous track
rofi.kb-custom-1:   Super+Left

! Next track
rofi.kb-custom-2:   Super+Right

! Toggle pause/play
rofi.kb-custom-3:   Super+space

! Toggle shuffle
rofi.kb-custom-4:   Super+s

! Cycle repeat state
rofi.kb-custom-5:   Super+r
```

These are convenient keybindings for me, but some experimentation might be needed depending on your setup. Make sure that any keybinding you use isn't already used by another default rofi keybinding or it will throw an error (you can get a full list of the config options by running rofi -dump-config).
