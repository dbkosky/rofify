#!/bin/bash

# Export relevant flags used by python as environment variables
# Negative width is rofi estimating character width, 
# e.g. -90 is roughly 90 characters width
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
export ROFI_WIDTH=-90
rofi -modi mymenu:$DIR/rofify/__main__.py\
	-show mymenu\
	-theme $DIR/rofify_theme.rasi\
	-config $DIR/rofify.config -width $ROFI_WIDTH\
	-show-icons
