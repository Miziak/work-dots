import os
import subprocess
import pyudev
from Xlib import display as xdisplay

from typing import List  # noqa: F401

from libqtile import bar, layout, widget, hook
from libqtile.config import Click, Drag, Group, Key, Screen, Match, ScratchPad, DropDown
from libqtile.lazy import lazy
from libqtile.log_utils import logger

control = "control"
shift = "shift"
alt = "mod1"
mod = "mod4"
# xephyr mod
# mod = alt

term = "alacritty"

keys = [
    Key([mod], "h", lazy.layout.left()),
    Key([mod], "l", lazy.layout.right()),
    Key([mod], "j", lazy.layout.down()),
    Key([mod], "k", lazy.layout.up()),
    Key([mod, control], "h", lazy.layout.swap_left()),
    Key([mod, control], "l", lazy.layout.swap_right()),
    Key([mod, control], "j", lazy.layout.shuffle_down()),
    Key([mod, control], "k", lazy.layout.shuffle_up()),
    Key([mod, shift], "l", lazy.layout.grow()),
    Key([mod, shift], "h", lazy.layout.shrink()),
    Key([mod], "equal", lazy.layout.normalize()),
    Key([mod], "c", lazy.window.kill(), desc="Kill focused window"),
    Key([mod], "q", lazy.to_screen(0), desc="Keyboard focus to monitor 1"),
    Key([mod], "w", lazy.to_screen(1), desc="Keyboard focus to monitor 2"),
    Key([mod], "Return", lazy.spawn(term)),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod, control], "f", lazy.window.toggle_floating()),
    Key([mod, alt], "m", lazy.to_layout_index(1)),
    Key([mod, alt], "s", lazy.to_layout_index(0)),
    Key([mod, control], "r", lazy.restart(), desc="Restart qtile"),
    Key([mod, control], "q", lazy.shutdown(), desc="Shutdown qtile"),
    Key([mod], "r", lazy.spawn("rofi -show drun")),
    Key([mod, control], "space", lazy.spawn("rofimoji")),
    Key([], "Print", lazy.spawn("gnome-screenshot")),
    Key([shift], "Print", lazy.spawn("gnome-screenshot -i")),
    Key([mod], "b", lazy.spawn("google-chrome")),
    Key([mod], "n", lazy.spawn(term + ' --class="term-ranger" -e ranger')),
]

groups = [
    ScratchPad(
        "scratchpad",
        [
            DropDown(
                "keepassxc",
                "keepassxc",
                x=0.3,
                y=0.2,
                width=0.4,
                height=0.6,
                on_focus_lost_hide=True,
            )
        ],
    ),
    Group("a", label="", layout="max", matches=[Match(wm_class=["Google-chrome"]),]),
    Group("s", label="", layout="max", matches=[Match(wm_class=["kitty-nvim"]),]),
    Group("d"),
    Group("f"),
    Group("u"),
    Group("i"),
    Group("o", label="", matches=[Match(wm_class=["Evolution"])]),
    Group("p", label="", matches=[Match(wm_class=["Microsoft Teams - Preview"])]),
]

for i in groups:
    if i.name == "scratchpad":
        keys.extend(
            [Key([mod], "x", lazy.group["scratchpad"].dropdown_toggle("keepassxc")),]
        )
    else:
        keys.extend(
            [
                # mod1 + letter of group = switch to group
                Key(
                    [mod],
                    i.name,
                    lazy.group[i.name].toscreen(),
                    desc="Switch to group {}".format(i.name),
                ),
                # mod1 + shift + letter of group = switch to & move focused window to
                # group
                Key(
                    [mod, "shift"],
                    i.name,
                    lazy.window.togroup(i.name, switch_group=True),
                    desc="Switch to & move focused window to group {}".format(i.name),
                ),
                # Or, use below if you prefer not to switch to that group.
                # # mod1 + shift + letter of group = move focused window to group
                # Key([mod, "shift"], i.name, lazy.window.togroup(i.name),
                #     desc="move focused window to group {}".format(i.name)),
            ]
        )

lColors = {
    "border_focus": "cc241d",
    "border_normal": "3c3836",
    "border_width": 3,
    "margin": 5,
}

