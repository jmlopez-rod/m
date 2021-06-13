from typing import TypeVar, Generic, Union

B = TypeVar('B')
G = TypeVar('G')


class StopBadIteration(Exception):
    """Store a `Bad` instance."""
    def __init__(self, bad):
        Exception.__init__(self)
        self.bad = bad


class OneOf(Generic[B, G]):
    """An instance of `OneOf` is an instance of either `Bad` or `Good`."""

    def __init__(self, bad: bool, val: Union[B, G]):
        self.is_bad = bad
        self.value = val

    def __iter__(self):
        if self.is_bad:
            raise StopBadIteration(self)
        yield self.value

    def iter(self):
        if not self.is_bad:
            yield self.value

    def map(self, fct):
        """The given function is applied if this is a `Good` value"""
        return self if self.is_bad else Good(fct(self.value))

    def map_bad(self, fct):
        """The given function is applied if this is a `Bad` value"""
        return Bad(fct(self.value)) if self.is_bad else self


class Bad(OneOf[B, G]):
    """The bad side of the disjoint union"""
    def __init__(self, val):
        OneOf.__init__(self, True, val)


class Good(OneOf[B, G]):
    """The good side of the disjoint union"""
    def __init__(self, val):
        OneOf.__init__(self, False, val)


def one_of(comp):
    """`comp` should be a lambda function which returns an array with a single
    value. To be used so that we may iterate over OneOf objects that may raise
    the StopBadIteration exception.
    """
    try:
        return Good(comp()[0])
    except StopBadIteration as ex:
        return ex.bad
    except BaseException as ex:
        return Bad(ex)
