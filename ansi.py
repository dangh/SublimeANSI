# -*- coding: utf-8 -*-

from collections import namedtuple
from functools import partial
import Default
import inspect
import json
import os
import re
import sublime
import sublime_plugin

print(os.environ)

DEBUG = True

AnsiDefinition = namedtuple("AnsiDefinition", "scope regex")
regex_obj_cache = {}

REGEX_RANGE_0_F = r'[0-9a-fA-F]'
REGEX_RANGE_0_255 = r'\b([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\b'  # 0..255
REGEX_RANGE_0_1_FLOAT = r'((\.\d+)|(0(\.\d+))|(1(\.0+)?))'  # 0..1
REGEX_RANGE_0_100 = r'0+|(0*[0-9])|(0*[1-9][0-9])|100'  # 0%..100%
REGEX_RANGE_0_360 = (
    r'0+|(0*[0-9])|(0*[1-9][0-9])|(0*[1-2][0-9][0-9])|(0*3[0-5][0-9])|(0*360)'
)

ANSI_NAMES = (
    'black',
    'red',
    'green',
    'yellow',
    'blue',
    'magenta',
    'cyan',
    'white',
    'black_light',
    'red_light',
    'green_light',
    'yellow_light',
    'blue_light',
    'magenta_light',
    'cyan_light',
    'white_light',
)

SEQUENCES = {
    # {flag, {
    #     value: (code_on, (code_off))
    # }}
    'bold': {'bold': (1, (0, 21, 22))},
    'dim': {'dim': (2, (0, 22))},
    'italic': {'italic': (3, (0, 23))},
    'underline': {'underline': (4, (0, 24))},
    'inverse': {'inverse': (7, (0, 27))},
    'hidden': {'hidden': (8, (0, 28))},
    'strikethrough': {'strikethrough': (9, (0, 29))},
    'foreground': {
        'black': (30, (0, 39)),
        'red': (31, (0, 39)),
        'green': (32, (0, 39)),
        'yellow': (33, (0, 39)),
        'blue': (34, (0, 39)),
        'magenta': (35, (0, 39)),
        'cyan': (36, (0, 39)),
        'white': (37, (0, 39)),
        'black_light': (90, (0, 39)),
        'red_light': (91, (0, 39)),
        'green_light': (92, (0, 39)),
        'yellow_light': (93, (0, 39)),
        'blue_light': (94, (0, 39)),
        'magenta_light': (95, (0, 39)),
        'cyan_light': (96, (0, 39)),
        'white_light': (97, (0, 39)),
    },
    'background': {
        'black': (40, (0, 49)),
        'red': (41, (0, 49)),
        'green': (42, (0, 49)),
        'yellow': (43, (0, 49)),
        'blue': (44, (0, 49)),
        'magenta': (45, (0, 49)),
        'cyan': (46, (0, 49)),
        'white': (47, (0, 49)),
        'black_light': (100, (0, 49)),
        'red_light': (101, (0, 49)),
        'green_light': (102, (0, 49)),
        'yellow_light': (103, (0, 49)),
        'blue_light': (104, (0, 49)),
        'magenta_light': (105, (0, 49)),
        'cyan_light': (106, (0, 49)),
        'white_light': (107, (0, 49)),
    },
}

