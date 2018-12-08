import re
import unittest
import test as tc
import helpers as h

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


def reduce_to_ansi(seq, supported_rgb):
    r256 = r'\b(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\b'  # 0..255

    regex_ansi_8bit = h.get_regex_obj(
        r'\b((?P<fg>38)|48);5;(?P<color>{0})'.format(r256)
    )
    seq = regex_ansi_8bit.sub(
        lambda m: get_ansi_8bit_escape_sequence(
            find_closest_color(
                ansi_8bit_to_rgb(int(m.groupdict()['color'])), supported_rgb
            ),
            m.groupdict()['fg'],
        ),
        seq,
    )

    regex_ansi_16bit = h.get_regex_obj(
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


def get_scope(flags):
    return 'c{0}_c{1}_{2}'.format(
        h.get_color_index(flags['foreground']) if 'foreground' in flags else 'F',
        h.get_color_index(flags['background']) if 'background' in flags else 'B',
        'd' if 'dim' in flags else '',
    )


def parse_ansi(content=None, reducer=None):
    '''
    @brief Parse ANSI text and grab all ANSI text regions

    @content string

    @return AnsiRegion[]
    '''

    '''
    what do we need?
    - capture 24-bit, 8-bit ansi_regions and yield out 4-bit scope region
    - capture all ansi_region with correct scope and location
    - capture all highlight region after remove all ansi_codes, otherwise we will miss some text

    requirement:
    - the order of parser should not matter
    '''

    parser = merge(AnsiParser(), HighlightParser())
    for result in parser(content):
        if type(result) is TextRegion:
            collector.add(result)
        elif type(result) is RemoveRegion:
            collector.cut_area(result)

    parsers = [Ansi8bitParser(), Ansi24bitParser(), Ansi4bitParser(), HighlightParser()]
    for parser in parsers:
        for result in parser.process(content):
            if type(result) is success:
                collector.add(result.scope, result.a, result.p)
            elif type(result) is clean_up:
                collector.cut_area(result.a, result.b)
            elif type(result) is fix_up:
                collector.
            if result.fix_up:
                collector.cut_area(result.cut_area)
            else:
                scope, ansi_region = result
                collector.add(scope, ansi_region[0], ansi_region[1])
            content = result.content_left



    parser = AnsiParser()
    for scope, (a, b) in parser.parse(content):
        collector.add(scope, a, b)

    content = parser.clean()

    parser =

    if content is None:
        # returns list of all the possible scopes
        for fg in ['F'] + list(range(1, 17)):
            for bg in ['B'] + list(range(1, 17)):
                for dim in ('', 'd'):
                    scope = 'c{0}_c{1}_{2}'.format(fg, bg, dim)
                    if scope is not 'cF_cB_':
                        yield AnsiRegion(scope)
        return

    # collect ansi regions
    regions = {
        # scope: AnsiRegion[],
    }

    sum_text_length = 0  # length of all ansi text
    sum_seq_length = 0  # length of all escaped sequences
    flags = {}
    for (a, b), (codes,) in h.find_all(r'\x1b\[([0-9;]*)m', content):
        text_length = a - (sum_text_length + sum_seq_length)
        seq_length = b - a
        if text_length:
            scope = get_scope(flags)
            if scope not in regions:
                regions[scope] = AnsiRegion(scope)
            regions[scope].add(sum_text_length, sum_text_length + text_length)

        sum_text_length += text_length
        sum_seq_length += seq_length

        if reducer:
            codes = reducer(codes)

        codes = map(int, filter(None, codes.split(';')))
        for code in codes:
            for flag, variants in SEQUENCES.items():
                for value, (code_on, code_off) in variants.items():
                    if code == code_on:
                        flags[flag] = value
                    elif code in code_off:
                        flags.pop(flag, None)

    # add the ending ansi text
    text_length = len(content) - (sum_text_length + sum_seq_length)
    if text_length:
        scope = get_scope(flags)
        if scope not in regions:
            regions[scope] = AnsiRegion(scope)
        regions[scope].add(sum_text_length, sum_text_length + text_length)

    # we don't need to paint the default regions
    regions.pop('cF_cB_', None)

    for scope in regions:
        yield regions[scope]


def parse_text(content=None, parsers=[]):
    collector = AnsiCollector()

    for parse in parsers:
        content, regions = parse(content)
        collector.collect(regions)

    return sum_regions


class TestParser(unittest.TestCase):
    def test_parse_ansi(self):
        content, expected = tc.get_ansi_test()
        self.maxDiff = None
        self.assertEqual(list(parse_ansi(content)), expected)
        # self.assertEqual(AnsiRegion(''), {'scope': '', 'regions': []})
        # self.assertEqual(AnsiRegion(''), AnsiRegion(''))

    def test_parse_ansi_none(self):
        content, expected = tc.get_ansi_test_none()
        self.maxDiff = None
        # self.assertEqual(list(parse_ansi(content)), expected)


if __name__ == '__main__':
    unittest.main()


parser = ansi_parser()
last_position = 0
for result in parser(content, last_position):
    if type(result) is Add:
        collection.add(result)
        last_position = result[1]
    elif type(result) is Remove:
        collection.cut_area(result)
        content = content[0:result[0]] + content[result[1]:]


def ansi_parser(content):
    last_position = 0
    seq = re.match(r'')
