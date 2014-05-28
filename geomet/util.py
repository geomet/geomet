import itertools
import six


def block_splitter(data, block_size):
    """
    Creates a generator by slicing ``data`` into chunks of ``block_size``.

    >>> data = range(10)
    >>> list(block_splitter(data, 2))
    [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]

    If ``data`` cannot be evenly divided by ``block_size``, the last block will
    simply be the remainder of the data. Example:

    >>> data = range(10)
    >>> list(block_splitter(data, 3))
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]

    If the ``block_size`` is greater than the total length of ``data``, a
    single block will be generated:

    >>> data = range(3)
    >>> list(block_splitter(data, 4))
    [[0, 1, 2]]

    :param data:
        Any iterable. If ``data`` is a generator, it will be exhausted,
        obviously.
    :param int block_site:
        Desired (maximum) block size.
    """
    buf = []
    for i, datum in enumerate(data):
        buf.append(datum)
        if len(buf) == block_size:
            yield buf
            buf = []

    # If there's anything leftover (a partial block),
    # yield it as well.
    if buf:
        yield buf


def take(n, iterable):
    """
    Return first n items of the iterable as a list

    Copied shamelessly from
    http://docs.python.org/2/library/itertools.html#recipes.
    """
    return list(itertools.islice(iterable, n))


def as_bin_str(a_list):
    if six.PY2:
        return b''.join(a_list)
    else:
        return bytes(a_list)
