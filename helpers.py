import re


REGEX_RANGE_0_F = r'[0-9a-fA-F]'
REGEX_RANGE_0_255 = r'\b([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\b'  # 0..255
REGEX_RANGE_0_1_FLOAT = r'((\.\d+)|(0(\.\d+))|(1(\.0+)?))'  # 0..1
REGEX_RANGE_0_100 = r'0+|(0*[0-9])|(0*[1-9][0-9])|100'  # 0%..100%
REGEX_RANGE_0_360 = (
    r'0+|(0*[0-9])|(0*[1-9][0-9])|(0*[1-2][0-9][0-9])|(0*3[0-5][0-9])|(0*360)'
)

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

regex_obj_cache = {}


def get_regex_obj(regex_string, flags=0):
    if regex_string not in regex_obj_cache:
        regex_obj_cache[regex_string] = re.compile(regex_string, flags)

    return regex_obj_cache[regex_string]


def find_all(regex_string, content, flags=0):
    return [
        (m.span(), m.groups())
        for m in get_regex_obj(regex_string, flags).finditer(content)
    ]


class Color(object):
    def __init__(self, value):
        super(Color, self).__init__()
        self.red = self.green = self.blue = 0
        self.alpha = 1

        color = self.parse(value)
        if color:
            self.red, self.green, self.blue, self.alpha = color

    def to_hex(self):
        rgb = '#{:02x}{:02x}{:02x}'.format(self.red, self.green, self.blue)
        if self.alpha < 1:
            rgb += '{:02x}'.format(int(self.alpha * 255))
        return rgb

    @staticmethod
    def parse(value):
        color = Color.parse_hex_short(value)
        if color:
            return color

        color = Color.parse_hex_full(value)
        if color:
            return color

        color = Color.parse_rgb(value)
        if color:
            return color

        color = Color.parse_hsl(value)
        if color:
            return color

        color = Color.parse_css_name(value)
        if color:
            return color

    @staticmethod
    def parse_hex_short(value):
        REGEX_HEX_SHORT = r'^#{0}{1}{2}{3}$'.format(
            r'(?P<red>{0})'.format(REGEX_RANGE_0_F),
            r'(?P<green>{0})'.format(REGEX_RANGE_0_F),
            r'(?P<blue>{0})'.format(REGEX_RANGE_0_F),
            r'(?P<alpha>{0})?'.format(REGEX_RANGE_0_F),
        )
        m = re.match(get_regex_obj(REGEX_HEX_SHORT, flags=re.IGNORECASE), value)
        if m:
            m = m.groupdict()
            return (
                int((m['red'] + m['red'])[:2], 16),
                int((m['green'] + m['green'])[:2], 16),
                int((m['blue'] + m['blue'])[:2], 16),
                int(((m['alpha'] or 'F') + (m['alpha'] or 'F'))[:2], 16) / 255,
            )

    @staticmethod
    def parse_hex_full(value):
        REGEX_HEX_FULL = r'^#{0}{1}{2}{3}'.format(
            r'(?P<red>{0}{0})'.format(REGEX_RANGE_0_F),
            r'(?P<green>{0}{0})'.format(REGEX_RANGE_0_F),
            r'(?P<blue>{0}{0})'.format(REGEX_RANGE_0_F),
            r'(?P<alpha>{0}{0})?'.format(REGEX_RANGE_0_F),
        )
        m = re.match(get_regex_obj(REGEX_HEX_FULL, flags=re.IGNORECASE), value)
        if m:
            m = m.groupdict()
            return (
                int(m['red'], 16),
                int(m['green'], 16),
                int(m['blue'], 16),
                int(m['alpha'] or 'FF', 16) / 255,
            )

    @staticmethod
    def parse_rgb(value):
        REGEX_RGB = r'^rgba?\({0},{1},{2}(?:,{3})?\)$'.format(
            r'\s*(?P<red>{0})\s*'.format(REGEX_RANGE_0_255),
            r'\s*(?P<green>{0})\s*'.format(REGEX_RANGE_0_255),
            r'\s*(?P<blue>{0})\s*'.format(REGEX_RANGE_0_255),
            r'\s*(?P<alpha>{0})\s*'.format(REGEX_RANGE_0_1_FLOAT),
        )
        m = re.match(get_regex_obj(REGEX_RGBA, flags=re.IGNORECASE), value)
        if m:
            m = m.groupdict()
            return (
                int(m['red']),
                int(m['green']),
                int(m['blue']),
                float(m['alpha'] or 1),
            )

    @staticmethod
    def parse_hsl(value):
        REGEX_HSLA = r'^hsla?\({0},{1},{2}(?:,{3})?\)$'.format(
            r'\s*(?P<hue>{0})\s*'.format(REGEX_RANGE_0_360),
            r'\s*(?P<saturation>{0})%?\s*'.format(REGEX_RANGE_0_100),
            r'\s*(?P<light>{0})%?\s*'.format(REGEX_RANGE_0_100),
            r'\s*(?P<alpha>{0})\s*'.format(REGEX_RANGE_0_1_FLOAT),
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

    @staticmethod
    def parse_css_name(value):
        value = value.strip().lower()
        if value in CSS_COLORS.keys():
            return Color.parse(CSS_COLORS[value])


def get_color_index(name):
    return ANSI_NAMES.index(name) + 1 if name in ANSI_NAMES else 0


class TextRegion(object):
    def __init__(self, scope):
        super(TextRegion, self).__init__()
        self.scope = scope
        self.regions = []

    def add(self, a, b):
        self.regions.append((a, b))

    def shift(self, distance):
        self.regions = [(a + distance, b + distance) for a, b in self.regions]

    def cut_area(self, a, b):
        begin, end = min(a, b), max(a, b)
        self.regions = [
            (self.subtract_region(a, begin, end), self.subtract_region(b, begin, end))
            for a, b in self.regions
            if a < begin or end < b
        ]

    @staticmethod
    def subtract_region(p, begin, end):
        """Findout the location of p after cut out (begin, end)"""
        # p < begin < end
        # delete (begin, end) has no effect
        if p < begin:
            return p

        # begin < p < end
        # after delete (begin, end), this point will fall to begin
        if p < end:
            return begin

        # begin < end < p
        # after delete (begin, end), the leftover will shift left
        return p - (end - begin)


class TextRegionCollection(object):
    def __init__(self):
        super(TextRegionCollection, self).__init__()
        self.regions = {}
        self.correction_table = {}

    def add(self, scope, a, b):
        if scope not in self.regions:
            self.regions[scope] = TextRegion(scope)
            self.correction_table[scope] = []
        self.regions[scope].add(a, b)

    def shift(self, distance):
        for scope, regions in self.regions.items():
            regions.shift(distance)

    def cut_area(self, a, b):
        for scope, ansi_regions in self.regions.items():
            ansi_regions.cut_area(a, b)


class TextParser:
    def parse(content):
        return content, []
