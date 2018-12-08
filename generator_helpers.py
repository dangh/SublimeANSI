import unittest


def my_generator(l):
    for i in l:
        yield i


def filter(f, gen):
    def filter_generator(*args):
        g = gen(*args)
        while True:
            try:
                val = next(g)
                if f(val):
                    yield val
            except StopIteration:
                break

    return filter_generator


def fold(f, gen):
    '''
    Fold contiguous items in a stream into one item.
    '''
    def fold_generator(*args):
        g = gen(*args)
        try:
            first = next(g)
        except StopIteration:
            return

        while True:
            try:
                second = next(g)
                first, second = f(first, second)
                if second is not None:
                    yield first
                    first = second
            except StopIteration:
                break

        yield first

    return fold_generator


def merge(f, gens):
    '''
    Merge multiple "streams" into one.
    '''
    def merge_generator():
        list_iter = [g() for g in gens]
        list_val = [next(g) for g in list_iter]
        while list_val:
            # yield the rest of the remaining iterator
            if len(list_val) is 1:
                while True:
                    try:
                        yield list_val[0]
                        list_val[0] = next(list_iter[0])
                    except StopIteration:
                        return

            # find the desire value
            val = f(*list_val)
            yield val

            # remove this value and get next value in the corresponding iterator
            for i, v in enumerate(list_val):
                if v is val:
                    try:
                        list_val[i] = next(list_iter[i])
                        break
                    except StopIteration:
                        # remove value and iterator from the lists if this iterator is ended
                        list_iter = list_iter[0:i] + list_iter[i + 1 :]
                        list_val = list_val[0:i] + list_val[i + 1 :]

    return merge_generator


class TestUtil(unittest.TestCase):
    def test_filter_odd(_):
        odd = filter(lambda x: x % 2, my_generator)
        _.assertEqual(list(odd([1, 2, 3, 4, 5])), [1, 3, 5])

    def test_fold_contiguous_uniq(_):
        contiguous_uniq = fold(lambda a, b: (a, b) if a != b else (a, None), my_generator)
        _.assertEqual(list(contiguous_uniq([1, 2, 2, 2, 3, 4, 4, 5, 5, 5, 6])), [1, 2, 3, 4, 5, 6])

    def test_fold_sum(_):
        sum = fold(lambda a, b: (a + b, None), my_generator)
        _.assertEqual(list(sum([1, 2, 3, 4, 5])), [15])

    def test_merge_sort(_):
        def nums(l):
            def gen():
                for n in l:
                    yield n

            return gen

        merge_sort = merge(min, [nums([1, 3, 6, 8, 9]), nums([0, 1, 2, 4, 5, 7, 10])])
        _.assertEqual(list(merge_sort()), [0, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])


if __name__ == '__main__':
    unittest.main()
