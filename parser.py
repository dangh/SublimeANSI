from collections import namedtuple
import inspect
import re
import unittest
from generator_helpers import fold


def call(f, *args):
    sig = inspect.signature(f)
    is_positional = False
    for p, param in sig.parameters.items():
        if param.kind is inspect.Parameter.VAR_POSITIONAL:
            is_positional = True
            break
    if not is_positional:
        args = args[0 : len(sig.parameters)]
    return f(*args)


def get_scope(flags):
    return '{0}_{1}_{2}'.format(
        flags['foreground'] if 'foreground' in flags else '',
        flags['background'] if 'background' in flags else '',
        'd' if 'dim' in flags else '',
    )


class PlainDict(object):
    def __init__(_, d=None):
        super(PlainDict, _).__init__()
        _.d = d or {}

    def __getattr__(_, k):
        if k in _.d:
            v = _.d[k]
            if type(v) is dict:
                return PlainDict(v)
            return v

    def __setattr__(_, k, v):
        _.d[k] = v


SEQUENCES = {
    # {code, {
    #     flag: value
    # }}
    '0': {
        'bold': False,
        'dim': False,
        'italic': False,
        'underline': False,
        'inverse': False,
        'hidden': False,
        'strikethrough': False,
        'foreground': None,
        'background': None,
    },
    # modifiers
    '1': {'bold': True},
    '2': {'dim': True},
    '3': {'italic': True},
    '4': {'underline': True},
    '7': {'inverse': True},
    '8': {'hidden': True},
    '9': {'strikethrough': True},
    '21': {'bold': False},
    '22': {'bold': False, 'dim': False},
    '23': {'italic': False},
    '24': {'underline': False},
    '27': {'inverse': False},
    '28': {'hidden': False},
    '29': {'strikethrough': False},
    # foreground
    '39': {'foreground': None},
    '30': {'foreground': 'black'},
    '31': {'foreground': 'red'},
    '32': {'foreground': 'green'},
    '33': {'foreground': 'yellow'},
    '34': {'foreground': 'blue'},
    '35': {'foreground': 'magenta'},
    '36': {'foreground': 'cyan'},
    '37': {'foreground': 'white'},
    '90': {'foreground': 'black_light'},
    '91': {'foreground': 'red_light'},
    '92': {'foreground': 'green_light'},
    '93': {'foreground': 'yellow_light'},
    '94': {'foreground': 'blue_light'},
    '95': {'foreground': 'magenta_light'},
    '96': {'foreground': 'cyan_light'},
    '97': {'foreground': 'white_light'},
    # background
    '49': {'background': None},
    '40': {'background': 'black'},
    '41': {'background': 'red'},
    '42': {'background': 'green'},
    '43': {'background': 'yellow'},
    '44': {'background': 'blue'},
    '45': {'background': 'magenta'},
    '46': {'background': 'cyan'},
    '47': {'background': 'white'},
    '100': {'background': 'black_light'},
    '101': {'background': 'red_light'},
    '102': {'background': 'green_light'},
    '103': {'background': 'yellow_light'},
    '104': {'background': 'blue_light'},
    '105': {'background': 'magenta_light'},
    '106': {'background': 'cyan_light'},
    '107': {'background': 'white_light'},
}


class AnsiFlag(object):
    def __init__(_):
        super(AnsiFlag, _).__init__()
        _.flags = {}

    def set(_, values):
        for k, v in values.items():
            if not v:
                _.flags.pop(k, None)
            else:
                _.flags[k] = v

    def __getattr__(_, key):
        return _.flags[key] if key in _.flags else None


Good = namedtuple('Good', 'data len')
Fail = namedtuple('Fail', 'expected actual')
RemoveRegion = namedtuple('RemoveRegion', 'a b')
AddRegion = namedtuple('AddRegion', 'scope a b')


def parse(parser, input):
    r = parser(input)
    if type(r) is Fail:
        raise SyntaxError(
            '''
  Expected {0}
  Actual {1}
'''.format(
                r.expected, r.actual
            )
        )
    return r


##
# PRIMITIVE PARSERS
##


def text(match):
    """
    Match the input against the provided text.
    """

    def text_parser(input):
        if input.startswith(match):
            return Good(match, len(match))
        return Fail("'{0}'".format(match), input)

    return text_parser


def regex(pattern):
    """
    Match the input against the provided pattern.
    """

    def regex_parser(input):
        m = re.match(pattern, input)
        if m:
            return Good(m.group(), m.end())
        return Fail(pattern, input)

    return regex_parser