CSS_COLORS = {
    'aliceblue': '#f0f8ff',
    'antiquewhite': '#faebd7',
    'aqua': '#00ffff',
    'aquamarine': '#7fffd4',
    'azure': '#f0ffff',
    'beige': '#f5f5dc',
    'bisque': '#ffe4c4',
    'black': '#000000',
    'blanchedalmond': '#ffebcd',
    'blue': '#0000ff',
    'blueviolet': '#8a2be2',
    'brown': '#a52a2a',
    'burlywood': '#deb887',
    'cadetblue': '#5f9ea0',
    'chartreuse': '#7fff00',
    'chocolate': '#d2691e',
    'coral': '#ff7f50',
    'cornflowerblue': '#6495ed',
    'cornsilk': '#fff8dc',
    'crimson': '#dc143c',
    'cyan': '#00ffff',
    'darkblue': '#00008b',
    'darkcyan': '#008b8b',
    'darkgoldenrod': '#b8860b',
    'darkgray': '#a9a9a9',
    'darkgreen': '#006400',
    'darkgrey': '#a9a9a9',
    'darkkhaki': '#bdb76b',
    'darkmagenta': '#8b008b',
    'darkolivegreen': '#556b2f',
    'darkorange': '#ff8c00',
    'darkorchid': '#9932cc',
    'darkred': '#8b0000',
    'darksalmon': '#e9967a',
    'darkseagreen': '#8fbc8f',
    'darkslateblue': '#483d8b',
    'darkslategray': '#2f4f4f',
    'darkslategrey': '#2f4f4f',
    'darkturquoise': '#00ced1',
    'darkviolet': '#9400d3',
    'deeppink': '#ff1493',
    'deepskyblue': '#00bfff',
    'dimgray': '#696969',
    'dimgrey': '#696969',
    'dodgerblue': '#1e90ff',
    'firebrick': '#b22222',
    'floralwhite': '#fffaf0',
    'forestgreen': '#228b22',
    'fuchsia': '#ff00ff',
    'gainsboro': '#dcdcdc',
    'ghostwhite': '#f8f8ff',
    'gold': '#ffd700',
    'goldenrod': '#daa520',
    'gray': '#808080',
    'green': '#008000',
    'greenyellow': '#adff2f',
    'grey': '#808080',
    'honeydew': '#f0fff0',
    'hotpink': '#ff69b4',
    'indianred': '#cd5c5c',
    'indigo': '#4b0082',
    'ivory': '#fffff0',
    'khaki': '#f0e68c',
    'lavender': '#e6e6fa',
    'lavenderblush': '#fff0f5',
    'lawngreen': '#7cfc00',
    'lemonchiffon': '#fffacd',
    'lightblue': '#add8e6',
    'lightcoral': '#f08080',
    'lightcyan': '#e0ffff',
    'lightgoldenrodyellow': '#fafad2',
    'lightgray': '#d3d3d3',
    'lightgreen': '#90ee90',
    'lightgrey': '#d3d3d3',
    'lightpink': '#ffb6c1',
    'lightsalmon': '#ffa07a',
    'lightseagreen': '#20b2aa',
    'lightskyblue': '#87cefa',
    'lightslategray': '#778899',
    'lightslategrey': '#778899',
    'lightsteelblue': '#b0c4de',
    'lightyellow': '#ffffe0',
    'lime': '#00ff00',
    'limegreen': '#32cd32',
    'linen': '#faf0e6',
    'magenta': '#ff00ff',
    'maroon': '#800000',
    'mediumaquamarine': '#66cdaa',
    'mediumblue': '#0000cd',
    'mediumorchid': '#ba55d3',
    'mediumpurple': '#9370db',
    'mediumseagreen': '#3cb371',
    'mediumslateblue': '#7b68ee',
    'mediumspringgreen': '#00fa9a',
    'mediumturquoise': '#48d1cc',
    'mediumvioletred': '#c71585',
    'midnightblue': '#191970',
    'mintcream': '#f5fffa',
    'mistyrose': '#ffe4e1',
    'moccasin': '#ffe4b5',
    'navajowhite': '#ffdead',
    'navy': '#000080',
    'oldlace': '#fdf5e6',
    'olive': '#808000',
    'olivedrab': '#6b8e23',
    'orange': '#ffa500',
    'orangered': '#ff4500',
    'orchid': '#da70d6',
    'palegoldenrod': '#eee8aa',
    'palegreen': '#98fb98',
    'paleturquoise': '#afeeee',
    'palevioletred': '#db7093',
    'papayawhip': '#ffefd5',
    'peachpuff': '#ffdab9',
    'peru': '#cd853f',
    'pink': '#ffc0cb',
    'plum': '#dda0dd',
    'powderblue': '#b0e0e6',
    'purple': '#800080',
    'rebeccapurple': '#663399',
    'red': '#ff0000',
    'rosybrown': '#bc8f8f',
    'royalblue': '#4169e1',
    'saddlebrown': '#8b4513',
    'salmon': '#fa8072',
    'sandybrown': '#f4a460',
    'seagreen': '#2e8b57',
    'seashell': '#fff5ee',
    'sienna': '#a0522d',
    'silver': '#c0c0c0',
    'skyblue': '#87ceeb',
    'slateblue': '#6a5acd',
    'slategray': '#708090',
    'slategrey': '#708090',
    'snow': '#fffafa',
    'springgreen': '#00ff7f',
    'steelblue': '#4682b4',
    'tan': '#d2b48c',
    'teal': '#008080',
    'thistle': '#d8bfd8',
    'tomato': '#ff6347',
    'turquoise': '#40e0d0',
    'violet': '#ee82ee',
    'wheat': '#f5deb3',
    'white': '#ffffff',
    'whitesmoke': '#f5f5f5',
    'yellow': '#ffff00',
    'yellowgreen': '#9acd32',
}