layouts = [
    layout.MonadTall(**lColors),
    layout.Max(**lColors),
    layout.MonadWide(),
    # Try more layouts by unleashing below layouts.
    # layout.Bsp(),
    # layout.Columns(),
    # layout.Matrix(),
    # layout.RatioTile(),
    # layout.Stack(**lColors, num_stacks=2),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]

widget_defaults = dict(font="Ubuntu Regular", fontsize=14, padding=3, foreground="ebdbb2",)
extension_defaults = widget_defaults.copy()

slave_screen = Screen(
    top=bar.Bar(
        [
            widget.Spacer(length=10),
            widget.CurrentLayoutIcon(scale=0.6),
            widget.GroupBox(
                active="ebdbb2",
                inactive="665c54",
                this_current_screen_border="ebdbb2",
                highlight_method="line",
                highlight_color=["3c3836", "3c3836"],
                center_aligned=True,
            ),
            widget.WindowName(width=600, for_current_screen=True),
            widget.Spacer(length=bar.STRETCH),
            widget.Clock(format="<b>%H:%M %d.%m.%Y</b>"),
            widget.Spacer(length=bar.STRETCH),
        ],
        30,
        background="282828",
        opacity=0.95,
        margin=[3, 0, 3, 0],
    ),
)

master_screen = Screen(
    top=bar.Bar(
        [
            widget.Spacer(length=10),
            widget.CurrentLayoutIcon(scale=0.6),
            widget.GroupBox(
                active="ebdbb2",
                inactive="665c54",
                this_current_screen_border="ebdbb2",
                highlight_method="line",
                highlight_color=["3c3836", "3c3836"],
                center_aligned=True,
            ),
            widget.WindowName(width=600, for_current_screen=True),
            widget.Spacer(length=bar.STRETCH),
            widget.Clock(format="<b>%H:%M %d.%m.%Y</b>"),
            widget.Spacer(length=bar.STRETCH),
            widget.Systray(),
            widget.Spacer(length=10),
            widget.BatteryIcon(theme_path=os.path.expanduser("~/.config/qtile/battery-icons"),),
            widget.Battery(format="{percent:2.0%}", **widget_defaults),
            widget.Spacer(length=10),
        ],
        30,
        background="282828",
        opacity=0.95,
        margin=[3, 0, 3, 0],
    ),
)


def get_num_monitors():
    num_monitors = 0
    try:
        display = xdisplay.Display()
        screen = display.screen()
        resources = screen.root.xrandr_get_screen_resources()

        for output in resources.outputs:
            monitor = display.xrandr_get_output_info(output, resources.config_timestamp)
            preferred = False
            if hasattr(monitor, "preferred"):
                preferred = monitor.preferred
            elif hasattr(monitor, "num_preferred"):
                preferred = monitor.num_preferred
            if preferred:
                num_monitors += 1
    except Exception as e:
        # always setup at least one monitor
        return 1
    else:
        return num_monitors


count = get_num_monitors()

subprocess.call([os.path.expanduser("~/.config/qtile/screenlayouts/" + str(count) + "screens.sh")])
screens = list(map(lambda i: master_screen if i == 0 else slave_screen, range(count)))

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: List
main = None
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        {"wmclass": "confirm"},
        {"wmclass": "dialog"},
        {"wmclass": "download"},
        {"wmclass": "error"},
        {"wmclass": "file_progress"},
        {"wmclass": "notification"},
        {"wmclass": "splash"},
        {"wmclass": "toolbar"},
        {"wmclass": "confirmreset"},  # gitk
        {"wmclass": "makebranch"},  # gitk
        {"wmclass": "maketag"},  # gitk
        {"wname": "branchdialog"},  # gitk
        {"wname": "pinentry"},  # GPG key password entry
        {"wmclass": "ssh-askpass"},  # ssh-askpass
        {"wmclass": "gnome-screenshot"},
        {"wmclass": "Evolution-alarm-notify"},
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"


@hook.subscribe.client_new
def floating_dialogs(window):
    dialog = (
        window.window.get_wm_type() == "dialog" or window.window.get_wm_type() == "notification"
    )
    transient = window.window.get_wm_transient_for()
    if dialog or transient:
        window.floating = True


# XXX: Gasp! We"re lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn"t work correctly. We may as well just lie
# and say that we"re a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java"s whitelist.
wmname = "LG3D"


@hook.subscribe.startup_once
def autostart():
    home = os.path.expanduser("~/.config/qtile/autostart.sh")
    subprocess.call([home])


def detect_screens(qtile):
    def setup_monitors(action=None, device=None):
        if action == "change":
            qtile.cmd_restart()

    setup_monitors()

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by("drm")
    monitor.enable_receiving()

    # observe if the monitors change and reset monitors config
    observer = pyudev.MonitorObserver(monitor, setup_monitors)
    observer.start()


def main(qtile):
    detect_screens(qtile)
