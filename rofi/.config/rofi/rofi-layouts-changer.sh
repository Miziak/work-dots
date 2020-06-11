#!/bin/bash
LAYOUT=$(ls ~/.config/qtile/screenlayouts/ | sed "s/.sh//" | rofi -dmenu)

if sh ~/.config/qtile/screenlayouts/$LAYOUT.sh 2> /dev/null ; then
  if [[ $LAYOUT == *"mirror"* ]]; then
    touch /tmp/QTILE_SCREEN_MIRROR
  else
    rm /tmp/QTILE_SCREEN_MIRROR 2> /dev/null
  fi
  qtile-cmd -o cmd -f restart 2> /dev/null
fi