def debug(view, msg):
    if not DEBUG:
        return

    info = inspect.getframeinfo(inspect.stack()[1][0])
    filepath = os.path.abspath(info.filename)
    if view.name():
        name = view.name()
    elif view.file_name():
        name = os.path.basename(view.file_name())
    else:
        name = "not named"
    msg = re.sub(r'\n', "\n\t", msg)

    print(
        "File: \"{path}\", line {lineno}, window: {window_id}, view: {view_id}, file: {name}\n\t{msg}".format_map(
            {
                'lineno': info.lineno,
                'msg': msg,
                'name': name,
                'path': filepath,
                'view_id': view.id(),
                'window_id': view.window().id(),
            }
        )
    )


def get_settings(name, default):
    settings = sublime.load_settings("ansi.sublime-settings")
    result = settings.get(name, default)
    if type(default) is dict:
        result = merge_dict(default, result)
    return result


def get_regex_obj(regex_string, flags=0):
    """
    @brief Get the regular expression object.

    @param regex_string the regular expression string
    @param flags        the regular expression flags

    @return The regular expression object.
    """

    if regex_string not in regex_obj_cache:
        regex_obj_cache[regex_string] = re.compile(regex_string, flags)

    return regex_obj_cache[regex_string]


def find_all(content, regex_string, flags=0):
    if not content:
        return []
    iterator = get_regex_obj(regex_string, flags).finditer(content)
    return [(m.span(), m.groups()) for m in iterator]


def ansi_regions(content=None):
    """
    @brief Find all text regions in the provided content.
           All the regions are adjusted as after stripped out the escape sequences.

    @param content the content string

    @return { scope: sublime.Region[] }
    """

    # collect ansi regions
    regions = {
        # scope: regions,
    }

    if content is None:
        # returns dictionary with all the possible scopes
        for fg in range(17):
            for bg in range(17):
                for dim in ('', 'd'):
                    scope = 'c{0}_c{1}_{2}'.format(fg, bg, dim)
                    regions[scope] = []

    ansi_codes = find_all(content, r'\x1b\[([0-9;]*)m')

    ANSI_COLORS_RGB = {
        k: parse_color_to_rgb(v) for k, v in get_settings('ANSI_COLORS', {}).items()
    }

    text_length = 0  # length of all ansi text
    seq_length = 0  # length of all escaped sequences
    flags = {}
    for (a, b), (codes,) in ansi_codes:
        this_text_length = a - (text_length + seq_length)
        this_seq_length = b - a
        if this_text_length:
            text_region = (text_length, text_length + this_text_length)
            scope = get_scope(flags)
            if scope not in regions:
                regions[scope] = []
            regions[scope].append(text_region)

        text_length += this_text_length
        seq_length += this_seq_length

        codes = reduce_to_ansi(codes, ANSI_COLORS_RGB)
        codes = map(int, filter(None, codes.split(';')))
        for code in codes:
            for flag, variants in SEQUENCES.items():
                for value, (code_on, code_off) in variants.items():
                    if code == code_on:
                        flags[flag] = value
                    elif code in code_off:
                        flags.pop(flag, None)

    # add the ending ansi text
    last_text_length = len(content) - (text_length + seq_length)
    if last_text_length:
        text_region = (text_length, text_length + last_text_length)
        scope = get_scope(flags)
        if scope not in regions:
            regions[scope] = []
        regions[scope].append(text_region)

    return regions


def highlight_regions(content=None):
    regions = {}
    HIGHLIGHT = get_settings('HIGHLIGHT', [])

    if content is None:
        for i in range(len(HIGHLIGHT)):
            regions['h{0}'.format(i + 1)] = []
        return regions

    for i in range(len(HIGHLIGHT)):
        scope = 'h{0}'.format(i + 1)
        rule = HIGHLIGHT[i]
        regions[scope] = [r for r, _ in find_all(content, rule['regex'], re.IGNORECASE)]

    return regions


def get_color_index(name):
    return ANSI_NAMES.index(name) + 1 if name in ANSI_NAMES else 0


