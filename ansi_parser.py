from helpers import TextParser, TextRegion, find_all


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


class AnsiParser(TextParser):
    def __init__(self, reduce=None):
        super(AnsiParser, self).__init__()
        self.reduce = reduce

    def parse(content):
        sum_text_length = 0  # length of all ansi text
        sum_seq_length = 0  # length of all escaped sequences
        flags = {}
        for (a, b), (codes,) in find_all(r'\x1b\[([0-9;]*)m', content):
            text_length = a - (sum_text_length + sum_seq_length)
            seq_length = b - a
            if text_length:
                scope = get_scope(flags)
                if scope not in regions:
                    regions[scope] = TextRegion(scope)
                regions[scope].add(sum_text_length, sum_text_length + text_length)

            sum_text_length += text_length
            sum_seq_length += seq_length

            if self.reduce:
                codes = self.reduce(codes)

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
                regions[scope] = TextRegion(scope)
            regions[scope].add(sum_text_length, sum_text_length + text_length)

        # we don't need to paint the default regions
        regions.pop('cF_cB_', None)

        for scope in regions:
            yield regions[scope]
