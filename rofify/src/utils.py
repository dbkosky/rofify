from rofify.src.config import config
import re
import os

# get client width
width = os.getenv("WIDTH")
if width is not None\
    and width[1:].isnumeric():
        width = -int(width)

# used in order to traverse the track dictionary structure
track_directory = {
    '<album>'           : lambda x : x['album']['name'],
    '<artists>'         : lambda x : ', '.join([artist['name'] for artist in x['artists']]), 
    '<disc_number>'     : lambda x : x['disc_number'], 
    '<duration>'        : lambda x : "{:0.0f}:{:0.0f}".format(*divmod(x['duration_ms']/1000,60)),
    '<episode>'         : lambda x : str(x['episode']), 
    '<name>'            : lambda x : x['name'], 
    '<track_number>'    : lambda x : str(x['track_number']), 
    '<type>'            : lambda x : x['type'],
}

# compile the keys of the track dictionary for parsing formatting config strings 
track_pattern = re.compile(r"("+'|'.join(list(track_directory.keys())) + r")")

# used to escape pango markup in retrieved track fields
escape_chars = {
    '<'  : '&lt;',
    '>'  : '&gt;',
    '&'  : '&amp;',
    "'"  : '&#39;',
}
escape_pattern = re.compile(r"("+'|'.join(list(escape_chars.keys()))+ r")")

def truncate(string, length, extra=0, add_whitespace=True):
    """
    Add whitespace to strings shorter than the length, truncate strings 
    longer than the length, replace the last few characters with ellipsis
    """
    # Strip whitespace
    base = string.strip()
    difference = length-(len(base))
    if difference > 0:
        whitespace = difference*" " if add_whitespace else ""
        return base + whitespace + extra*" "
    else:
        return base[0:(length-1)]+"…" + extra*" "

def substitute_pango_escape(string):
    """
    Takes a string and substitutes all symbols used by pango with its related 
    escape sequence
    """
    return re.sub(escape_pattern, lambda x : escape_chars[x.group(0)], string)

def playlist_track_label(track):
    """
    Parse the config and return a string formatted according to the config
    for the playlist-track-label option
    """
    structure = config.playlist_track_label
    matches = re.findall(track_pattern, structure)
    track_label = config.track_item_icon + " "
    for index,match in enumerate(matches):
        field_text = track_directory[match](track)
        margin = 0 if index+1 == len(matches) else 2
        # Substitute pango escape sequences only after the text has been 
        # truncated in order to ensure the it correctly renders in rofi 
        track_label += substitute_pango_escape(
            truncate(field_text, (width-1)//len(matches)-3, margin)
        )

    return track_label

def header_playback_label(playback):
    """
    Parse the config and return a string formatted according to the config
    for the header-playback-label option
    """
    # First check to see if anything is playing
    if playback._playback is None:
        return config.nothing_playing

    # First we need to specify what is retrieved by the playback options
    playback_directory = {
        # where x is a playback object
        '<shuffle>': lambda x : config.shuffle_off if not x.shuffle_state else config.shuffle_on,
        '<repeat>': lambda x : {'off': config.repeat_off, 'track':config.repeat_track, 'context':config.repeat_context}[x.repeat_state],
        # TODO add option for nothing playing or paused
        '<isplaying>': lambda x : config.playing if x.playing else config.paused,
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
            playback_label += substitute_pango_escape(
                truncate(field, ((width-20)//len(matches))-2, margin, add_whitespace=False)
            )
            if index + 1 < len(matches) and (matches[index+1] in track_directory.keys()): 
                playback_label += " - "

        # These elements are formatted differently (i.e. without seperator)
        elif playback_directory.get(match) is not None:
            field = playback_directory[match](playback)
            playback_label += substitute_pango_escape(
                f" {field} "
            )

    return playback_label