def pure(data):
    """
    Create a parser that always success with `data` without consuming any input
    """

    def pure_parser(input):
        return Good(data, 0)

    return pure_parser


##
# Higher-order parsers
##


def one_of(*parsers):
    """
    Parse the input using one of the provided parsers.
    """

    def one_of_parser(input):
        for parser in parsers:
            r = parser(input)
            if type(r) is Good:
                return r
        return Fail('one_of', input)

    return one_of_parser


def many(parser):
    def many_parser(input):
        data = []
        while True:
            r = parser(input)
            if type(r) is Fail:
                return Good([r.data for r in data], sum(r.len for r in data))
            input = input[r.len :]
            data.append(r)

    return many_parser


def map(f, parser):
    """
    Higher-order parser that will parse and map the data.
    """

    def map_parser(input):
        r = parser(input)
        if type(r) is Fail:
            return r
        mapped = f(r.data, r.len)
        if type(mapped) is Fail:
            return mapped
        return Good(mapped, r.len)

    return map_parser


def collect(gen, f):
    """
    Like filter, but iterative
    """

    def collect_parser(input):
        pass


def serial(parsers):
    def serial_parser(input):
        sum_r = []
        for parser in parsers:
            r = parser(input)
            if type(r) is Fail:
                return r
            sum_r.append(r)
            input = input[r.len :]

        sum_data = [r.data for r in sum_r]
        sum_len = sum(r.len for r in sum_r)
        return Good(sum_data, sum_len)

    return serial_parser


def lexeme(junk):
    def create_token_parser(parser):
        return map(lambda data, len: data[1], serial([junk, parser, junk]))

    return create_token_parser


def combinator(gen):
    """
    Convert a generator into a parser.
    """

    def combinator_parser(input):
        g = gen()
        done, parser = next(g)
        sum_len = 0
        while not done:
            r = parser(input)
            if type(r) is Fail:
                return r
            done, parser = g.send(r.data)
            input = input[r.len :]
            sum_len += r.len
        r = parser(input)
        if type(r) is Fail:
            return r
        return Good(r.data, sum_len + r.len)

    return combinator_parser


def manyiter(parser):
    def manyiter_parser(input):
        while True:
            r = parser(input)
            if type(r) is Fail:
                yield True, None
            yield False, r

    return manyiter_parser


def collect1(gen):
    def collect_parser(input):
        g = gen()
        sum_r = []
        while True:
            done, r = next(g)
            if type(r) is Fail:
                return r
            if done:
                return Good([r.data for r in sum_r], sum(r.len for r in sum_r))
            sum_r.append(r)

    return collect_parser


def label(parser, expected):
    def label_parser(input):
        r = parser(input)
        if type(r) is Fail:
            return Fail(expected, r.actual)
        return r

    return label_parser


def unexpected(actual):
    """
    Create a parser that always failed with customized `actual` value
    """

    def unexpected_parser(input):
        return Fail('unexpected', actual)

    return unexpected_parser


##
# PARSER COMBINATORS
##


# higher-order parser that will skim all leading and trailing semicolons
token = lexeme(regex(r';*'))


escape_on = text('\x1b[')
escape_off = text('m')
decimal = regex('\d+')
eof = label(regex(r'$'), 'EOF')


@combinator
def ansi_code_4bit():
    code = yield False, decimal
    if int(code) > 255:
        yield True, label(unexpected(code), '[0..255]')
    if code not in SEQUENCES:
        yield True, label(unexpected(code), 'ANSI-16 code')
    yield True, pure(code)


@combinator
def ansi_sequence():
    yield False, escape_on
    codes = yield False, many(token(ansi_code_4bit))
    yield False, escape_off
    yield True, pure(codes)


ansi_text = regex(r'[^\x1b]+')


@combinator
def ansi():
    data = yield False, many(one_of(ansi_sequence, ansi_text))
    yield False, eof
    yield True, pure(data)


@combinator
def ansi_regions():
    flags = {}
    start = 0

    def update_flags(codes, l):
        nonlocal flags
        nonlocal start
        for code in codes:
            if code in SEQUENCES:
                for flag, value in SEQUENCES[code].items():
                    if not value:
                        flags.pop(flag, None)
                    else:
                        flags[flag] = value
        region = RemoveRegion(start, start + l)
        start += l
        return region

    def yield_region(text, l):
        nonlocal start
        region = AddRegion(get_scope(flags), start, start + l)
        start += l
        return region

    yield True, many(
        one_of(map(update_flags, ansi_sequence), map(yield_region, ansi_text))
    )


