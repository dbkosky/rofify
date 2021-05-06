import re
import os

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
