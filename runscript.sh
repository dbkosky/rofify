#!/bin/bash

# Export relevant flags used by python as environment variables
# Negative width is rofi estimating character width, 
# e.g. -90 is roughly 90 characters width
export WIDTH=-90
rofi -modi mymenu:$PWD/rofify/__main__.py\
	-show mymenu -theme rofify_theme.rasi\
	-config tmp.config -width $WIDTH\
	-show-icons