def get_scope(flags):
    return "c{0}_c{1}_{2}".format(
        get_color_index(flags['foreground']) if 'foreground' in flags else 'F',
        get_color_index(flags['background']) if 'background' in flags else 'B',
        'd' if 'dim' in flags else '',
    )


def reduce_to_ansi(seq, supported_rgb):
    r256 = r'\b(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\b'  # 0..255

    regex_ansi_8bit = get_regex_obj(r'\b((?P<fg>38)|48);5;(?P<color>{0})'.format(r256))
    seq = regex_ansi_8bit.sub(
        lambda m: get_ansi_8bit_escape_sequence(
            find_closest_color(
                ansi_8bit_to_rgb(int(m.groupdict()['color'])), supported_rgb
            ),
            m.groupdict()['fg'],
        ),
        seq,
    )

    regex_ansi_16bit = get_regex_obj(
        r'\b((?P<fg>38)|48);2;(?P<red>{0});(?P<green>{0});(?P<blue>{0})'.format(r256)
    )
    seq = regex_ansi_16bit.sub(
        lambda m: get_ansi_8bit_escape_sequence(
            find_closest_color(
                (
                    int(m.groupdict()['red']),
                    int(m.groupdict()['green']),
                    int(m.groupdict()['blue']),
                ),
                supported_rgb,
            ),
            m.groupdict()['fg'],
        ),
        seq,
    )

    return seq


def get_ansi_8bit_escape_sequence(color_name, is_foreground):
    return str(
        SEQUENCES['foreground' if is_foreground else 'background'][color_name][0]
    )


def ansi_8bit_to_rgb(num):
    # handle greyscale
    if num >= 232:
        c = (num - 232) * 10 + 8
        return (c, c, c)

    num -= 16
    return (int(num / 36) / 5 * 255, int((num % 36) / 6) / 5 * 255, (num % 6) / 5 * 255)


def parse_color_to_rgb(value):
    """
    @brief HEX, RGB, HSL and CSS colors to RGBA tuple.

    @param value string

    @return (red, green, blue, alpha)
    """

    hex_to_dec = lambda c: int(((c or 'F') + (c or 'F'))[:2], 16)

    REGEX_HEX_SHORT = r'^\s*#(?P<red>{0})(?P<green>{0})(?P<blue>{0})(?P<alpha>{0})?\s*$'.format(
        REGEX_RANGE_0_F
    )
    m = re.match(get_regex_obj(REGEX_HEX_SHORT, flags=re.IGNORECASE), value)
    if m:
        m = m.groupdict()
        return (
            hex_to_dec(m['red']),
            hex_to_dec(m['green']),
            hex_to_dec(m['blue']),
            hex_to_dec(m['alpha']) / 255,
        )

    REGEX_HEX_FULL = r'^\s*#(?P<red>{0}{0})(?P<green>{0}{0})(?P<blue>{0}{0})(?P<alpha>{0}{0})?\s*$'.format(
        REGEX_RANGE_0_F
    )
    m = re.match(get_regex_obj(REGEX_HEX_FULL, flags=re.IGNORECASE), value)
    if m:
        m = m.groupdict()
        return (
            hex_to_dec(m['red']),
            hex_to_dec(m['green']),
            hex_to_dec(m['blue']),
            hex_to_dec(m['alpha']) / 255,
        )

    REGEX_RGBA = r'^\s*rgba?\(\s*(?P<red>{0})\s*,\s*(?P<green>{0})\s*,\s*(?P<blue>{0})\s*(,\s*(?P<alpha>{1})\s*)?\)\s*$'.format(
        REGEX_RANGE_0_255, REGEX_RANGE_0_1_FLOAT
    )
    m = re.match(get_regex_obj(REGEX_RGBA, flags=re.IGNORECASE), value)
    if m:
        m = m.groupdict()
        return (int(m['red']), int(m['green']), int(m['blue']), float(m['alpha'] or 1))

    REGEX_HSLA = r'^\s*hsla?\s*\(\s*(?P<hue>{0})\s*,\s*(?P<saturation>0|({1}%))\s*,\s*(?P<light>0|({1}%))\s*(,\s*(?P<alpha>{2}))?\s*\)'.format(
        REGEX_RANGE_0_360, REGEX_RANGE_0_100, REGEX_RANGE_0_1_FLOAT
    )
    m = re.match(get_regex_obj(REGEX_RGBA, flags=re.IGNORECASE), value)
    if m:
        m = m.groupdict()
        rgb = hsl_to_rgb(
            (
                int(m['hue']),
                int(m['saturation'].rstrip('%')),
                int(m['light'].rstrip('%')),
            )
        )
        return rgb + (float(m['alpha'] or 1))

    value = value.strip().lower()
    if value in CSS_COLORS.keys():
        return parse_color_to_rgb(CSS_COLORS[value])


