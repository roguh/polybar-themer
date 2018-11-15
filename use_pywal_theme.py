#!/usr/bin/env python3
import json
import os
import polybar_themer

def get_colors():
    colors = None
    try:
        with open(os.path.expanduser('~/.cache/wal/colors.json')) as f:
            colors = json.load(f)
    except Exception as e:
        print('pywal colors not found')
        print(e)

    return colors

def main():
    colors = get_colors()
    back = [colors['special']['background']] + \
        [colors['colors']['color' + str(i)] for i in range(11, 14)]
    under = [colors['colors']['color' + str(i)] for i in range(2, 7)]
    # under_right = [colors['colors']['color' + str(i)] for i in range(9, 14)]
    polybar_themer.go(['#00ffffff'] + back, ['white'], under) # , under_right)

if __name__ == '__main__':
    main()
