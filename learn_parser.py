import re
import inspect
from collections import namedtuple


Failure = namedtuple('Failure', 'expected actual')
Success = namedtuple('Success', 'data rest')


def parse(parser, input):
    result = parser(input)
    if type(result) is Failure:
        raise SyntaxError(
            '''
  Expected {0}
  Actual {1}
'''.format(
                result.expected, result.actual
            )
        )
    return result


def text(match):
    def _text_parser(input):
        if input.startswith(match):
            return Success(match, input[len(match) :])
        return Failure("'{0}'".format(match), input)

    return _text_parser


def regex(pattern):
    def _regex_parser(input):
        m = re.match(pattern, input)
        if m:
            return Success(m.group(), input[m.end() :])
        return Failure(pattern, input)

    return _regex_parser


def _map(f, parser):
    def _map_parser(input):
        result = parser(input)
        if type(result) is Failure:
            return result
        return Success(f(result.data), result.rest)

    return _map_parser


def apply(f, parsers):
    def _apply_parser(input):
        data = []
        for parser in parsers:
            result = parser(input)
            if type(result) is Failure:
                return result
            data.append(result.data)
            input = result.rest
        sig = inspect.getargspec(f)
        if sig.varargs:
            return Success(f(*data), input)

        args = data[0 : len(sig.args)]
        return Success(f(*args), input)

    return _apply_parser


def one_of(*parsers):
    def _one_of_parser(input):
        for parser in parsers:
            result = parser(input)
            if type(result) is Success:
                return result
        return Failure('one_of', input)

    return _one_of_parser


def eof(input):
    return Failure('EOF', input) if input else Success(None, input)


def label(parser, expected):
    def _label_parser(input):
        result = parser(input)
        if type(result) is Failure:
            return Failure(expected, input)
        return result

    return _label_parser


def lexeme(junk):
    def _create_token_parser(parser):
        return apply(lambda x: x, [parser, junk])

    return _create_token_parser


spaces = regex(r'\s*')
token = lexeme(spaces)


op_map = {
    '+': lambda a, b: a + b,
    '-': lambda a, b: a - b,
    '*': lambda a, b: a * b,
    '/': lambda a, b: a / b,
}
op = label(
    _map(op_map.get, one_of(text('+'), text('-'), text('*'), text('/'))),
    'an arithmetic operator',
)
_decimal = _map(lambda x: float(x), label(regex(r'\d+(?:\.\d+)?'), 'a decimal'))
expr = apply(
    lambda _, a, opFunc, b: opFunc(a, b),
    [
        spaces,  # skip leading spaces
        token(_decimal),
        token(op),
        token(_decimal),
        spaces,  # skip trailing spaces
        eof,
    ],
)


def go(gen):
    def _go_parser(input):
        g = gen()
        done, parser = next(g)
        while not done:
            result = parser(input)
            if type(result) is Failure:
                return result

            done, parser = g.send(result.data)
            input = result.rest

            if done:
                return parser(input)

    return _go_parser


def pure(value):
    def _pure_parser(input):
        return Success(value, input)

    return _pure_parser


def many(parser):
    this = None

    @go
    def recur_parser():
        head = yield False, parser
        tail = yield False, this
        yield True, pure([head] + tail)

    this = one_of(recur_parser, pure([]))

    return this


def collect(*parsers):
    return apply(lambda *x: x, parsers)


def _reduce(f, initial=None, *parsers):
    def _reduce_parser(input):
        parser = parsers[0]
        _parsers = parsers[1:]
        r = parser(input)
        if type(r) is Failure:
            return r
        print(r.data)
        print(f(initial, r.data))
        value = f(initial, r.data)
        for parser in _parsers:
            r = parser(r.rest)
            if type(r) is Failure:
                return r
            value = f(value, r.data)
        return Success(value, r.rest)

    return _reduce_parser


@go
def expr():
    a = yield False, token(_decimal)
    values = (
        yield False,
        _reduce(
            lambda acc, (opFunc, v): opFunc(acc, v),
            a,
            many(collect(token(op), token(_decimal))),
        ),
    )
    yield True, pure(values)


# print(many(regex(r'\d'))('123'))
# print(collect(regex(r'\d'), text('a'))('1a'))
# print((lambda *x: x)(1, 2, 3))
# print(inspect.getargspec(lambda a, c: 10))
print(parse(expr, '12 * 34'))
print(parse(expr, '12 - 32'))
print(parse(expr, '1 + 2 + 3 + 4'))
# print(parse(expr, '12a+34'))
# print(parse(expr, '12a34'))
# print(parse(expr, '12+34rest'))
# print(parse(_decimal, "a12*34"))