def hsl_to_rgb(hsl):
    hue = hsl[0] / 360
    saturation = hsl[1] / 100
    light = hsl[2] / 100

    if saturation == 0:
        val = light * 255
        return (val, val, val)

    if light < 0.5:
        t2 = light * (1 + saturation)
    else:
        t2 = light + saturation - light * saturation

    t1 = 2 * light - t2

    rgb = (0, 0, 0)
    for i in range(3):
        t3 = hue + 1 / 3 * -(i - 1)
        if t3 < 0:
            t3 += 1
        if t3 > 1:
            t3 -= 1

        if 6 * t3 < 1:
            val = t1 + (t2 - t1) * 6 * t3
        elif 2 * t3 < 1:
            val = t2
        elif 3 * t3 < 2:
            val = t1 + (t2 - t1) * (2 / 3 - t3) * 6
        else:
            val = t1

        rgb[i] = val * 255

    return rgb


def rgb_to_hex(rgba):
    r, g, b, a = rgba
    rgb = '#{:02x}{:02x}{:02x}'.format(r, g, b)
    if a < 1:
        rgb += '{:02x}'.format(int(a * 255))
    return rgb


def find_closest_color(rgb, supported_rgb):
    d = {k: euclidean_distance(v, rgb) for k, v in supported_rgb.items()}
    return min(d, key=d.get)


def euclidean_distance(a, b):
    """
    @brief Calculate Euclidean distance between 2 RGB colors.
    """

    dr = (a[0] - b[0]) * (a[0] - b[0])
    dg = (a[1] - b[1]) * (a[1] - b[1])
    db = (a[2] - b[2]) * (a[2] - b[2])
    return dr + dg + db


class AnsiRegion(object):
    def __init__(self, scope):
        super(AnsiRegion, self).__init__()
        self.scope = scope
        self.regions = []

    def add(self, a, b):
        self.regions.append([a, b])

    def cut_area(self, a, b):
        begin, end = min(a, b), max(a, b)
        for n, (a, b) in enumerate(self.regions):
            a = self.subtract_region(a, begin, end)
            b = self.subtract_region(b, begin, end)
            self.regions[n] = (a, b)

    def shift(self, val):
        for n, (a, b) in enumerate(self.regions):
            self.regions[n] = (a + val, b + val)

    def jsonable(self):
        return {self.scope: self.regions}

    @staticmethod
    def subtract_region(p, begin, end):
        if p < begin:
            return p
        elif p < end:
            return begin
        else:
            return p - (end - begin)


class AnsiCommand(sublime_plugin.TextCommand):
    def run(self, edit, regions=None, clear_before=False):
        view = self.view
        if view.settings().get("ansi_in_progres", False):
            debug(view, "oops ... the ansi command is already in progress")
            return
        view.settings().set("ansi_in_progres", True)

        # if the syntax has not already been changed to ansi this means the command has
        # been run via the sublime console therefore the syntax must be changed manually
        if view.settings().get("syntax") != "Packages/sublime-ansi/ANSI.sublime-syntax":
            view.settings().set("syntax", "Packages/sublime-ansi/ANSI.sublime-syntax")

        view.settings().set("ansi_enabled", True)
        view.settings().set(
            "color_scheme", "Packages/User/sublime-ansi/ansi.sublime-color-scheme"
        )
        view.settings().set("draw_white_space", "none")

        # save the view's original scratch and read only settings
        if not view.settings().has("ansi_scratch"):
            view.settings().set("ansi_scratch", view.is_scratch())
        view.set_scratch(True)
        if not view.settings().has("ansi_read_only"):
            view.settings().set("ansi_read_only", view.is_read_only())
        view.set_read_only(False)

        if clear_before:
            self._remove_ansi_regions()
            self._remove_highlight_regions()

        if regions is None:
            self._colorize_ansi_codes(edit)
            self._colorize_highlight_regions(edit)
        else:
            self._colorize_regions(regions)

        view.settings().set("ansi_in_progres", False)
        view.settings().set("ansi_size", view.size())
        view.set_read_only(True)

    def _colorize_regions(self, regions):
        view = self.view
        debug(view, '_colorize_regions: {}\n---------\n'.format(regions))
        for scope, regions_points in regions.items():
            regions = [sublime.Region(a, b) for a, b in regions_points]
            sum_regions = view.get_regions(scope) + regions
            view.add_regions(
                scope,
                sum_regions,
                scope,
                '',
                sublime.DRAW_NO_OUTLINE | sublime.PERSISTENT,
            )

    def _colorize_ansi_codes(self, edit):
        view = self.view

        # collect ansi regions
        content = view.substr(sublime.Region(0, view.size()))
        regions = ansi_regions(content)
        debug(view, "regions: {}\n----------\n".format(regions))

        # removing ansi escaped codes
        for (a, b), _ in reversed(find_all(content, r'\x1b\[([0-9;]*)m')):
            view.erase(edit, sublime.Region(a, b))

        # render corrected ansi regions
        self._colorize_regions(regions)

    def _remove_ansi_regions(self):
        view = self.view
        for scope in ansi_regions():
            view.erase_regions(scope)

    def _colorize_highlight_regions(self, edit):
        view = self.view
        content = view.substr(sublime.Region(0, view.size()))
        self._colorize_regions(highlight_regions(content))

    def _remove_highlight_regions(self):
        view = self.view
        for scope in highlight_regions():
            view.erase_regions(scope)


class UndoAnsiCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        # if ansi is in progress or don't have ansi_in_progress setting
        # don't run the command
        if view.settings().get("ansi_in_progres", True):
            debug(view, "oops ... the ansi command is already executing")
            return
        view.settings().set("ansi_in_progres", True)

        # if the syntax has not already been changed from ansi this means the command has
        # been run via the sublime console therefore the syntax must be changed manually
        if view.settings().get("syntax") == "Packages/sublime-ansi/ANSI.sublime-syntax":
            view.settings().set("syntax", "Packages/Text/Plain text.tmLanguage")

        view.settings().erase("ansi_enabled")
        view.settings().erase("color_scheme")
        view.settings().erase("draw_white_space")

        view.set_read_only(False)
        view.run_command("undo")
        for scope in ansi_regions():
            view.erase_regions(scope)

        # restore the view's original scratch and read only settings
        view.set_scratch(view.settings().get("ansi_scratch", False))
        view.settings().erase("ansi_scratch")
        view.set_read_only(view.settings().get("ansi_read_only", False))
        view.settings().erase("ansi_read_only")
        view.settings().erase("ansi_in_progres")
        view.settings().erase("ansi_size")


class AnsiEventListener(sublime_plugin.EventListener):
    def on_new_async(self, view):
        self.process_view_open(view)

    def on_load_async(self, view):
        self.process_view_open(view)

    def on_pre_close(self, view):
        self.process_view_close(view)

    def process_view_open(self, view):
        self._del_event_listeners(view)
        self._add_event_listeners(view)
        if view.settings().get("syntax") == "Packages/sublime-ansi/ANSI.sublime-syntax":
            view.run_command("ansi")

    def process_view_close(self, view):
        self._del_event_listeners(view)
        # if view.settings().get("syntax") == "Packages/sublime-ansi/ANSI.sublime-syntax":
        #    view.window().run_command("undo_ansi") ** this needs to be tested **

    def detect_left_ansi(self, view):
        sublime.set_timeout_async(partial(self.check_left_ansi, view), 50)

    def check_left_ansi(self, view):
        if not self._is_view_valid(view):
            self._del_event_listeners(view)
            return
        if view.settings().get("syntax") != "Packages/sublime-ansi/ANSI.sublime-syntax":
            return
        if view.settings().get("ansi_in_progres", False):
            debug(view, "ansi in progres")
            sublime.set_timeout_async(partial(self.check_left_ansi, view), 50)
            return
        if view.settings().get("ansi_size", view.size()) != view.size():
            debug(view, "ANSI view size changed. Running ansi command")
            view.run_command("ansi", args={"clear_before": True})
        debug(view, "ANSI cmd done and no codes left")

    def detect_syntax_change(self, view):
        if not self._is_view_valid(view):
            self._del_event_listeners(view)
            return
        if view.settings().get("ansi_in_progres", False):
            return
        if view.settings().get("syntax") == "Packages/sublime-ansi/ANSI.sublime-syntax":
            if not view.settings().has("ansi_enabled"):
                debug(view, "Syntax change detected (running ansi command).")
                view.run_command("ansi", args={"clear_before": True})
        else:
            if view.settings().has("ansi_enabled"):
                debug(view, "Syntax change detected (running undo command).")
                view.window().run_command("undo_ansi")

    def _is_view_valid(self, view):
        if view.window() is None:
            return False
        if view.window() not in sublime.windows():
            return False
        if view not in view.window().views():
            return False
        return True

    def _add_event_listeners(self, view):
        view.settings().add_on_change(
            "CHECK_FOR_ANSI_SYNTAX", lambda: self.detect_syntax_change(view)
        )
        view.settings().add_on_change(
            "CHECK_FOR_LEFT_ANSI", lambda: self.detect_left_ansi(view)
        )
        debug(view, "sublime-ansi event listeners assigned to view.")

    def _del_event_listeners(self, view):
        view.settings().clear_on_change("CHECK_FOR_ANSI_SYNTAX")
        view.settings().clear_on_change("CHECK_FOR_LEFT_ANSI")
        debug(view, "sublime-ansi event listener removed from view.")