ansi_text_region = map(
    lambda text, state: AddRegion(
        get_scope(state['flags']),
        state['continue_at'],
        state['continue_at'] + len(text),
    ),
    ansi_text,
)

ansi_sequence_region = map(
    lambda seq, state: RemoveRegion(
        state['continue_at'], state['continue_at'] + len(seq)
    ),
    ansi_sequence,
)


class TestParser(unittest.TestCase):
    def assertFailExpect(_, expected, fn, *args, **kwargs):
        try:
            fn(*args, **kwargs)
        except Exception as e:
            _.assertIn('Expected {}'.format(expected), str(e))
        else:
            _.fail('Exception not raised')

    def test_primitive(_):
        _.assertEqual(parse(escape_on, '\x1b[123'), Good(data='\x1b[', len=2))
        _.assertEqual(parse(escape_off, 'm123'), Good(data='m', len=1))
        _.assertEqual(parse(decimal, '123m'), Good(data='123', len=3))

    def test_token(_):
        _.assertEqual(parse(token(text('8')), ';;;8;'), Good(data='8', len=5))
        _.assertEqual(parse(token(text('8')), '8'), Good(data='8', len=1))

    def test_many(_):
        _.assertEqual(parse(many(text('m')), 'mmm'), Good(data=['m', 'm', 'm'], len=3))
        _.assertEqual(parse(many(text('m')), ''), Good(data=[], len=0))

    def test_serial(_):
        _.assertEqual(
            parse(serial([text('m'), text('o'), text('m')]), 'mom'),
            Good(data=['m', 'o', 'm'], len=3),
        )

    # def test_manyiter(_):
    #     _.assertEqual(parse(collect(manyiter(text('m'))), 'mmm'), 'm')

    def test_ansi_code_4bit(_):
        _.assertEqual(parse(ansi_code_4bit, '39'), Good(data='39', len=2))
        _.assertFailExpect('[0..255]', parse, ansi_code_4bit, '256')
        _.assertFailExpect('ANSI-16 code', parse, ansi_code_4bit, '13')

    def test_ansi_sequence(_):
        _.assertEqual(parse(ansi_sequence, '\x1b[;39;m'), Good(data=['39'], len=7))
        _.assertFailExpect("'\x1b['", parse, ansi_sequence, '123')
        _.assertFailExpect("'\x1b['", parse, ansi_sequence, '\x1b')

    def test_ansi(_):
        _.assertEqual(
            parse(ansi, '\x1b[;31;mhello\x1b[0mworld'),
            Good(data=[['31'], 'hello', ['0'], 'world'], len=21),
        )
        _.assertFailExpect('EOF', parse, ansi, '\x1b[;31;mhello\x1b[0mworld\x1b')

    def test_ansi_regions(_):
        _.maxDiff = None
        _.assertEqual(
            parse(
                ansi_regions,
                'ciao\x1b[2m\x1b[30m\x1b[42mhello\x1b[49m\x1b[39m\x1b[22mbaby',
            ).data,
            [
                AddRegion('__', 0, 4),
                RemoveRegion(4, 8),
                RemoveRegion(8, 13),
                RemoveRegion(13, 18),
                AddRegion('black_green_d', 18, 23),
                RemoveRegion(23, 28),
                RemoveRegion(28, 33),
                RemoveRegion(33, 38),
                AddRegion('__', 38, 42),
            ],
        )

    def test_filter(_):
        _.assertEqual(parse())

    def test_ansi_region_merge(_):
        def merge_remove_regions(current, r):
            if type(r) is not RemoveRegion:
                yield True, r
            elif current.b == r.a:
                yield False, RemoveRegion(current.a, r.b)

        _.assertEqual(
            parse(
                collect(fold(merge_remove_regions, ansi_regions)),
                'ciao\x1b[2m\x1b[30m\x1b[42mhello\x1b[49m\x1b[39m\x1b[22mbaby',
            ),
            [
                AddRegion('__', 0, 4),
                RemoveRegion(4, 18),
                AddRegion('black_green_d', 18, 23),
                RemoveRegion(23, 38),
                AddRegion('__', 38, 42),
            ],
        )


if __name__ == '__main__':
    unittest.main()
