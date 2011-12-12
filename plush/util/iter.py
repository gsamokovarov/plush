import itertools
import functools

__all__ = "first_of second_of third_of forth_of last_of nth".split()


def nth(iterable, n, default=None):
    '''
    Returns the `nth` element.
    '''

    return next(itertools.islice(iterable, n, None), default)

last_of = functools.partial(nth, n=-1)
first_of = functools.partial(nth, n=0)
second_of = functools.partial(nth, n=1)
third_of = functools.partial(nth, n=2)
forth_of = functools.partial(nth, n=3)