class AnsiColorBuildCommand(Default.exec.ExecCommand):

    process_trigger = "on_finish"

    @classmethod
    def update_build_settings(self, settings):
        val = settings.get("ANSI_process_trigger", "on_finish")
        if val in ["on_finish", "on_data"]:
            self.process_trigger = val
        else:
            self.process_trigger = None
            sublime.error_message(
                "sublime-ansi settings warning:\n\nThe setting ANSI_process_trigger has been set to an invalid value; must be one of 'on_finish' or 'on_data'."
            )

    @classmethod
    def clear_build_settings(self, settings):
        self.process_trigger = None

    def on_data_process(self, proc, data):
        view = self.output_view
        if (
            not view.settings().get("syntax")
            == "Packages/sublime-ansi/ANSI.sublime-syntax"
        ):
            super(AnsiColorBuildCommand, self).on_data(proc, data)
            return

        str_data = data

        # find all regions
        regions = ansi_regions(str_data)

        # adjust regions location because there was data
        adjust_val = view.size()
        adjusted_regions = {}
        print('DIZZ', str_data)
        print('BEFORE', regions)
        for scope, regions in regions.items():
            adjusted_regions[scope] = [
                (a + adjust_val, b + adjust_val) for a, b in regions
            ]
        print('AFTER', adjusted_regions)

        # remove codes
        ansi_codes = find_all(str_data, r'(\x1b\[[0-9;]*m)+')
        for (a, b), _ in reversed(ansi_codes):
            print('cut', a, b)
            print('before', str_data)
            str_data = str_data[0:a] + str_data[b:]
            print('after', str_data)

        highlights = highlight_regions(str_data)
        print('highlights', highlights)
        adjusted_highlights = {}
        for scope, regions in highlights.items():
            adjusted_highlights[scope] = [
                (a + adjust_val, b + adjust_val) for a, b in regions
            ]

        # send on_data without ansi codes
        super(AnsiColorBuildCommand, self).on_data(proc, str_data)

        # send ansi command
        view.run_command('ansi', args={"regions": adjusted_regions})
        # view.run_command('ansi', args={"regions": adjusted_highlights})

    def on_data(self, proc, data):
        if self.process_trigger == "on_data":
            self.on_data_process(proc, data)
        else:
            super(AnsiColorBuildCommand, self).on_data(proc, data)

    def on_finished(self, proc):
        super(AnsiColorBuildCommand, self).on_finished(proc)
        if self.process_trigger == "on_finish":
            view = self.output_view
            if (
                view.settings().get("syntax")
                == "Packages/sublime-ansi/ANSI.sublime-syntax"
            ):
                view.run_command("ansi", args={"clear_before": True})


def adjust_to_diff(color, base):
    """
    If we draw the region with the same background as the theme background,
    sublime will use foreground color as background, which is undesirable.

    This function will adjust the color so it will slightly different to the background,
    but still close enough so the human eye cannot distinguise.
    """

    color = parse_color_to_rgb(color)
    base = parse_color_to_rgb(base)
    if color != base:
        return rgb_to_hex(color)

    return rgb_to_hex((color[0], color[1], color[2] - 1 if color[2] else 1, color[3]))


def merge_dict(*argv):
    r = {}
    for d in argv:
        for k, v in d.items():
            if k not in r or v:
                r[k] = v
    return r


