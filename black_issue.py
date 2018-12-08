other_argument = None


def my_func():
    my_result = (
        yield (
            True,
            a_very_long_function_call_to_make_line_break(
                lambda first, second, third, fourth, fifth: 10, other_argument
            ),
        )
    )


def a_very_long_function_call_to_make_line_break(*args):
    return 10


d = my_func()
a, b = next(d)
print(b, a)
