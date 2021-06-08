from itertools import islice


def chunk(it, size):
    it = iter(it)
    return iter(lambda: list(islice(it, size)), [])