def generate_color_scheme(cs_file, settings):
    print("Regenerating ANSI color scheme...")

    ANSI_COLORS = get_settings('ANSI_COLORS', {})
    ANSI_dim_alpha = get_settings('ANSI_dim_alpha', 0.7)
    HIGHLIGHT = settings.get('HIGHLIGHT', [])
    GENERAL = get_settings(
        'GENERAL',
        {
            'foreground': ANSI_COLORS['white'] or '#fff',
            'background': ANSI_COLORS['black'] or '#000',
        },
    )

    view_fg = GENERAL['foreground']
    view_bg = GENERAL['background']

    # FIX: reverted color when painting black background
    ANSI_COLORS['black'] = adjust_to_diff(ANSI_COLORS['black'], view_bg)

    dim = lambda color, alpha=ANSI_dim_alpha: 'color({0} alpha({1}))'.format(
        color, alpha
    )

    scheme = {
        'name': 'ANSI',
        'variables': {
            'cF': view_fg,
            'cFd': dim(view_fg),
            # FIX: reverted color when painting transparent background
            'cB': adjust_to_diff(view_bg, view_bg),
        },
        'globals': merge_dict(
            {
                'gutter': view_bg,
                'gutter_foreground': dim(view_fg, 0.5),
                'caret': dim(view_fg, 0.7),
                'selection': dim(ANSI_COLORS['white_light'], 0.2),
                'line_highlight': dim(ANSI_COLORS['white_light'], 0.25),
                'selection_corner_style': 'square',
                'selection_border_width': '0',
                'guide': view_bg,
                'active_guide': view_bg,
                'stack_guide': view_bg,
            },
            GENERAL,
        ),
        'rules': [],
    }
    for i in range(16):
        scheme['variables']['c{0}'.format(i + 1)] = ANSI_COLORS[ANSI_NAMES[i]]
        scheme['variables']['c{0}d'.format(i + 1)] = dim(ANSI_COLORS[ANSI_NAMES[i]])
    for fg in ('F',) + tuple(range(1, 17)):
        for bg in ('B',) + tuple(range(1, 17)):
            for dim in ['', 'd']:
                scheme['rules'].append(
                    {
                        'scope': 'c{0}_c{1}_{2}'.format(fg, bg, dim),
                        'foreground': 'var(c{0}{1})'.format(fg, dim),
                        'background': 'var(c{0})'.format(bg),
                    }
                )
    h = 0
    for rule in HIGHLIGHT:
        h += 1
        scheme['rules'].append(
            {
                'scope': 'h{0}'.format(h),
                'foreground': rule['foreground'] if 'foreground' in rule else 'var(cF)',
                'background': rule['background'] if 'background' in rule else 'var(cB)',
            }
        )
    with open(cs_file, 'w') as color_scheme:
        json.dump(scheme, color_scheme, separators=(',', ':'))


def plugin_loaded():
    # load pluggin settings
    settings = sublime.load_settings("ansi.sublime-settings")
    # create ansi color scheme directory
    ansi_cs_dir = os.path.join(sublime.packages_path(), "User", "sublime-ansi")
    if not os.path.exists(ansi_cs_dir):
        os.makedirs(ansi_cs_dir)
    # create ansi color scheme file
    cs_file = os.path.join(ansi_cs_dir, "ansi.sublime-color-scheme")
    if not os.path.isfile(cs_file):
        generate_color_scheme(cs_file, settings)
    # update the settings for the plugin
    AnsiColorBuildCommand.update_build_settings(settings)
    settings.add_on_change(
        "ANSI_COLORS_CHANGE", lambda: generate_color_scheme(cs_file, settings)
    )
    settings.add_on_change(
        "ANSI_TRIGGER_CHANGE",
        lambda: AnsiColorBuildCommand.update_build_settings(settings),
    )
    # update the setting for each view
    # for window in sublime.windows():
    #     for view in window.views():
    #         AnsiEventListener().process_view_open(view)


def plugin_unloaded():
    # update the settings for the plugin
    settings = sublime.load_settings("ansi.sublime-settings")
    AnsiColorBuildCommand.clear_build_settings(settings)
    settings.clear_on_change("ANSI_COLORS_CHANGE")
    settings.clear_on_change("ANSI_TRIGGER_CHANGE")
    # update the setting for each view
    # for window in sublime.windows():
    #     for view in window.views():
    #         AnsiEventListener().process_view_close(view)
