#!/usr/bin/env python3
# benefits: palettable colors, automated module order

# old school ubuntu: go(palettable.colorbrewer.sequential.OrRd_3.colors, ['#000'], palettable.wesanderson.GrandBudapest1_4.colors)
# goes well with bluish i3: go(['#fff'] + palettable.cmocean.sequential.Tempo_4.colors[1:], ['#000'], palettable.colorbrewer.sequential.OrRd_9.colors[3:])
# ugly example: go(palettable.colorbrewer.sequential.YlGnBu_4.colors, ['#000'], palettable.wesanderson.GrandBudapest1_4.colors)

# TODO bar
# TODO cmd line interface

# TODO handle indirection? color=${section.colorvar}
# TODO warn if variable is reused, create new var
# TODO create your own variables in the [colors] section

import math
import os
import re

import configobj
import palettable
import colour

CONFIGPATH = '~/.config/polybar/config'


# Use ; as comments
class ConfigObjPolybar(configobj.ConfigObj):
    COMMENT_MARKERS = [';']


white = colour.Color('white')


def set_colors(config, variables, colors, section="colors"):
    if isinstance(colors, palettable.palette.Palette):
        colors = colors.colors
    if type(variables) is str:
        variables = variables.split()
    for i, v in enumerate(variables):
        if ',#' in v:
            v, alpha = v.split(',#') 
        else:
            alpha = None
        c = tohex(colors[math.floor(i / len(variables) * len(colors))])
        if alpha:
            if len(c) == 4:
                alpha = alpha[0]
            c = c.replace('#', '#' + alpha)
        config[section][v] = c

# i3/bspwm
# should be colors.background...

# consider self.xxxx
# re.match('\${(?P<section>.*?)\.(?P<var>.*?)}', s)


"""
TODO:
format-disconnected-underline
format-discharging-underline
format-warn-underline # temperature
"""

# for area in ['modules-center', 'modules-right']:

def tocolor(col):
    if type(col) is not str and hasattr(col, '__getitem__'):
        if type(col[0]) is int:
            col = [c / 255 for c in col]
        return colour.Color(rgb=col)
    else:
        return colour.Color(col)


def tohex(col):
    if type(col) is str and col.startswith('#') and len(col) - 1 in [3, 6, 8]:
        return col
    h = tocolor(col).get_hex()
    if len(h) == 4:
        h = '#' + ''.join(c + c for c in h[1:]) 
    return h


def lighten(col):
    hsl = list(col.get_hsl())
    hsl[2] = (1 + hsl[2]) / 2
    return colour.Color(hsl=hsl)


def module_underline_colors(config, module_area, bar='bar/primary', colors=palettable.colorbrewer.sequential.YlOrRd_9.colors, change_background=False, change_foreground=False, reset_fg=False):
    if isinstance(colors, palettable.palette.Palette):
        colors = colors.colors

    def palette(i):
        return tohex(colors[math.floor(i % len(colors))])

    if not (bar in config and module_area in config[bar]):
        return

    modules = config[bar][module_area].split()
    valid_keys = ['format-underline', 'format-mounted-underline', 'format-volume-underline',
                  'format-discharging-underline', 'format-charging-underline', 'format-connected-underline']
    paired_text = {'format-mounted-underline': 'label-mounted'}
    # recommend: use self.xxx instead
    # paired_color = {'format-background'}
    for i, m in enumerate(modules):
        section = config['module/' + m]
        for k in section.keys():
            if k in valid_keys:
                color = palette(i)
                lighter = lighten(lighten(lighten(tocolor(color))))
                darker = list(tocolor(color).get_hsl())
                darker[2] = min(darker[2] / 2, 0.35) # 1 - darker[2]
                # darker[2] = max(darker[2] - 0.1, 0)
                # darker[0] = 1 - darker[0]
                darker = colour.Color(hsl=darker)
                section[k] = color
                if k in paired_text and paired_text[k] in section:
                    section[paired_text[k]] = re.sub('%{F#.{6,6}}', '%{F' + color + '}', section[paired_text[k]])
                bg = k.replace('underline', 'background')
                fg = k.replace('underline', 'foreground')
                if reset_fg:
                    if bg in section:
                        del section[bg]
                    if fg in section:
                        del section[fg]
                if change_background:
                    print(m, k, bg, section[bg])
                    section[bg] = tohex(darker).replace('#', '#c9')
                if change_foreground:
                    section[fg] = tohex(lighter)


def load_config(fname):
    # Ignore inline comments that start with #
    config = ConfigObjPolybar(fname, encoding='UTF8', _inspec=True)
    # Do not write empty quotes "" for empty values
    config.write_empty_values = True
    return config

def save_config(config, fname):
    with open(fname, 'wb') as f:
        config.write(f)

def go(colors_back, colors_fore, colors_under, colors_under_right=None, reset_fg=False):
    config_path = os.path.expanduser(CONFIGPATH)
    config = load_config(config_path)
    module_underline_colors(config, module_area='modules-center',
        change_background=True, change_foreground=True, reset_fg=reset_fg, colors=colors_under)
    module_underline_colors(config, module_area='modules-right',
        change_background=True, change_foreground=True, reset_fg=reset_fg,
        colors=colors_under_right or colors_under) # [-1::-1])
    set_colors(config, 'background,#00 background-alt,#cc primary secondary background-alt-sub,#99', colors=colors_back)
    set_colors(config, 'foreground foreground-alt', colors=colors_fore)
    save_config(config, config_path)

if __name__ == '__main__':
    pass
