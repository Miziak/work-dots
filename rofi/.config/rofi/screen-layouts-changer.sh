#!/bin/bash
LAYOUT=$(ls ~/.config/qtile/screenlayouts/ | sed "s/.sh//" | rofi -dmenu)
if [[ $LAYOUT == *"mirror"* ]]; then
  touch /tmp/QTILE_SCREEN_MIRROR
else
  rm /tmp/QTILE_SCREEN_MIRROR 2> /dev/null
fi
sh ~/.config/qtile/screenlayouts/$LAYOUT.sh
qtile-cmd -o cmd -f restart 2> /dev/null
