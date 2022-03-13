import sys
import argparse
import collections
from itertools import islice
from typing import *


import hpat.sylfr as sylfr
from hpat.xsampa import XSAMPA


ipa = XSAMPA.to_ipa  # alias
xsampa = XSAMPA.from_ipa  # alias


def iter_stdin() -> Iterator[str]:
    for line in sys.stdin:
        yield line.rstrip()


def consume(iterator, n=None):
    """
    Advance the iterator n-steps ahead. If n is None, consume entirely.

    Reference
    ---------
    https://docs.python.org/3.9/library/itertools.html
    """
    # Use functions that consume iterators at C speed.
    if n is None:
        # feed the entire iterator into a zero-length deque
        collections.deque(iterator, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(islice(iterator, n, n), None)


def callback(*, source_format, target_format):
    stream: Iterator[str] = iter_stdin()

    if source_format == "xsampa":
        stream = map(ipa, stream)
    elif source_format == "ipa":
        pass
    else:
        raise NotImplementedError(f"{source_format=}")

    stream: Iterator[sylfr.Syllabification] = map(sylfr.syllabify, stream)
    stream: Iterator[str] = map(str, stream)

    if target_format == "ipa":
        pass
    elif target_format == "xsampa":
        stream = map(xsampa, stream)
    else:
        raise NotImplementedError(f"{target_format=}")

    stream = map(print, stream)
    consume(stream)


def ArgumentParser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--from",
        dest="source_format",
        choices=("xsampa", "ipa"),
        default="ipa",
    )
    parser.add_argument(
        "--to",
        dest="target_format",
        choices=("xsampa", "ipa"),
        default="ipa",
    )
    parser.set_defaults(__callback__=callback)
    return parser


def main():
    parser = ArgumentParser()
    args = parser.parse_args()
    kwargs = vars(args)
    callback = kwargs.pop("__callback__", None)
    if callback is None:
        parser.print_help()
    else:
        callback(**kwargs)


if __name__ == '__main__':
    main()
